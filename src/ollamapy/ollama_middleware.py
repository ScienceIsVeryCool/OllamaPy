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
                    return jsonify({'error': 'No JSON body provided'}), 400
                
                model = data.get('model')
                prompt = data.get('prompt')
                system = data.get('system')
                stream = data.get('stream', False)
                
                if not model or not prompt:
                    return jsonify({'error': 'Missing required fields: model, prompt'}), 400
                
                # Process with skills if enabled
                if self.enable_skills and self.analysis_engine:
                    response_text = self._process_with_skills(model, prompt, system)
                else:
                    # Direct passthrough to Ollama
                    response_text = self.client.generate(model, prompt, system)
                
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
                    response_text = self.client.generate(model, prompt, system)
                
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
        """Process prompt through the skills system."""
        try:
            # Use analysis engine to get applicable actions
            applicable_actions = self.analysis_engine.select_all_applicable_actions(prompt)
            
            if applicable_actions:
                # Use the first applicable action
                action_name, action_params = applicable_actions[0]
                
                # Execute skill if available
                if action_name in SKILL_REGISTRY.skills:
                    try:
                        SKILL_REGISTRY.execute_skill(action_name, action_params)
                        # Get execution logs as output
                        logs = SKILL_REGISTRY.get_logs()
                        if logs:
                            skill_output = '\n'.join(logs)
                            enhanced_prompt = f"{prompt}\n\nSkill '{action_name}' executed:\n{skill_output}"
                            return self.client.generate(model, enhanced_prompt, system)
                    except Exception as skill_error:
                        logger.warning(f"Skill execution failed: {skill_error}")
            
            # Fallback to regular generation if no skills used
            return self.client.generate(model, prompt, system)
            
        except Exception as e:
            logger.error(f"Error processing with skills: {e}")
            # Fallback to regular generation on any error
            return self.client.generate(model, prompt, system)
    
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