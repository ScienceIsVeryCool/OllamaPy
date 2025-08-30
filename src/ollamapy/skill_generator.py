"""Automated skill generation system using AI with multi-step prompts and safe execution."""

import json
import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

from .ai_query import AIQuery
from .ollama_client import OllamaClient
from .skills import Skill, SkillRegistry
from .analysis_engine import AnalysisEngine


@dataclass
class SkillPlan:
    """A plan for generating a skill, created step by step."""
    idea: str = ""
    name: str = ""
    description: str = ""
    role: str = ""
    vibe_test_phrases: Optional[List[str]] = None
    parameters: Optional[Dict[str, Dict[str, Any]]] = None
    function_code: str = ""
    
    def __post_init__(self):
        if self.vibe_test_phrases is None:
            self.vibe_test_phrases = []
        if self.parameters is None:
            self.parameters = {}


@dataclass
class SkillGenerationResult:
    """Result of a skill generation attempt."""
    success: bool
    skill: Optional[Skill]
    plan: Optional[SkillPlan]
    step_results: Dict[str, bool]
    errors: List[str]
    generation_time: float
    attempts: int
    vibe_test_passed: bool = False
    vibe_test_results: Optional[Dict[str, Any]] = None


class SafeCodeExecutor:
    """Safely executes generated code in isolation."""
    
    def __init__(self):
        self.timeout_seconds = 10
        self.allowed_imports = ['math', 'json', 'datetime', 'os', 're', 'random']
        
    def test_code_safely(self, function_code: str, test_params: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Test generated code safely without crashing the main process.
        
        Args:
            function_code: The Python function code to test
            test_params: Optional parameters to test with
            
        Returns:
            Tuple of (success, output_or_error)
        """
        # Create a test script
        # Properly indent the function code
        indented_code = '\n'.join('    ' + line if line.strip() else line for line in function_code.split('\n'))
        
        test_script = f"""
import json
import sys
import traceback

# Mock the log function
logged_messages = []
def log(message):
    logged_messages.append(str(message))

# Allow basic imports only
allowed_imports = {self.allowed_imports}

try:
    # The generated function code
{indented_code}
    
    # Test if execute function exists and is callable
    if 'execute' not in locals():
        print("ERROR: No 'execute' function found")
        sys.exit(1)
    
    if not callable(execute):
        print("ERROR: 'execute' is not callable")
        sys.exit(1)
    
    # Try calling the function with test parameters
    test_params = {test_params or {}}
    if test_params:
        result = execute(**test_params)
    else:
        result = execute()
    
    # Output the logged messages
    print("SUCCESS")
    for msg in logged_messages:
        print(f"LOG: {{msg}}")
        
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    traceback.print_exc()
    sys.exit(1)
"""
        
        # Write to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_file = f.name
        
        try:
            # Run the test script in isolation
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            
            output = result.stdout.strip()
            
            if result.returncode == 0 and output.startswith("SUCCESS"):
                return True, output
            else:
                error_output = result.stderr if result.stderr else result.stdout
                return False, f"Code execution failed: {error_output}"
                
        except subprocess.TimeoutExpired:
            return False, f"Code execution timed out after {self.timeout_seconds} seconds"
        except Exception as e:
            return False, f"Failed to test code: {str(e)}"
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass


class IncrementalSkillGenerator:
    """Generates skills using multiple focused AI prompts."""
    
    def __init__(self, model: str = "gemma3:4b", analysis_model: Optional[str] = None):
        """Initialize the incremental skill generator."""
        self.model = model
        self.analysis_model = analysis_model or model
        self.client = OllamaClient()
        self.ai_query = AIQuery(self.client, model)
        self.skill_registry = SkillRegistry()
        self.code_executor = SafeCodeExecutor()
        
    def generate_skill_idea(self) -> str:
        """Step 1: Generate a focused skill idea."""
        prompt = """Generate ONE specific, useful skill idea for an AI assistant.

Think of a practical task that users commonly need help with. Be specific and focused.

Examples of good ideas:
- "Convert text between different cases (uppercase, lowercase, title case)"
- "Calculate compound interest with various compounding periods"
- "Extract email addresses from text"
- "Generate random passwords with specific criteria"

Respond with just the skill idea in one clear sentence. Be specific about what it does."""

        result = self.ai_query.open(prompt)
        return result.content.strip()
    
    def generate_skill_name(self, idea: str) -> str:
        """Step 2: Generate a skill name from the idea."""
        prompt = f"""Based on this skill idea: "{idea}"

Generate a good function name for this skill.

Rules:
- Use only lowercase letters, numbers, and underscores
- Be descriptive but concise
- Follow Python naming conventions
- Should be 2-4 words joined by underscores

Examples:
- "convert_text_case"
- "calculate_compound_interest"
- "extract_emails"
- "generate_password"

Respond with ONLY the function name, nothing else."""

        result = self.ai_query.single_word(
            question=f"What should the function name be for this skill: {idea}?"
        )
        return result.word
    
    def generate_skill_description(self, idea: str) -> str:
        """Step 3: Generate a clear skill description."""
        prompt = f"""Based on this skill idea: "{idea}"

Write a clear, concise description of when this skill should be used.

The description should:
- Be 10-50 words
- Explain WHEN to use this skill
- Be specific about what it does
- Use simple, clear language

Example: "Use when the user wants to convert text between different cases like uppercase, lowercase, or title case"

Respond with ONLY the description, nothing else."""

        result = self.ai_query.open(prompt)
        return result.content.strip().strip('"').strip("'")
    
    def generate_skill_role(self, idea: str) -> str:
        """Step 4: Determine the skill's role category."""
        prompt = f"""Based on this skill idea: "{idea}"

What category does this skill belong to?

Choose from these options:
A. text_processing
B. mathematics
C. data_analysis
D. file_operations
E. web_utilities
F. time_date
G. formatting
H. validation
I. general

Respond with ONLY the letter (A, B, C, etc.)"""

        result = self.ai_query.multiple_choice(
            question="What category does this skill belong to?",
            options=[
                "text_processing", "mathematics", "data_analysis", "file_operations",
                "web_utilities", "time_date", "formatting", "validation", "general"
            ]
        )
        return result.value
    
    def generate_vibe_test_phrases(self, idea: str, name: str) -> List[str]:
        """Step 5: Generate vibe test phrases."""
        prompt = f"""Based on this skill: "{idea}" (function name: {name})

Generate 5 realistic things a user might say that should trigger this skill.

Make them natural, varied user requests. Think about different ways people might ask for the same thing.

Format as a simple numbered list:
1. First example
2. Second example  
3. Third example
4. Fourth example
5. Fifth example

Include the full list, nothing else."""

        result = self.ai_query.open(prompt)
        
        # Parse the numbered list
        phrases = []
        lines = result.content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number and clean up
                phrase = line.split('.', 1)[-1].strip()
                phrase = phrase.strip('-').strip()
                if phrase:
                    phrases.append(phrase)
        
        return phrases[:5]  # Ensure max 5 phrases
    
    def generate_parameters(self, idea: str, name: str) -> Dict[str, Dict[str, Any]]:
        """Step 6: Generate function parameters."""
        prompt = f"""Based on this skill: "{idea}" (function name: {name})

What input parameters does this function need?

If it needs parameters, respond in this EXACT JSON format:
{{"param_name": {{"type": "string", "description": "what this parameter is for", "required": true}}}}

If it needs NO parameters, respond with:
{{}}

Parameter types can only be: "string", "number", "boolean"

Examples:
- For text processing: {{"text": {{"type": "string", "description": "The text to process", "required": true}}}}
- For calculations: {{"amount": {{"type": "number", "description": "The amount to calculate", "required": true}}, "rate": {{"type": "number", "description": "The interest rate", "required": true}}}}
- For no parameters: {{}}

Respond with ONLY the JSON, nothing else."""

        result = self.ai_query.open(prompt)
        
        try:
            # Clean the response and parse JSON
            content = result.content.strip()
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0]
            elif content.startswith('```'):
                content = content.split('```')[1].split('```')[0]
            
            return json.loads(content)
        except:
            return {}  # Default to no parameters if parsing fails
    
    def generate_function_code(self, plan: SkillPlan) -> str:
        """Step 7: Generate the function code."""
        params_desc = ""
        if plan.parameters:
            param_list = []
            for name, spec in plan.parameters.items():
                param_type = spec.get('type', 'str')
                python_type = {'string': 'str', 'number': 'float', 'boolean': 'bool'}.get(param_type, 'str')
                required = spec.get('required', True)
                if required:
                    param_list.append(f"{name}: {python_type}")
                else:
                    param_list.append(f"{name}: {python_type} = None")
            params_desc = f"Parameters: {', '.join(param_list)}"
        else:
            params_desc = "No parameters required"

        prompt = f"""Write a Python function for this skill:

Idea: {plan.idea}
Function name: execute
Description: {plan.description}
{params_desc}

Requirements:
1. Function MUST be named 'execute'
2. Use log("message") to output results (log function is available)
3. Include error handling with try/except
4. Add descriptive log messages
5. Keep it simple and focused
6. No dangerous operations (no subprocess, eval, exec)
7. Only import: math, json, datetime, os, re, random

Write ONLY the function code, no explanations:"""

        result = self.ai_query.open(prompt)
        
        # Clean the response
        content = result.content.strip()
        if content.startswith('```python'):
            content = content.split('```python')[1].split('```')[0]
        elif content.startswith('```'):
            content = content.split('```')[1].split('```')[0]
        
        return content.strip()
    
    def build_skill_plan(self, idea: Optional[str] = None) -> SkillPlan:
        """Build a complete skill plan step by step."""
        plan = SkillPlan()
        
        try:
            # Step 1: Generate or use provided idea
            if idea:
                plan.idea = idea
                print(f"📝 Using provided idea: {idea}")
            else:
                print("🎯 Generating skill idea...")
                plan.idea = self.generate_skill_idea()
                print(f"💡 Generated idea: {plan.idea}")
            
            # Step 2: Generate name
            print("🔧 Generating skill name...")
            plan.name = self.generate_skill_name(plan.idea)
            print(f"📛 Name: {plan.name}")
            
            # Step 3: Generate description
            print("📝 Generating description...")
            plan.description = self.generate_skill_description(plan.idea)
            print(f"📋 Description: {plan.description}")
            
            # Step 4: Generate role
            print("🏷️ Determining role category...")
            plan.role = self.generate_skill_role(plan.idea)
            print(f"🎭 Role: {plan.role}")
            
            # Step 5: Generate vibe test phrases
            print("🧪 Generating vibe test phrases...")
            plan.vibe_test_phrases = self.generate_vibe_test_phrases(plan.idea, plan.name)
            print(f"💬 Generated {len(plan.vibe_test_phrases)} test phrases")
            
            # Step 6: Generate parameters
            print("⚙️ Generating parameters...")
            plan.parameters = self.generate_parameters(plan.idea, plan.name)
            param_count = len(plan.parameters)
            print(f"🔧 Parameters: {param_count} {'parameter' if param_count == 1 else 'parameters'}")
            
            # Step 7: Generate function code
            print("💻 Generating function code...")
            plan.function_code = self.generate_function_code(plan)
            print(f"✅ Generated {len(plan.function_code.splitlines())} lines of code")
            
            return plan
            
        except Exception as e:
            print(f"❌ Error building plan: {e}")
            raise
    
    def validate_and_test_plan(self, plan: SkillPlan) -> Tuple[bool, List[str]]:
        """Validate and safely test a skill plan."""
        errors = []
        
        # Basic validation
        if not plan.name or not plan.name.replace('_', '').isalnum():
            errors.append("Invalid skill name")
        
        if not plan.description or len(plan.description) < 10:
            errors.append("Description too short")
        
        if not plan.vibe_test_phrases or len(plan.vibe_test_phrases) < 3:
            errors.append("Need at least 3 vibe test phrases")
        
        if not plan.function_code or 'def execute' not in plan.function_code:
            errors.append("Function code missing or invalid")
        
        if errors:
            return False, errors
        
        # Test code safely
        print("🔒 Testing code safely...")
        success, output = self.code_executor.test_code_safely(plan.function_code, {})
        
        if not success:
            errors.append(f"Code execution failed: {output}")
            return False, errors
        
        print("✅ Code tested successfully")
        return True, []
    
    def run_isolated_vibe_test(self, skill: Skill) -> Tuple[bool, Dict[str, Any]]:
        """Run vibe test for a single skill."""
        print("🧪 Running vibe tests...")
        
        # Create analysis engine
        analysis_engine = AnalysisEngine(self.analysis_model, self.client)
        
        total_correct = 0
        total_tests = 0
        phrase_results = {}
        
        for phrase in skill.vibe_test_phrases[:3]:  # Test first 3 phrases
            correct = 0
            iterations = 2  # Keep it simple - 2 iterations per phrase
            
            for i in range(iterations):
                try:
                    prompt = f"""Should the '{skill.name}' skill be used for: "{phrase}"?
                    
Skill description: {skill.description}

Answer only 'yes' or 'no'."""
                    
                    response = analysis_engine.ask_yes_no_question(prompt)
                    if response:
                        correct += 1
                        total_correct += 1
                    total_tests += 1
                    
                except Exception as e:
                    print(f"⚠️ Vibe test error: {e}")
                    total_tests += 1
            
            success_rate = (correct / iterations) * 100 if iterations > 0 else 0
            phrase_results[phrase] = {
                'correct': correct,
                'total': iterations,
                'success_rate': success_rate
            }
            
            status = "✅" if success_rate >= 50 else "❌"
            print(f"  {status} '{phrase[:40]}...': {correct}/{iterations}")
        
        overall_success = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        passed = overall_success >= 50.0
        
        print(f"🎯 Overall vibe test: {total_correct}/{total_tests} ({overall_success:.0f}%)")
        
        return passed, {
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success,
            'phrase_results': phrase_results
        }
    
    def generate_skill(self, idea: Optional[str] = None, max_attempts: int = 3) -> SkillGenerationResult:
        """Generate a complete skill using the incremental approach."""
        import time
        start_time = time.time()
        
        step_results = {
            'plan_created': False,
            'validation_passed': False,
            'skill_registered': False,
            'vibe_test_passed': False
        }
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🚀 Generation attempt {attempt}/{max_attempts}")
            print("=" * 50)
            
            try:
                # Build the skill plan
                plan = self.build_skill_plan(idea)
                step_results['plan_created'] = True
                
                # Validate and test the plan
                valid, errors = self.validate_and_test_plan(plan)
                if not valid:
                    print(f"❌ Validation failed: {errors}")
                    if attempt == max_attempts:
                        return SkillGenerationResult(
                            success=False,
                            skill=None,
                            plan=plan,
                            step_results=step_results,
                            errors=errors,
                            generation_time=time.time() - start_time,
                            attempts=attempt
                        )
                    continue
                
                step_results['validation_passed'] = True
                
                # Create and register the skill
                skill = Skill(
                    name=plan.name,
                    description=plan.description,
                    vibe_test_phrases=plan.vibe_test_phrases or [],
                    parameters=plan.parameters or {},
                    function_code=plan.function_code,
                    verified=False,
                    scope="local",
                    role=plan.role
                )
                
                # Try to register safely
                try:
                    success = self.skill_registry.register_skill(skill)
                    if not success:
                        raise Exception("Failed to register skill")
                    step_results['skill_registered'] = True
                    print(f"✅ Skill '{skill.name}' registered successfully")
                except Exception as e:
                    print(f"❌ Registration failed: {e}")
                    continue
                
                # Run vibe tests
                vibe_passed, vibe_results = self.run_isolated_vibe_test(skill)
                step_results['vibe_test_passed'] = vibe_passed
                
                generation_time = time.time() - start_time
                
                return SkillGenerationResult(
                    success=True,
                    skill=skill,
                    plan=plan,
                    step_results=step_results,
                    errors=[],
                    generation_time=generation_time,
                    attempts=attempt,
                    vibe_test_passed=vibe_passed,
                    vibe_test_results=vibe_results
                )
                
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    return SkillGenerationResult(
                        success=False,
                        skill=None,
                        plan=None,
                        step_results=step_results,
                        errors=[f"Generation failed: {str(e)}"],
                        generation_time=time.time() - start_time,
                        attempts=attempt
                    )
        
        # Should not reach here
        return SkillGenerationResult(
            success=False,
            skill=None,
            plan=None,
            step_results=step_results,
            errors=["Max attempts exceeded"],
            generation_time=time.time() - start_time,
            attempts=max_attempts
        )


def run_skill_generation(model: str = "gemma3:4b", analysis_model: Optional[str] = None, 
                        count: int = 1, ideas: Optional[List[str]] = None) -> bool:
    """Main entry point for incremental skill generation."""
    print("🤖 OllamaPy Incremental Skill Generation")
    print("=" * 60)
    print(f"Generation model: {model}")
    print(f"Analysis model: {analysis_model or model}")
    print(f"Target count: {count}")
    print()
    
    generator = IncrementalSkillGenerator(model, analysis_model)
    
    successful_skills = []
    failed_attempts = []
    
    for i in range(count):
        print(f"\n🎯 Generating skill {i+1}/{count}")
        print("=" * 40)
        
        idea = ideas[i] if ideas and i < len(ideas) else None
        result = generator.generate_skill(idea, max_attempts=3)
        
        if result.success and result.skill:
            successful_skills.append(result.skill)
            status = "✅" if result.vibe_test_passed else "⚠️"
            print(f"\n{status} SUCCESS: {result.skill.name}")
            print(f"   Description: {result.skill.description}")
            print(f"   Role: {result.skill.role}")
            print(f"   Vibe test: {'PASSED' if result.vibe_test_passed else 'FAILED'}")
            print(f"   Time: {result.generation_time:.1f}s, Attempts: {result.attempts}")
        else:
            failed_attempts.append(result)
            print(f"\n❌ FAILED after {result.attempts} attempts")
            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")
    
    # Summary
    print(f"\n📊 Generation Complete!")
    print("=" * 40)
    print(f"✅ Successful: {len(successful_skills)}/{count}")
    print(f"❌ Failed: {len(failed_attempts)}/{count}")
    
    if successful_skills:
        print(f"\n🎉 Generated Skills:")
        for skill in successful_skills:
            print(f"  • {skill.name}: {skill.description}")
        return True
    else:
        print(f"\n😞 No skills were successfully generated")
        return False