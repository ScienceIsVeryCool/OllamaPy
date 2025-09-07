# Skills Library

OllamaPy's skills system enables AI to automatically perform actions based on conversation context.

## Available Skills

### Weather
Get current weather information for any location.
- **Trigger**: "What's the weather like?"
- **Parameters**: Location (auto-detected or specified)

### Calculator  
Perform mathematical calculations and computations.
- **Trigger**: Mathematical expressions or "calculate"
- **Parameters**: Expression to evaluate

### File Operations
Create, read, edit, and manage files.
- **Trigger**: "create file", "read file", "save to file"
- **Parameters**: Filename, content, operation type

## Skill Development

Skills are defined using JSON configuration files with:
- Activation patterns
- Parameter extraction rules
- Action definitions
- Response templates

See the [Skill Editor](../skill-editor/index.md) for visual skill creation.