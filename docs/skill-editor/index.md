# Interactive Skill Editor

The OllamaPy Skill Editor is a web-based interface for creating, editing, and testing AI skills interactively.

## Features

- **Visual Skill Creation**: Create skills using web forms
- **Real-time Validation**: Instant feedback on skill syntax and structure
- **Live Testing**: Test skills immediately after creation
- **Built-in Protection**: Built-in skills are protected from accidental modification
- **Export/Import**: Share skills as JSON files

## Getting Started

### Launch the Editor

```bash
# Install with editor support
pip install ollamapy[editor]

# Launch editor
ollamapy --skill-editor

# Custom port
ollamapy --skill-editor --port 9000
```

### Access the Interface

Open your browser to `http://localhost:8765` (or your custom port).

## Interface Overview

### Main Dashboard
- View all available skills
- See built-in vs custom skills
- Quick access to create new skills

### Skill Editor
- Form-based skill creation
- Syntax highlighting for Python code
- Parameter definition interface
- Vibe test phrase management

### Testing Interface
- Execute skills with test inputs
- View output and logs
- Validate skill behavior

## API Endpoints

The skill editor provides a REST API:

- `GET /api/skills` - List all skills
- `GET /api/skills/{name}` - Get specific skill
- `POST /api/skills` - Create new skill
- `PUT /api/skills/{name}` - Update skill
- `DELETE /api/skills/{name}` - Delete skill
- `POST /api/skills/validate` - Validate skill
- `POST /api/skills/test` - Test skill execution

## Next Steps

- [Getting Started Guide](getting-started.md)
- [API Reference](api.md)
- [Web Interface Guide](web-interface.md)