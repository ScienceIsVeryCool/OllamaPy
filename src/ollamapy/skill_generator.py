"""Automated skill generation system using AI."""

import json
import ast
import sys
import traceback
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .ai_query import AIQuery, FileWriteResult, OpenResult
from .ollama_client import OllamaClient
from .skills import Skill, SkillRegistry
from .vibe_tests import VibeTestRunner
from .analysis_engine import AnalysisEngine


@dataclass
class SkillGenerationResult:
    """Result of a skill generation attempt."""
    success: bool
    skill: Optional[Skill]
    validation_errors: List[str]
    compilation_success: bool
    vibe_test_passed: bool
    vibe_test_results: Optional[Dict[str, Any]]
    generation_time: float
    iterations_needed: int


class SkillValidator:
    """Validates generated skills for correctness and safety."""
    
    def __init__(self):
        self.required_fields = ['name', 'description', 'vibe_test_phrases', 'parameters', 'function_code']
        self.forbidden_imports = ['subprocess', '__import__', 'compile']
        self.forbidden_functions = ['eval(', 'exec(']
        self.required_function_name = 'execute'
    
    def validate_skill_structure(self, skill_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate the structure of generated skill data.
        
        Args:
            skill_data: The generated skill data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in skill_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate name
        if 'name' in skill_data:
            name = skill_data['name']
            if not isinstance(name, str) or not name:
                errors.append("Skill name must be a non-empty string")
            elif not name.replace('_', '').isalnum():
                errors.append("Skill name must be alphanumeric (underscores allowed)")
        
        # Validate description
        if 'description' in skill_data:
            if not isinstance(skill_data['description'], str) or len(skill_data['description']) < 10:
                errors.append("Description must be at least 10 characters long")
        
        # Validate vibe test phrases
        if 'vibe_test_phrases' in skill_data:
            phrases = skill_data['vibe_test_phrases']
            if not isinstance(phrases, list) or len(phrases) < 3:
                errors.append("Must have at least 3 vibe test phrases")
            elif not all(isinstance(p, str) and p for p in phrases):
                errors.append("All vibe test phrases must be non-empty strings")
        
        # Validate parameters
        if 'parameters' in skill_data:
            if not isinstance(skill_data['parameters'], dict):
                errors.append("Parameters must be a dictionary")
            else:
                for param_name, param_spec in skill_data['parameters'].items():
                    if not isinstance(param_spec, dict):
                        errors.append(f"Parameter '{param_name}' specification must be a dictionary")
                    elif 'type' not in param_spec or 'description' not in param_spec:
                        errors.append(f"Parameter '{param_name}' must have 'type' and 'description'")
        
        # Validate function code
        if 'function_code' in skill_data:
            code = skill_data['function_code']
            if not isinstance(code, str) or len(code) < 20:
                errors.append("Function code must be at least 20 characters")
            elif self.required_function_name not in code:
                errors.append(f"Function code must define a function named '{self.required_function_name}'")
        
        return len(errors) == 0, errors
    
    def validate_code_safety(self, function_code: str) -> Tuple[bool, List[str]]:
        """Validate that the generated code is safe to execute.
        
        Args:
            function_code: The Python function code to validate
            
        Returns:
            Tuple of (is_safe, security_issues)
        """
        issues = []
        
        # Check for forbidden imports/functions
        for forbidden in self.forbidden_imports:
            if forbidden in function_code:
                issues.append(f"Forbidden import '{forbidden}' detected in code")
        
        # Check for forbidden function calls
        for forbidden in self.forbidden_functions:
            if forbidden in function_code:
                issues.append(f"Forbidden function call '{forbidden}' detected in code")
        
        # Check for file system operations outside safe methods
        dangerous_ops = ['rmdir', 'unlink', 'remove', 'rmtree']
        for op in dangerous_ops:
            if op in function_code:
                issues.append(f"Potentially dangerous operation '{op}' detected")
        
        return len(issues) == 0, issues
    
    def validate_code_compilation(self, function_code: str) -> Tuple[bool, Optional[str]]:
        """Validate that the code compiles without syntax errors.
        
        Args:
            function_code: The Python function code to compile
            
        Returns:
            Tuple of (compiles_successfully, error_message)
        """
        try:
            # Parse the code to check for syntax errors
            ast.parse(function_code)
            
            # Try to compile it
            compile(function_code, '<generated>', 'exec')
            
            # Check that it defines the required function
            namespace: Dict[str, Any] = {}
            exec(function_code, namespace)
            
            if self.required_function_name not in namespace:
                return False, f"Code does not define required function '{self.required_function_name}'"
            
            if not callable(namespace[self.required_function_name]):
                return False, f"'{self.required_function_name}' is not callable"
            
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"


class SkillGenerator:
    """Generates new skills automatically using AI."""
    
    def __init__(self, model: str = "gemma3:4b", analysis_model: Optional[str] = None):
        """Initialize the skill generator.
        
        Args:
            model: The model to use for skill generation
            analysis_model: Optional model for vibe testing (defaults to main model)
        """
        self.model = model
        self.analysis_model = analysis_model or model
        self.client = OllamaClient()
        self.ai_query = AIQuery(self.client, model)
        self.validator = SkillValidator()
        self.skill_registry = SkillRegistry()
        
        # Template for skill generation
        self.skill_template = self._create_skill_template()
    
    def _create_skill_template(self) -> str:
        """Create a comprehensive template for skill generation."""
        return """You are tasked with creating a new Python skill for an AI assistant system.

A skill is a discrete capability that the AI can execute. Here's the complete structure:

SKILL DATA MODEL:
- name: str (alphanumeric with underscores, e.g., "calculate_statistics")
- description: str (when the skill should be used, 10+ characters)
- vibe_test_phrases: List[str] (at least 3 example user inputs that should trigger this skill)
- parameters: Dict[str, Dict[str, Any]] (input parameters the skill needs)
  Format: {"param_name": {"type": "string|number", "description": "...", "required": bool}}
- function_code: str (Python code defining an 'execute' function)
- scope: str (always "local" for generated skills)
- role: str (category like "mathematics", "text_processing", "data_analysis", etc.)

FUNCTION CODE REQUIREMENTS:
1. Must define a function named 'execute' with appropriate parameters
2. Use 'log(message)' to output results (this is pre-defined)
3. Can import: math, json, datetime, os, Path
4. Cannot use: subprocess, eval, exec, or dangerous operations
5. Include error handling with try/except blocks
6. Add descriptive log messages for what the skill is doing

EXAMPLE SKILL:
```json
{
    "name": "word_counter",
    "description": "Count words, characters, and lines in provided text",
    "vibe_test_phrases": [
        "How many words are in this text?",
        "Count the words in this paragraph",
        "Tell me the word count of this document",
        "Analyze the length of this text"
    ],
    "parameters": {
        "text": {
            "type": "string",
            "description": "The text to analyze",
            "required": true
        }
    },
    "function_code": "def execute(text: str):\\n    log('[Word Counter] Starting text analysis...')\\n    try:\\n        word_count = len(text.split())\\n        char_count = len(text)\\n        line_count = len(text.splitlines())\\n        \\n        log(f'[Word Counter] Word count: {word_count}')\\n        log(f'[Word Counter] Character count: {char_count}')\\n        log(f'[Word Counter] Line count: {line_count}')\\n        \\n        avg_word_length = char_count / word_count if word_count > 0 else 0\\n        log(f'[Word Counter] Average word length: {avg_word_length:.2f} characters')\\n    except Exception as e:\\n        log(f'[Word Counter] Error analyzing text: {str(e)}')",
    "scope": "local",
    "role": "text_processing"
}
```

GENERATION TASK: {task}

IMPORTANT RULES:
1. The skill must be useful and well-defined
2. Vibe test phrases must be realistic user inputs
3. Parameters should cover necessary inputs
4. Function code must be complete and handle errors
5. Use clear, descriptive names
6. Output ONLY valid JSON, no additional text
"""
    
    def generate_skill_idea(self) -> str:
        """Generate a random skill idea using AI.
        
        Returns:
            Description of a skill to generate
        """
        prompt = """Generate a creative and useful skill idea for an AI assistant.

Think of common tasks users might need help with that aren't already covered by basic functions.
Consider areas like:
- Text analysis and processing
- Data manipulation and formatting
- Mathematical calculations beyond basics
- Pattern recognition
- Code generation helpers
- File content analysis
- Time and date calculations
- Unit conversions
- Statistical analysis
- String manipulations

Describe the skill in one sentence, focusing on what it does and when it would be useful.
Be specific and practical.

Your response:"""
        
        result = self.ai_query.open(prompt)
        return result.content.strip()
    
    def generate_skill(self, skill_idea: Optional[str] = None, max_attempts: int = 3) -> SkillGenerationResult:
        """Generate a complete skill using AI.
        
        Args:
            skill_idea: Optional specific skill to generate. If None, generates random idea.
            max_attempts: Maximum attempts to generate valid skill
            
        Returns:
            SkillGenerationResult with generation details
        """
        import time
        start_time = time.time()
        
        # Generate skill idea if not provided
        if not skill_idea:
            skill_idea = self.generate_skill_idea()
            print(f"🎯 Generated skill idea: {skill_idea}")
        
        validation_errors = []
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            print(f"🔧 Generation attempt {attempts}/{max_attempts}...")
            
            # Generate the skill using AI
            skill_prompt = self.skill_template.format(task=skill_idea)
            result = self.ai_query.file_write(
                requirements=skill_prompt,
                context="Generate a complete skill definition as valid JSON"
            )
            
            try:
                # Parse the generated JSON
                skill_data = json.loads(result.content)
                
                # Validate structure
                is_valid, errors = self.validator.validate_skill_structure(skill_data)
                if not is_valid:
                    validation_errors.extend(errors)
                    print(f"❌ Validation errors: {errors}")
                    continue
                
                # Validate code safety
                is_safe, safety_issues = self.validator.validate_code_safety(
                    skill_data['function_code']
                )
                if not is_safe:
                    validation_errors.extend(safety_issues)
                    print(f"❌ Safety issues: {safety_issues}")
                    continue
                
                # Validate code compilation
                compiles, compile_error = self.validator.validate_code_compilation(
                    skill_data['function_code']
                )
                if not compiles:
                    if compile_error:
                        validation_errors.append(compile_error)
                    print(f"❌ Compilation error: {compile_error}")
                    continue
                
                # Create Skill object
                skill = Skill(
                    name=skill_data['name'],
                    description=skill_data['description'],
                    vibe_test_phrases=skill_data['vibe_test_phrases'],
                    parameters=skill_data['parameters'],
                    function_code=skill_data['function_code'],
                    verified=False,  # Never auto-verify
                    scope="local",  # Always local for generated skills
                    role=skill_data.get('role', 'general')
                )
                
                # Register the skill
                success = self.skill_registry.register_skill(skill)
                if not success:
                    validation_errors.append("Failed to register skill")
                    continue
                
                print(f"✅ Skill '{skill.name}' generated and registered successfully!")
                
                # Run vibe test on the new skill
                print(f"🧪 Running vibe test for '{skill.name}'...")
                vibe_passed, vibe_results = self.run_isolated_vibe_test(skill)
                
                generation_time = time.time() - start_time
                
                return SkillGenerationResult(
                    success=True,
                    skill=skill,
                    validation_errors=[],
                    compilation_success=True,
                    vibe_test_passed=vibe_passed,
                    vibe_test_results=vibe_results,
                    generation_time=generation_time,
                    iterations_needed=attempts
                )
                
            except json.JSONDecodeError as e:
                validation_errors.append(f"JSON parse error: {str(e)}")
                print(f"❌ Failed to parse generated JSON: {e}")
            except Exception as e:
                validation_errors.append(f"Unexpected error: {str(e)}")
                print(f"❌ Unexpected error: {e}")
        
        # All attempts failed
        generation_time = time.time() - start_time
        return SkillGenerationResult(
            success=False,
            skill=None,
            validation_errors=validation_errors,
            compilation_success=False,
            vibe_test_passed=False,
            vibe_test_results=None,
            generation_time=generation_time,
            iterations_needed=attempts
        )
    
    def run_isolated_vibe_test(self, skill: Skill, iterations: int = 3) -> Tuple[bool, Dict[str, Any]]:
        """Run vibe test only for a specific newly generated skill.
        
        Args:
            skill: The skill to test
            iterations: Number of test iterations per phrase
            
        Returns:
            Tuple of (test_passed, test_results)
        """
        # Create a temporary registry with just this skill
        temp_registry = SkillRegistry(skills_directory=None)
        temp_registry.skills = {skill.name: skill}
        temp_registry.compiled_functions = self.skill_registry.compiled_functions
        
        # Create analysis engine for testing
        analysis_engine = AnalysisEngine(self.analysis_model, self.client)
        
        # Test each vibe phrase
        total_correct = 0
        total_tests = 0
        phrase_results = {}
        
        print(f"Testing {len(skill.vibe_test_phrases)} vibe test phrases...")
        
        for phrase in skill.vibe_test_phrases:
            phrase_correct = 0
            
            for i in range(iterations):
                try:
                    # Ask if this skill should be selected for this phrase
                    prompt = f"""Should the '{skill.name}' skill be used for this input: "{phrase}"?

Skill description: {skill.description}

Answer only 'yes' or 'no'."""
                    
                    response = analysis_engine.ask_yes_no_question(prompt)
                    
                    if response:
                        phrase_correct += 1
                        total_correct += 1
                    
                    total_tests += 1
                    
                except Exception as e:
                    print(f"Error testing phrase: {e}")
                    total_tests += 1
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            phrase_results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate
            }
            
            phrase_display = phrase[:50] + '...' if len(phrase) > 50 else phrase
            status = "✅" if success_rate >= 60 else "❌"
            print(f"  {status} '{phrase_display}': {phrase_correct}/{iterations} ({success_rate:.0f}%)")
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        test_passed = overall_success_rate >= 60.0
        
        print(f"Overall vibe test: {total_correct}/{total_tests} ({overall_success_rate:.0f}%)")
        
        return test_passed, {
            'skill_name': skill.name,
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success_rate,
            'phrase_results': phrase_results
        }
    
    def generate_batch(self, count: int = 5, skill_ideas: Optional[List[str]] = None) -> List[SkillGenerationResult]:
        """Generate multiple skills in batch.
        
        Args:
            count: Number of skills to generate
            skill_ideas: Optional list of specific skill ideas
            
        Returns:
            List of SkillGenerationResult objects
        """
        results = []
        
        print(f"🚀 Starting batch generation of {count} skills...")
        print("=" * 60)
        
        for i in range(count):
            print(f"\n📦 Generating skill {i+1}/{count}")
            print("-" * 40)
            
            skill_idea = skill_ideas[i] if skill_ideas and i < len(skill_ideas) else None
            result = self.generate_skill(skill_idea)
            results.append(result)
            
            if result.success and result.skill:
                print(f"✅ Successfully generated: {result.skill.name}")
            else:
                print(f"❌ Failed to generate skill after {result.iterations_needed} attempts")
        
        # Summary
        successful = sum(1 for r in results if r.success)
        vibe_passed = sum(1 for r in results if r.vibe_test_passed)
        
        print("\n" + "=" * 60)
        print(f"📊 Generation Summary:")
        print(f"  Total attempted: {count}")
        print(f"  Successfully generated: {successful}/{count}")
        print(f"  Passed vibe tests: {vibe_passed}/{successful}")
        print(f"  Average generation time: {sum(r.generation_time for r in results) / len(results):.2f}s")
        
        return results


def run_skill_generation(model: str = "gemma3:4b", analysis_model: Optional[str] = None, 
                        count: int = 1, ideas: Optional[List[str]] = None) -> bool:
    """Main entry point for skill generation.
    
    Args:
        model: Model to use for generation
        analysis_model: Model for vibe testing (defaults to main model)
        count: Number of skills to generate
        ideas: Optional list of specific skill ideas
        
    Returns:
        True if at least one skill was successfully generated
    """
    print("🤖 OllamaPy Automated Skill Generation")
    print("=" * 60)
    print(f"Generation model: {model}")
    print(f"Analysis model: {analysis_model or model}")
    print(f"Target count: {count}")
    print()
    
    generator = SkillGenerator(model, analysis_model)
    
    if count == 1 and not ideas:
        # Single skill generation
        result = generator.generate_skill()
        
        if result.success and result.skill:
            print(f"\n✅ Successfully generated skill: {result.skill.name}")
            print(f"   Description: {result.skill.description}")
            print(f"   Role: {result.skill.role}")
            print(f"   Vibe test: {'PASSED' if result.vibe_test_passed else 'FAILED'}")
            print(f"   Generation time: {result.generation_time:.2f}s")
            print(f"   Attempts needed: {result.iterations_needed}")
            return True
        else:
            print(f"\n❌ Failed to generate skill")
            print(f"   Validation errors: {result.validation_errors}")
            return False
    else:
        # Batch generation
        results = generator.generate_batch(count, ideas)
        successful = sum(1 for r in results if r.success)
        
        if successful > 0:
            print(f"\n✅ Successfully generated {successful}/{count} skills")
            
            # List generated skills
            print("\nGenerated skills:")
            for r in results:
                if r.success and r.skill:
                    status = "✅" if r.vibe_test_passed else "⚠️"
                    print(f"  {status} {r.skill.name}: {r.skill.description}")
            
            return True
        else:
            print(f"\n❌ Failed to generate any skills")
            return False