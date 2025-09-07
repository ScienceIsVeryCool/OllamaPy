# Testing

OllamaPy includes comprehensive testing through the vibe test framework.

## Vibe Tests

Vibe tests evaluate AI model consistency and performance:

```bash
# Basic vibe tests
ollamapy --vibetest

# Multi-model comparison
ollamapy --multi-model-vibetest

# Specific iterations
ollamapy --vibetest -n 10
```

## Test Categories

- **Skill Activation**: Tests whether AI correctly identifies when to use skills
- **Parameter Extraction**: Tests parameter parsing accuracy
- **Consistency**: Tests repeatability of AI decisions
- **Performance**: Tests response times and efficiency

## Interpreting Results

- **Success Rate**: Percentage of correct decisions
- **Consistency Score**: Reliability of behavior
- **Timing**: Average response times
- **Model Comparison**: Performance across different models