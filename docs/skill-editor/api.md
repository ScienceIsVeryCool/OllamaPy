# Skill Editor API Reference

The Skill Editor provides REST API endpoints for programmatic skill management.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently no authentication required for local development.

## Endpoints

### GET /skills
List all available skills.

**Response**:
```json
{
  "skills": [
    {
      "name": "weather",
      "description": "Get weather information",
      "version": "1.0.0"
    }
  ]
}
```

### GET /skills/{skill_name}
Get detailed information about a specific skill.

**Parameters**:
- `skill_name`: Name of the skill

**Response**:
```json
{
  "name": "weather",
  "description": "Get weather information", 
  "triggers": ["weather", "temperature"],
  "parameters": {...},
  "action": {...}
}
```

### POST /skills
Create a new skill.

**Request Body**:
```json
{
  "name": "my_skill",
  "description": "My custom skill",
  "triggers": ["trigger_phrase"],
  "parameters": {...},
  "action": {...}
}
```

### PUT /skills/{skill_name}
Update an existing skill.

### DELETE /skills/{skill_name}  
Delete a skill.

### POST /skills/{skill_name}/test
Test a skill with sample input.

**Request Body**:
```json
{
  "input": "What's the weather like?",
  "context": {...}
}
```

## Error Responses

All errors return appropriate HTTP status codes with error details:

```json
{
  "error": "Skill not found",
  "code": 404,
  "details": "The requested skill 'nonexistent' was not found"
}
```