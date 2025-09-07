# Getting Started with Skill Editor

The Skill Editor provides a visual interface for creating and managing AI skills.

## Prerequisites

- OllamaPy installed
- Flask dependencies: `pip install flask flask-cors`

## Starting the Skill Editor

```bash
ollamapy --skill-editor
```

The skill editor will start on `http://localhost:5000`.

## Creating Your First Skill

1. **Open the Editor**: Navigate to `http://localhost:5000`
2. **Click "New Skill"**: Start creating a new skill
3. **Define Triggers**: Set up phrases that activate the skill
4. **Configure Parameters**: Define what data the skill needs
5. **Set Actions**: Specify what the skill should do
6. **Test**: Use the built-in testing interface
7. **Save**: Export your skill to the skills directory

## Basic Workflow

1. **Plan**: Decide what your skill should accomplish
2. **Create**: Use the visual editor to build the skill
3. **Test**: Verify the skill works correctly
4. **Deploy**: Save the skill for use in chat sessions
5. **Monitor**: Use vibe tests to track performance