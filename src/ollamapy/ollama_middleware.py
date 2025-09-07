"""Ollama-compatible middleware server that enhances requests with OllamaPy's skills system."""

import json
import time
import logging
from typing import Dict, Any, Optional, Generator
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

from .ollama_client import OllamaClient
from .analysis_engine import AnalysisEngine
from .skills import SKILL_REGISTRY, get_available_actions
from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class OllamaMiddlewareServer:
    """Ollama-compatible API server that enhances requests with OllamaPy's skills system."""
    
    def __init__(
        self,
        port: int = 11435,
        upstream_ollama: str = "http://localhost:11434",
        enable_skills: bool = True,
        enable_analysis: bool = True,
        analysis_model: str = "gemma3:4b"
    ):
        """Initialize the middleware server.
        
        Args:
            port: Port to run the middleware server on
            upstream_ollama: URL of the upstream Ollama server
            enable_skills: Whether to enable skills system enhancement
            enable_analysis: Whether to enable analysis engine
            analysis_model: Model to use for analysis
        """
        self.port = port
        self.upstream_ollama = upstream_ollama
        self.enable_skills = enable_skills
        self.enable_analysis = enable_analysis
        self.analysis_model = analysis_model
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web frontends
        
        # Initialize OllamaPy components
        self.client = OllamaClient(base_url=upstream_ollama)
        self.model_manager = ModelManager(self.client)
        
        if enable_analysis:
            self.analysis_engine = AnalysisEngine(analysis_model, self.client)
        else:
            self.analysis_engine = None
        
        # Set up routes
        self._setup_routes()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
    
    def _setup_routes(self):
        """Set up all API routes to match Ollama's API."""
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate():
            """Ollama-compatible generation endpoint with skills enhancement."""
            try:
                data = request.json
                if not data:
                    logger.warning("📥 [GENERATE] No JSON body provided")
                    return jsonify({'error': 'No JSON body provided'}), 400
                
                model = data.get('model')
                prompt = data.get('prompt')
                system = data.get('system')
                stream = data.get('stream', False)
                
                logger.info(f"📥 [GENERATE] Request - Model: {model}, Stream: {stream}, Prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
                
                if not model or not prompt:
                    logger.warning("📥 [GENERATE] Missing required fields")
                    return jsonify({'error': 'Missing required fields: model, prompt'}), 400
                
                # Process with skills if enabled
                if self.enable_skills and self.analysis_engine:
                    response_text = self._process_with_skills(model, prompt, system)
                else:
                    # Direct passthrough to Ollama
                    response_text = self.client.generate(model, prompt, system, show_context=False)
                
                # Clean response to ensure no tool-call patterns leak through
                response_text = self._clean_response_for_continue(response_text)
                
                if stream:
                    # Return streaming response
                    return Response(
                        self._stream_response(model, response_text),
                        mimetype='application/x-ndjson'
                    )
                else:
                    # Return non-streaming response
                    return jsonify({
                        'model': model,
                        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'response': response_text,
                        'done': True,
                        'context': [],  # Simplified for compatibility
                        'total_duration': 0,
                        'load_duration': 0,
                        'prompt_eval_count': len(prompt.split()),
                        'prompt_eval_duration': 0,
                        'eval_count': len(response_text.split()),
                        'eval_duration': 0
                    })
                    
            except Exception as e:
                logger.error(f"Error in /api/generate: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Ollama-compatible chat endpoint with skills enhancement."""
            try:
                data = request.json
                if not data:
                    return jsonify({'error': 'No JSON body provided'}), 400
                
                model = data.get('model')
                messages = data.get('messages', [])
                stream = data.get('stream', False)
                
                if not model or not messages:
                    return jsonify({'error': 'Missing required fields: model, messages'}), 400
                
                # Convert messages to prompt for processing
                prompt = self._messages_to_prompt(messages)
                system = self._extract_system_from_messages(messages)
                
                # Process with skills if enabled
                if self.enable_skills and self.analysis_engine:
                    response_text = self._process_with_skills(model, prompt, system)
                else:
                    # Direct passthrough to Ollama
                    response_text = self.client.generate(model, prompt, system, show_context=False)
                
                # Clean response to ensure no tool-call patterns leak through
                response_text = self._clean_response_for_continue(response_text)
                
                if stream:
                    # Return streaming response
                    return Response(
                        self._stream_chat_response(model, response_text),
                        mimetype='application/x-ndjson'
                    )
                else:
                    # Return non-streaming response
                    return jsonify({
                        'model': model,
                        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'message': {
                            'role': 'assistant',
                            'content': response_text
                        },
                        'done': True,
                        'total_duration': 0,
                        'load_duration': 0,
                        'prompt_eval_count': len(prompt.split()),
                        'prompt_eval_duration': 0,
                        'eval_count': len(response_text.split()),
                        'eval_duration': 0
                    })
                    
            except Exception as e:
                logger.error(f"Error in /api/chat: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tags', methods=['GET'])
        def tags():
            """List available models - pass through to upstream Ollama."""
            try:
                models = self.client.list_models()
                # Format to match Ollama's response
                formatted_models = []
                for model in models:
                    formatted_models.append({
                        'name': model,
                        'model': model,
                        'modified_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'size': 0,  # Simplified
                        'digest': '',  # Simplified
                        'details': {
                            'parent_model': '',
                            'format': '',
                            'family': '',
                            'families': [],
                            'parameter_size': '',
                            'quantization_level': ''
                        }
                    })
                
                return jsonify({'models': formatted_models})
                
            except Exception as e:
                logger.error(f"Error in /api/tags: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/show', methods=['POST'])
        def show():
            """Show model information - pass through to upstream Ollama."""
            try:
                data = request.json
                if not data or 'name' not in data:
                    return jsonify({'error': 'Missing model name'}), 400
                
                # For now, return basic model info
                # In a full implementation, you'd proxy this to upstream Ollama
                return jsonify({
                    'license': '',
                    'modelfile': '',
                    'parameters': '',
                    'template': '',
                    'details': {
                        'parent_model': '',
                        'format': '',
                        'family': '',
                        'families': [],
                        'parameter_size': '',
                        'quantization_level': ''
                    }
                })
                
            except Exception as e:
                logger.error(f"Error in /api/show: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/pull', methods=['POST'])
        def pull():
            """Pull model - pass through to upstream Ollama."""
            try:
                data = request.json
                if not data or 'name' not in data:
                    return jsonify({'error': 'Missing model name'}), 400
                
                model_name = data['name']
                success = self.client.pull_model(model_name)
                
                if success:
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'error': 'Failed to pull model'}), 500
                    
            except Exception as e:
                logger.error(f"Error in /api/pull: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            upstream_healthy = self.client.is_available()
            return jsonify({
                'status': 'healthy' if upstream_healthy else 'unhealthy',
                'upstream_ollama': upstream_healthy,
                'skills_enabled': self.enable_skills,
                'analysis_enabled': self.enable_analysis,
                'skills_count': len(SKILL_REGISTRY.skills) if self.enable_skills else 0
            })
    
    def _process_with_skills(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Process prompt with skills enhancement - SILENT MODE for Continue compatibility."""
        try:
            logger.info(f"🔍 [MIDDLEWARE] Processing request: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
            
            # Silently check if we should use skills for this prompt
            skill_results = self._execute_skills_silently(prompt)
            
            if skill_results:
                logger.info(f"✅ [MIDDLEWARE] Skills executed: {[r['skill'] for r in skill_results]}")
                # Build enhanced prompt with skill results as context
                enhanced_prompt = self._build_enhanced_prompt(prompt, skill_results)
                logger.info(f"📝 [MIDDLEWARE] Enhanced prompt created (length: {len(enhanced_prompt)} chars)")
                response = self.client.generate(model, enhanced_prompt, system, show_context=False)
                logger.info(f"🎯 [MIDDLEWARE] Generated response with skills (length: {len(response)} chars)")
                return response
            else:
                logger.info(f"⚪ [MIDDLEWARE] No skills triggered, using direct Ollama")
                response = self.client.generate(model, prompt, system, show_context=False)
                logger.info(f"🎯 [MIDDLEWARE] Direct response (length: {len(response)} chars)")
                return response
                
        except Exception as e:
            logger.error(f"❌ [MIDDLEWARE] Skills processing failed: {e}")
            # Always fallback to direct Ollama on any error
            return self.client.generate(model, prompt, system, show_context=False)
    
    def _execute_skills_silently(self, prompt: str) -> list:
        """Execute applicable skills silently and return results."""
        try:
            skill_results = []
            prompt_lower = prompt.lower()
            
            logger.info(f"🔎 [SKILLS] Analyzing prompt for skill triggers...")
            
            # Check for calculation requests
            calc_triggers = ['calculate', 'compute', '+', '-', '*', '/', 'math', 'square root', '=', 'what is']
            if any(word in prompt_lower for word in calc_triggers):
                logger.info(f"🧮 [SKILLS] Math keywords detected: {[w for w in calc_triggers if w in prompt_lower]}")
                
                if 'calculate' in SKILL_REGISTRY.skills:
                    try:
                        logger.info(f"⚡ [SKILLS] Executing 'calculate' skill...")
                        # Clear logs first
                        SKILL_REGISTRY.execution_logs.clear()
                        SKILL_REGISTRY.execute_skill('calculate', {'expression': prompt})
                        logs = SKILL_REGISTRY.get_logs()
                        
                        logger.info(f"📋 [SKILLS] Calculate skill logs: {logs}")
                        
                        if logs:
                            result = '\n'.join([log for log in logs if '[calculate]' in log])
                            if result:
                                clean_result = result.replace('[calculate]', '').strip()
                                skill_results.append({
                                    'skill': 'calculate',
                                    'result': clean_result
                                })
                                logger.info(f"✅ [SKILLS] Calculate result: '{clean_result}'")
                            else:
                                logger.warning(f"⚠️ [SKILLS] Calculate skill ran but no result found")
                        else:
                            logger.warning(f"⚠️ [SKILLS] Calculate skill ran but no logs generated")
                    except Exception as e:
                        logger.error(f"❌ [SKILLS] Calculate skill failed: {e}")
                else:
                    logger.warning(f"⚠️ [SKILLS] Calculate skill not found in registry")
            
            # Check for weather requests
            weather_triggers = ['weather', 'temperature', 'forecast', 'climate']
            if any(word in prompt_lower for word in weather_triggers):
                logger.info(f"🌤️ [SKILLS] Weather keywords detected: {[w for w in weather_triggers if w in prompt_lower]}")
                
                if 'getWeather' in SKILL_REGISTRY.skills:
                    try:
                        logger.info(f"⚡ [SKILLS] Executing 'getWeather' skill...")
                        SKILL_REGISTRY.execution_logs.clear()
                        SKILL_REGISTRY.execute_skill('getWeather', {})
                        logs = SKILL_REGISTRY.get_logs()
                        
                        logger.info(f"📋 [SKILLS] Weather skill logs: {logs}")
                        
                        if logs:
                            # Look for weather-related log entries
                            weather_logs = [log for log in logs if any(tag in log for tag in ['[Weather]', '[getWeather]', '[Weather Check]'])]
                            if weather_logs:
                                # Clean up the weather data
                                clean_result = '\n'.join(weather_logs)
                                clean_result = clean_result.replace('[Weather Check]', '').replace('[Weather]', '').replace('[getWeather]', '').strip()
                                skill_results.append({
                                    'skill': 'weather',
                                    'result': clean_result
                                })
                                logger.info(f"✅ [SKILLS] Weather result captured ({len(weather_logs)} entries)")
                    except Exception as e:
                        logger.error(f"❌ [SKILLS] Weather skill failed: {e}")
                else:
                    logger.warning(f"⚠️ [SKILLS] getWeather skill not found in registry")
            
            # Check for time requests
            time_triggers = ['time', 'date', 'today', 'now', 'current']
            if any(word in prompt_lower for word in time_triggers):
                logger.info(f"🕐 [SKILLS] Time keywords detected: {[w for w in time_triggers if w in prompt_lower]}")
                
                if 'getTime' in SKILL_REGISTRY.skills:
                    try:
                        logger.info(f"⚡ [SKILLS] Executing 'getTime' skill...")
                        SKILL_REGISTRY.execution_logs.clear()
                        SKILL_REGISTRY.execute_skill('getTime', {})
                        logs = SKILL_REGISTRY.get_logs()
                        
                        logger.info(f"📋 [SKILLS] Time skill logs: {logs}")
                        
                        if logs:
                            # Look for time-related log entries  
                            time_logs = [log for log in logs if any(tag in log for tag in ['[Time]', '[getTime]', '[Current Time]'])]
                            if time_logs:
                                # Clean up the time data
                                clean_result = '\n'.join(time_logs)
                                clean_result = clean_result.replace('[Time]', '').replace('[getTime]', '').replace('[Current Time]', '').strip()
                                skill_results.append({
                                    'skill': 'time',
                                    'result': clean_result
                                })
                                logger.info(f"✅ [SKILLS] Time result captured ({len(time_logs)} entries)")
                    except Exception as e:
                        logger.error(f"❌ [SKILLS] Time skill failed: {e}")
                else:
                    logger.warning(f"⚠️ [SKILLS] getTime skill not found in registry")
            
            if not skill_results:
                logger.info(f"ℹ️ [SKILLS] No skill triggers found in prompt")
            
            if skill_results:
                logger.info(f"✅ [SKILLS] Total skills executed: {len(skill_results)}")
            else:
                logger.info(f"⚪ [SKILLS] No skills executed")
                
            return skill_results
            
        except Exception as e:
            logger.error(f"❌ [SKILLS] Silent skill execution failed: {e}")
            return []
    
    def _build_enhanced_prompt(self, original_prompt: str, skill_results: list) -> str:
        """Build enhanced prompt with skill results embedded as context."""
        if not skill_results:
            return original_prompt
        
        # Build context from skill results
        context_parts = []
        for result in skill_results:
            skill_name = result['skill']
            skill_output = result['result']
            
            # Format skill output as natural context (not as tool calls)
            if skill_name == 'calculate':
                context_parts.append(f"Mathematical calculation: {skill_output}")
            elif skill_name == 'weather':
                context_parts.append(f"Current weather information: {skill_output}")
            elif skill_name == 'time':
                context_parts.append(f"Current time/date: {skill_output}")
            else:
                context_parts.append(f"Relevant information: {skill_output}")
        
        # Build enhanced prompt with context embedded naturally
        enhanced = f"""Context: {' | '.join(context_parts)}

User question: {original_prompt}

Please provide a helpful response using the context above where relevant."""
        
        return enhanced
    
    def _clean_response_for_continue(self, response_text: str) -> str:
        """Remove any tool-use indicators from response for Continue compatibility."""
        import re
        
        logger.info(f"🧹 [CLEAN] Original response length: {len(response_text)} chars")
        
        # Remove common patterns that Continue might interpret as tool calls
        patterns_to_remove = [
            r'🔍.*?\n',           # Analysis indicators
            r'✓.*?\n',            # Success indicators  
            r'✗.*?\n',            # Failure indicators
            r'🎯.*?\n',           # Target indicators
            r'\[.*?\].*?\n',      # Bracketed action indicators
            r'Context:.*?\n',     # Context usage indicators
            r'Analyzing.*?\n',    # Analysis mentions
            r'Selected.*action.*?\n', # Action selection mentions
            r'Extracting.*parameter.*?\n', # Parameter extraction
            r'Executing.*?\n',    # Execution mentions
            r'<think>.*?</think>', # Thinking blocks
            r'```.*?```',         # Code blocks that might look like tools
        ]
        
        cleaned = response_text
        patterns_found = []
        
        for pattern in patterns_to_remove:
            matches = re.findall(pattern, cleaned, flags=re.DOTALL | re.IGNORECASE)
            if matches:
                patterns_found.extend(matches)
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove multiple newlines
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned)
        
        if patterns_found:
            logger.info(f"🧹 [CLEAN] Removed patterns: {patterns_found}")
        
        logger.info(f"✅ [CLEAN] Cleaned response length: {len(cleaned.strip())} chars")
        
        return cleaned.strip()
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert chat messages to a single prompt."""
        prompt_parts = []
        for msg in messages:
            if msg.get('role') == 'user':
                prompt_parts.append(msg.get('content', ''))
        return '\n'.join(prompt_parts)
    
    def _extract_system_from_messages(self, messages: list) -> Optional[str]:
        """Extract system message from messages."""
        for msg in messages:
            if msg.get('role') == 'system':
                return msg.get('content')
        return None
    
    def _stream_response(self, model: str, response_text: str) -> Generator[str, None, None]:
        """Generate streaming response for /api/generate."""
        # Simulate streaming by yielding chunks
        words = response_text.split()
        for i, word in enumerate(words):
            chunk = {
                'model': model,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'response': word + (' ' if i < len(words) - 1 else ''),
                'done': False
            }
            yield json.dumps(chunk) + '\n'
            time.sleep(0.01)  # Small delay to simulate streaming
        
        # Final chunk
        final_chunk = {
            'model': model,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'response': '',
            'done': True,
            'context': [],
            'total_duration': 0,
            'load_duration': 0,
            'prompt_eval_count': 0,
            'prompt_eval_duration': 0,
            'eval_count': len(words),
            'eval_duration': 0
        }
        yield json.dumps(final_chunk) + '\n'
    
    def _stream_chat_response(self, model: str, response_text: str) -> Generator[str, None, None]:
        """Generate streaming response for /api/chat."""
        # Simulate streaming by yielding chunks
        words = response_text.split()
        for i, word in enumerate(words):
            chunk = {
                'model': model,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'message': {
                    'role': 'assistant',
                    'content': word + (' ' if i < len(words) - 1 else '')
                },
                'done': False
            }
            yield json.dumps(chunk) + '\n'
            time.sleep(0.01)  # Small delay to simulate streaming
        
        # Final chunk
        final_chunk = {
            'model': model,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'message': {
                'role': 'assistant',
                'content': ''
            },
            'done': True,
            'total_duration': 0,
            'load_duration': 0,
            'prompt_eval_count': 0,
            'prompt_eval_duration': 0,
            'eval_count': len(words),
            'eval_duration': 0
        }
        yield json.dumps(final_chunk) + '\n'
    
    def run(self):
        """Start the middleware server."""
        print(f"🚀 OllamaPy Middleware Server starting...")
        print(f"📡 Middleware running on: http://localhost:{self.port}")
        print(f"🔗 Upstream Ollama: {self.upstream_ollama}")
        print(f"🎯 Skills system: {'Enabled' if self.enable_skills else 'Disabled'}")
        print(f"🔍 Analysis engine: {'Enabled' if self.enable_analysis else 'Disabled'}")
        
        if self.enable_skills:
            print(f"📚 Available skills: {len(SKILL_REGISTRY.skills)}")
        
        print(f"\n💡 Configure your Ollama-compatible tools to use: http://localhost:{self.port}")
        print("   Example for Continue: Set 'apiBase' to the above URL")
        print("\n🔥 Ready to serve enhanced requests!")
        
        # Log available skills for debugging
        if self.enable_skills:
            available_skills = list(SKILL_REGISTRY.skills.keys())
            logger.info(f"📚 [STARTUP] Available skills: {available_skills}")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)


def run_middleware_server(
    port: int = 11435,
    upstream_ollama: str = "http://localhost:11434", 
    enable_skills: bool = True,
    enable_analysis: bool = True,
    analysis_model: str = "gemma3:4b"
):
    """Run the Ollama middleware server.
    
    Args:
        port: Port to run the middleware server on
        upstream_ollama: URL of the upstream Ollama server
        enable_skills: Whether to enable skills system enhancement
        enable_analysis: Whether to enable analysis engine
        analysis_model: Model to use for analysis
    """
    server = OllamaMiddlewareServer(
        port=port,
        upstream_ollama=upstream_ollama,
        enable_skills=enable_skills,
        enable_analysis=enable_analysis,
        analysis_model=analysis_model
    )
    server.run()