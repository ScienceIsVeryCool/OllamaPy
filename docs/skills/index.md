# Skills System

The OllamaPy skills system allows the AI to perform specific tasks and respond to certain types of queries with specialized behavior.

## How Skills Work

Skills are Python functions that:
- Have an `execute()` function
- Include vibe test phrases for automatic matching
- Can accept parameters
- Have descriptions and metadata

## Built-in Skills

OllamaPy comes with several built-in skills:

- **fear**: Handles fear-related responses
- **happy**: Generates positive responses
- **creative**: Assists with creative tasks
- **technical**: Provides technical explanations

## Skill Structure

```python
def execute(param1=None, param2=None):
    """Skill execution function"""
    log(f"[SkillName] Executing with {param1}, {param2}")
    # Skill logic here
    return result
```

## Vibe Testing

Skills are automatically matched to conversations using "vibe test phrases":

```json
{
    "vibe_test_phrases": [
        "I'm scared",
        "I'm afraid",
        "that's frightening"
    ]
}
```

## Custom Skills

You can create custom skills using:

1. The [Skill Editor](../skill-editor/index.md) web interface
2. JSON files in `~/.ollamapy/skills/`
3. Python modules

## Next Steps

- [Create Custom Skills](custom.md)
- [Use the Skill Editor](../skill-editor/getting-started.md)