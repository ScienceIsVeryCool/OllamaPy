__version__ = "0.8.0"

from .main import hello, greet, chat
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .chat_session import ChatSession
from .terminal_interface import TerminalInterface
from .skills import (
    get_available_actions, 
    get_actions_with_vibe_tests, 
    execute_action,
    SKILL_REGISTRY,
    clear_action_logs,
    get_action_logs,
    Skill,
    SkillRegistry
)
from .parameter_utils import (
    convert_parameter_value,
    validate_required_parameters,
    extract_numbers_from_text,
    extract_expressions_from_text,
    prepare_function_parameters,
    extract_parameter_from_response
)
from .vibe_tests import VibeTestRunner, run_vibe_tests
from .vibe_report import VibeTestReportGenerator
from .skill_generator import SkillGenerator, SkillValidator, SkillGenerationResult, run_skill_generation

__all__ = [
    "hello", 
    "greet", 
    "chat", 
    "OllamaClient",
    "ModelManager",
    "AnalysisEngine", 
    "ChatSession",
    "TerminalInterface",
    "get_available_actions",
    "get_actions_with_vibe_tests",
    "execute_action",
    "SKILL_REGISTRY",
    "Skill",
    "SkillRegistry",
    "clear_action_logs",
    "get_action_logs",
    "convert_parameter_value",
    "validate_required_parameters", 
    "extract_numbers_from_text",
    "extract_expressions_from_text",
    "prepare_function_parameters",
    "extract_parameter_from_response",
    "VibeTestRunner", 
    "run_vibe_tests",
    "VibeTestReportGenerator",
    "SkillGenerator",
    "SkillValidator",
    "SkillGenerationResult",
    "run_skill_generation"
]