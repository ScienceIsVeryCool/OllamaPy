# Creating Skills

Learn how to create custom AI skills using the visual editor.

## Skill Components

Every skill consists of:

### 1. Metadata
- **Name**: Unique identifier for the skill
- **Description**: What the skill does
- **Version**: Skill version for tracking changes

### 2. Triggers
- **Activation Patterns**: Phrases that activate the skill
- **Context Rules**: When the skill should be available
- **Priority**: Skill priority when multiple skills match

### 3. Parameters
- **Required Parameters**: Data the skill must have
- **Optional Parameters**: Additional configuration
- **Validation Rules**: Parameter format requirements

### 4. Actions
- **Primary Action**: Main skill functionality
- **Error Handling**: What to do when things go wrong
- **Response Generation**: How to format results

## Example: Weather Skill

```json
{
  "name": "weather",
  "description": "Get current weather information",
  "triggers": [
    "weather",
    "temperature",
    "forecast"
  ],
  "parameters": {
    "location": {
      "type": "string",
      "required": true,
      "description": "Geographic location"
    }
  },
  "action": {
    "type": "api_call",
    "endpoint": "https://api.weather.com/current",
    "method": "GET"
  }
}
```

## Best Practices

1. **Clear Triggers**: Use specific, unambiguous activation phrases
2. **Robust Parameters**: Handle missing or invalid parameters gracefully  
3. **Error Handling**: Provide helpful error messages
4. **Testing**: Thoroughly test with various inputs
5. **Documentation**: Document your skill's behavior