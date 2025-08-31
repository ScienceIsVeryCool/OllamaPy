"""
Enhanced OllamaPy with 4 Query Types, Response Parser, Context Compression, and Templated Prompting
Integrating the best features from todollama's AI system
"""

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Generator

from .ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================ 
# DATA CLASSES FOR QUERY RESULTS
# ============================================================================ 

@dataclass
class MultipleChoiceResult:
    """Result from a multiple choice query with lettered answers"""
    letter: str  # A, B, C, etc.
    index: int   # 0, 1, 2, etc.
    value: str   # The actual option text
    confidence: float
    raw: str
    context_compressed: bool = False
    compression_rounds: int = 0


@dataclass
class SingleWordResult:
    """Result from a single continuous string query (no whitespace allowed)"""
    word: str  # The extracted continuous string without any whitespace
    confidence: float
    raw: str
    context_compressed: bool = False
    compression_rounds: int = 0


@dataclass
class OpenResult:
    """Result from an open essay-style response query"""
    content: str
    raw: str
    context_compressed: bool = False
    compression_rounds: int = 0


@dataclass
class FileWriteResult:
    """Result from a file write query"""
    content: str
    raw: str
    context_compressed: bool = False
    compression_rounds: int = 0

# ============================================================================ 
# RESPONSE PARSER
# ============================================================================ 

class ResponseParser:
    """Parse and extract information from AI responses"""
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Tuple[Optional[str], str]]:
        """Extract code blocks from text. Returns list of (language, code) tuples."""
        blocks = []
        
        # Pattern for fenced code blocks with optional language
        pattern = r'```(?:(\w+))?\n(.*?)\n```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1)
            code = match.group(2)
            blocks.append((language, code))
        
        return blocks
    
    @staticmethod
    def parse_multiple_choice(response: str, options: List[str]) -> Tuple[str, int, float]:
        """Parse multiple choice response to extract letter, index, and confidence"""
        # Look for single letter A-Z
        letter_match = re.search(r'\b([A-Z])\b', response.upper().strip())
        
        if letter_match:
            letter = letter_match.group(1)
            index = ord(letter) - ord('A')
            if 0 <= index < len(options):
                confidence = 0.9  # High confidence for clear letter match
                return letter, index, confidence
        
        # Fallback: try to match option text
        response_clean = response.lower().strip()
        for i, option in enumerate(options):
            if option.lower() in response_clean:
                letter = chr(ord('A') + i)
                confidence = 0.7  # Medium confidence for text match
                return letter, i, confidence
        
        # Default to first option with low confidence
        logger.warning(f"Could not parse multiple choice response: {response}")
        return 'A', 0, 0.3
    
    @staticmethod
    def parse_single_word(response: str) -> Tuple[str, float]:
        """Parse single continuous string response (no whitespace allowed)"""
        cleaned = response.strip()
        
        # Extract the first continuous alphanumeric string
        match = re.search(r'^([a-zA-Z0-9_-]+)', cleaned)
        
        if match:
            word = match.group(1)
            confidence = 0.9 if word == cleaned else 0.7
            return word, confidence
        
        # Fallback: try to extract any alphanumeric sequence
        fallback_match = re.search(r'([a-zA-Z0-9]+)', cleaned)
        if fallback_match:
            word = fallback_match.group(1)
            return word, 0.5
        
        return "unknown", 0.3
    
    @staticmethod
    def clean_file_content(response: str) -> str:
        """Clean response for file content"""
        content = response.strip()
        
        # Remove markdown code block markers if present
        if content.startswith('```'):
            lines = content.split('\n')
            lines = lines[1:]  # Remove first line
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line
            content = '\n'.join(lines)
        
        return content.strip()


# ============================================================================ 
# CONTEXT COMPRESSOR
# ============================================================================ 

class ContextCompressor:
    """Compress large contexts to fit within model limits"""
    
    def __init__(self, client: OllamaClient, model: str):
        self.client = client
        self.model = model
        self.max_context = client.get_model_context_size(model)
        self.usable_context = int(self.max_context * 0.7)  # Reserve 30% for prompt/response
    
    def needs_compression(self, text: str) -> bool:
        """Check if text needs compression"""
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = len(text) / 4
        return estimated_tokens > self.usable_context
    
    def compress(self, text: str, query: str, max_rounds: int = 3) -> Tuple[str, int]:
        """Compress text focusing on query relevance"""
        if not self.needs_compression(text):
            return text, 0
        
        rounds = 0
        current_text = text
        
        while self.needs_compression(current_text) and rounds < max_rounds:
            rounds += 1
            logger.info(f"Compression round {rounds} - Size: {len(current_text)} chars")
            
            # Split into chunks
            chunks = self._split_into_chunks(current_text)
            compressed_chunks = []
            
            for i, chunk in enumerate(chunks):
                prompt = f"""Compress the following text, keeping ONLY information relevant to this query:
                
                "{query}"
                
                Remove all irrelevant details, examples, and redundancy.
                Keep technical details, names, and specific information related to the query.

                Text to compress:
                {chunk}

                Compressed version (be aggressive in removing irrelevant content):"""
                
                compressed = self.client.generate(self.model, prompt)
                compressed_chunks.append(compressed)
                logger.debug(f"Chunk {i+1}/{len(chunks)} compressed")
            
            current_text = "\n\n".join(compressed_chunks)
            
            # Check compression ratio
            ratio = len(current_text) / len(text)
            logger.info(f"Compression ratio: {ratio:.2%}")
            
            if ratio > 0.9:  # Less than 10% reduction
                logger.warning("Compression ineffective, stopping")
                break
        
        return current_text, rounds
    
    def _split_into_chunks(self, text: str, chunk_size: int = 2000) -> List[str]:
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        current_chunk: List[str] = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


# ============================================================================ 
# AI QUERY INTERFACE WITH 4 QUERY TYPES
# ============================================================================ 

class AIQuery:
    """Enhanced AI query interface with 4 distinct query types and templated prompts"""
    
    # Query Templates
    TEMPLATES = {
        "multiple_choice": """Based on the context provided, answer the following question by selecting the best option.

Context: {context}

Question: {question}

Options:
{options}

Instructions:
- Choose the BEST answer from the options above
- Respond with ONLY the letter (A, B, C, etc.) of your chosen answer
- Do not include explanations or additional text
- Be decisive and select exactly one option

Your answer:""",

        "single_word": """Based on the context provided, answer the following question with a single continuous string.

Context: {context}

Question: {question}

CRITICAL OUTPUT REQUIREMENTS:
- Output EXACTLY ONE continuous string with NO spaces, NO tabs, NO newlines
- Do NOT add quotes, apostrophes, backticks, or ANY punctuation marks
- The output will be read LITERALLY character-by-character as raw text
- If your answer would normally be "hello world", output: helloworld
- NO whitespace characters allowed ANYWHERE in your response

Your answer:""",

        "open": """Write a comprehensive response to the following prompt.

Context: {context}

Prompt: {prompt}

Instructions:
- Provide a detailed, well-structured response
- Use clear reasoning and examples where appropriate
- Write in a professional, informative tone
- Structure your response logically with proper flow

Your response:""",

        "file_write": """Generate the complete content for a file based on the requirements below.

Context: {context}

Requirements: {requirements}

Instructions:
- Generate ONLY the file content, no explanations
- Include all necessary components as specified
- Use proper formatting and syntax
- Do not include markdown code blocks or backticks
- Start immediately with the actual file content

File content:"""
    }
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.parser = ResponseParser()
        self.compressor = ContextCompressor(client, model)
    
    def multiple_choice(
        self,
        question: str,
        options: List[str],
        context: str = "",
        auto_compress: bool = True,
        show_context: bool = True
    ) -> MultipleChoiceResult:
        """Ask AI to choose from multiple options with lettered answers"""
        
        # Handle context compression if needed
        compressed_context = context
        compression_rounds = 0
        
        if auto_compress and context:
            compressed_context, compression_rounds = self.compressor.compress(
                context, question
            )
        
        # Format options with letters
        formatted_options = "\n".join([
            f"{chr(ord('A') + i)}. {option}"
            for i, option in enumerate(options)
        ])
        
        # Build prompt from template
        prompt = self.TEMPLATES["multiple_choice"].format(
            context=compressed_context if compressed_context else "No additional context provided",
            question=question,
            options=formatted_options
        )
        
        # Get response with context monitoring
        response = self.client.generate(self.model, prompt, show_context=show_context)
        
        # Parse response
        letter, index, confidence = self.parser.parse_multiple_choice(response, options)
        
        return MultipleChoiceResult(
            letter=letter,
            index=index,
            value=options[index] if 0 <= index < len(options) else options[0],
            confidence=confidence,
            raw=response,
            context_compressed=compression_rounds > 0,
            compression_rounds=compression_rounds
        )
    
    def single_word(
        self,
        question: str,
        context: str = "",
        auto_compress: bool = True,
        show_context: bool = True
    ) -> SingleWordResult:
        """Ask AI for a single word response"""
        
        # Handle context compression if needed
        compressed_context = context
        compression_rounds = 0
        
        if auto_compress and context:
            compressed_context, compression_rounds = self.compressor.compress(
                context, question
            )
        
        # Build prompt from template
        prompt = self.TEMPLATES["single_word"].format(
            context=compressed_context if compressed_context else "No additional context provided",
            question=question
        )
        
        # Get response with context monitoring
        response = self.client.generate(self.model, prompt, show_context=show_context)
        
        # Parse response
        word, confidence = self.parser.parse_single_word(response)
        
        return SingleWordResult(
            word=word,
            confidence=confidence,
            raw=response,
            context_compressed=compression_rounds > 0,
            compression_rounds=compression_rounds
        )
    
    def open(
        self,
        prompt: str,
        context: str = "",
        auto_compress: bool = True,
        show_context: bool = True
    ) -> OpenResult:
        """Ask AI for an open-ended detailed response"""
        
        # Handle context compression if needed
        compressed_context = context
        compression_rounds = 0
        
        if auto_compress and context:
            compressed_context, compression_rounds = self.compressor.compress(
                context, prompt
            )
        
        # Build prompt from template
        full_prompt = self.TEMPLATES["open"].format(
            context=compressed_context if compressed_context else "No additional context provided",
            prompt=prompt
        )
        
        # Get response with context monitoring
        response = self.client.generate(self.model, full_prompt, show_context=show_context)
        
        return OpenResult(
            content=response.strip(),
            raw=response,
            context_compressed=compression_rounds > 0,
            compression_rounds=compression_rounds
        )
    
    def file_write(
        self,
        requirements: str,
        context: str = "",
        auto_compress: bool = True,
        show_context: bool = True
    ) -> FileWriteResult:
        """Ask AI to generate file content"""
        
        # Handle context compression if needed
        compressed_context = context
        compression_rounds = 0
        
        if auto_compress and context:
            compressed_context, compression_rounds = self.compressor.compress(
                context, requirements
            )
        
        # Build prompt from template
        prompt = self.TEMPLATES["file_write"].format(
            context=compressed_context if compressed_context else "No additional context provided",
            requirements=requirements
        )
        
        # Get response with context monitoring
        response = self.client.generate(self.model, prompt, show_context=show_context)
        
        # Clean the response
        content = self.parser.clean_file_content(response)
        
        return FileWriteResult(
            content=content,
            raw=response,
            context_compressed=compression_rounds > 0,
            compression_rounds=compression_rounds
        )
