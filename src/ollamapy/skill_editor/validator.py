"""Skill validation utilities."""

import ast
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of skill validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class SkillValidator:
    """Validates skill data and code."""
    
    def __init__(self):
        """Initialize the validator."""
        self.required_fields = ['name', 'description', 'function_code']
        self.valid_parameter_types = ['string', 'number', 'boolean']
        self.valid_roles = [
            'general', 'text_processing', 'mathematics', 'data_analysis',
            'file_operations', 'web_utilities', 'time_date', 'formatting',
            'validation', 'emotional_response', 'information', 'advanced'
        ]
    
    def validate_skill_data(self, skill_data: Dict[str, Any]) -> ValidationResult:
        """Validate complete skill data structure.
        
        Args:
            skill_data: The skill data dictionary to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in skill_data or not skill_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate skill name
        if 'name' in skill_data:
            name_validation = self._validate_skill_name(skill_data['name'])
            errors.extend(name_validation.errors)
            warnings.extend(name_validation.warnings)
        
        # Validate description
        if 'description' in skill_data:
            desc_validation = self._validate_description(skill_data['description'])
            warnings.extend(desc_validation.warnings)
        
        # Validate role
        if 'role' in skill_data:
            role_validation = self._validate_role(skill_data['role'])
            errors.extend(role_validation.errors)
            warnings.extend(role_validation.warnings)
        
        # Validate parameters
        if 'parameters' in skill_data and skill_data['parameters']:
            param_validation = self._validate_parameters(skill_data['parameters'])
            errors.extend(param_validation.errors)
            warnings.extend(param_validation.warnings)
        
        # Validate vibe test phrases
        if 'vibe_test_phrases' in skill_data:
            vibe_validation = self._validate_vibe_phrases(skill_data['vibe_test_phrases'])
            warnings.extend(vibe_validation.warnings)
        
        # Validate function code
        if 'function_code' in skill_data:
            code_validation = self._validate_function_code(
                skill_data['function_code'], 
                skill_data.get('parameters', {})
            )
            errors.extend(code_validation.errors)
            warnings.extend(code_validation.warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_skill_name(self, name: str) -> ValidationResult:
        """Validate skill name."""
        errors = []
        warnings = []
        
        if not isinstance(name, str):
            errors.append("Skill name must be a string")
            return ValidationResult(False, errors, warnings)
        
        if not name.strip():
            errors.append("Skill name cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        # Check for valid identifier
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            errors.append("Skill name must be a valid Python identifier (no spaces or special characters except underscore)")
        
        # Length check
        if len(name) > 50:
            warnings.append("Skill name is quite long, consider shortening it")
        
        # Naming conventions
        if name[0].isupper():
            warnings.append("Skill names typically use camelCase or snake_case (starting with lowercase)")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_description(self, description: str) -> ValidationResult:
        """Validate skill description."""
        errors = []
        warnings = []
        
        if not isinstance(description, str):
            errors.append("Description must be a string")
            return ValidationResult(False, errors, warnings)
        
        if not description.strip():
            warnings.append("Description is empty - consider adding a clear description of when to use this skill")
            return ValidationResult(True, errors, warnings)
        
        if len(description) < 10:
            warnings.append("Description is very short - consider providing more detail")
        
        if len(description) > 500:
            warnings.append("Description is very long - consider making it more concise")
        
        # Check for common patterns
        if not any(word in description.lower() for word in ['when', 'use', 'for', 'to']):
            warnings.append("Description should clearly indicate when this skill should be used")
        
        return ValidationResult(True, errors, warnings)
    
    def _validate_role(self, role: str) -> ValidationResult:
        """Validate skill role."""
        errors = []
        warnings = []
        
        if not isinstance(role, str):
            errors.append("Role must be a string")
            return ValidationResult(False, errors, warnings)
        
        if role not in self.valid_roles:
            errors.append(f"Invalid role '{role}'. Valid roles: {', '.join(self.valid_roles)}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> ValidationResult:
        """Validate skill parameters."""
        errors = []
        warnings = []
        
        if not isinstance(parameters, dict):
            errors.append("Parameters must be a dictionary")
            return ValidationResult(False, errors, warnings)
        
        for param_name, param_info in parameters.items():
            # Validate parameter name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param_name):
                errors.append(f"Parameter name '{param_name}' must be a valid Python identifier")
            
            # Validate parameter info structure
            if not isinstance(param_info, dict):
                errors.append(f"Parameter '{param_name}' info must be a dictionary")
                continue
            
            # Check required fields
            if 'type' not in param_info:
                errors.append(f"Parameter '{param_name}' is missing 'type' field")
            elif param_info['type'] not in self.valid_parameter_types:
                errors.append(f"Parameter '{param_name}' has invalid type '{param_info['type']}'. Valid types: {', '.join(self.valid_parameter_types)}")
            
            # Check for description
            if 'description' not in param_info or not param_info['description']:
                warnings.append(f"Parameter '{param_name}' is missing a description")
            
            # Check required field
            if 'required' in param_info and not isinstance(param_info['required'], bool):
                errors.append(f"Parameter '{param_name}' 'required' field must be boolean")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_vibe_phrases(self, vibe_phrases: List[str]) -> ValidationResult:
        """Validate vibe test phrases."""
        errors = []
        warnings = []
        
        if not isinstance(vibe_phrases, list):
            errors.append("Vibe test phrases must be a list")
            return ValidationResult(False, errors, warnings)
        
        if not vibe_phrases:
            warnings.append("No vibe test phrases provided - the AI won't know when to use this skill")
            return ValidationResult(True, errors, warnings)
        
        if len(vibe_phrases) < 2:
            warnings.append("Consider adding more vibe test phrases for better AI recognition")
        
        for i, phrase in enumerate(vibe_phrases):
            if not isinstance(phrase, str):
                errors.append(f"Vibe test phrase {i+1} must be a string")
            elif not phrase.strip():
                warnings.append(f"Vibe test phrase {i+1} is empty")
            elif len(phrase) < 5:
                warnings.append(f"Vibe test phrase {i+1} is very short")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_function_code(self, code: str, parameters: Dict[str, Any] = None) -> ValidationResult:
        """Validate Python function code."""
        errors = []
        warnings = []
        
        if not isinstance(code, str):
            errors.append("Function code must be a string")
            return ValidationResult(False, errors, warnings)
        
        if not code.strip():
            errors.append("Function code cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        # Try to parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error in function code: {e}")
            return ValidationResult(False, errors, warnings)
        
        # Check for execute function
        has_execute = False
        execute_func = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'execute':
                has_execute = True
                execute_func = node
                break
        
        if not has_execute:
            errors.append("Function code must define an 'execute' function")
            return ValidationResult(False, errors, warnings)
        
        # Validate execute function signature
        if execute_func and parameters:
            param_validation = self._validate_execute_signature(execute_func, parameters)
            errors.extend(param_validation.errors)
            warnings.extend(param_validation.warnings)
        
        # Check for log usage
        if 'log(' not in code:
            warnings.append("Function should use log() to output results that the AI can see")
        
        # Check for potentially dangerous operations
        dangerous_patterns = [
            ('os.system', 'Using os.system() can be dangerous'),
            ('subprocess.call', 'Using subprocess.call() can be dangerous'),
            ('eval(', 'Using eval() can be dangerous'),
            ('exec(', 'Using exec() can be dangerous'),
            ('__import__', 'Dynamic imports can be dangerous'),
        ]
        
        for pattern, warning in dangerous_patterns:
            if pattern in code:
                warnings.append(warning)
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_execute_signature(self, func_node: ast.FunctionDef, parameters: Dict[str, Any]) -> ValidationResult:
        """Validate that execute function signature matches declared parameters."""
        errors = []
        warnings = []
        
        # Get function arguments
        func_args = [arg.arg for arg in func_node.args.args]
        
        # Check if all declared parameters are in function signature
        for param_name in parameters.keys():
            if param_name not in func_args:
                if parameters[param_name].get('required', False):
                    errors.append(f"Required parameter '{param_name}' not found in execute function signature")
                else:
                    warnings.append(f"Optional parameter '{param_name}' not found in execute function signature")
        
        # Check for extra function arguments
        param_names = set(parameters.keys())
        for arg_name in func_args:
            if arg_name not in param_names:
                warnings.append(f"Function argument '{arg_name}' not declared in parameters")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_code_syntax(self, code: str) -> ValidationResult:
        """Quick syntax validation for code."""
        errors = []
        warnings = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)