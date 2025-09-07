# API Reference

OllamaPy provides several APIs for integration and extension.

## Core APIs

### Chat API
Programmatic interface for chat functionality.

```python
from ollamapy import ChatSession

session = ChatSession(model="gemma3:4b")
response = session.chat("Hello, world!")
```

### Skills API
Interface for managing and executing skills.

```python
from ollamapy.skills import SkillRegistry

registry = SkillRegistry()
skills = registry.list_skills()
```

### Analysis API
AI analysis and decision-making interface.

```python
from ollamapy import AnalysisEngine

engine = AnalysisEngine(model="gemma3:4b")
result = engine.analyze("What's the weather like?")
```

## REST APIs

### Skill Editor API
See [Skill Editor API Reference](../skill-editor/api.md) for REST endpoint documentation.

## Configuration API

### Model Configuration
Configure models for different purposes.

```python
from ollamapy import ModelManager

manager = ModelManager()
manager.set_chat_model("llama3.2:3b")  
manager.set_analysis_model("gemma2:2b")
```

### Skill Configuration
Configure skill behavior and parameters.

```python
skill_config = {
    "weather": {
        "enabled": True,
        "api_key": "your_key_here",
        "default_location": "London"
    }
}
```

## Integration Examples

### Custom Actions
Create custom skill actions:

```python
from ollamapy.skills import BaseAction

class CustomAction(BaseAction):
    def execute(self, parameters):
        # Your custom logic here
        return {"result": "success"}
```

### Event Handlers
React to chat events:

```python
def on_skill_activated(skill_name, parameters):
    print(f"Skill {skill_name} activated with {parameters}")

session.on("skill_activated", on_skill_activated)
```