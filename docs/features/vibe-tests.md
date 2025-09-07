# Vibe Tests

## AI Consistency & Performance Analysis

Vibe tests evaluate the consistency and reliability of AI models by testing their ability to correctly identify when to use various skills. Each test presents the AI with prompts that should or shouldn't trigger specific skills, measuring accuracy and response time.

### Latest Test Results

The results below are automatically generated from the most recent vibe test run. They show performance metrics across different models and test scenarios.

<div style="width: 100%; height: 1200px; border: none; border-radius: 8px; overflow: hidden;">
    <iframe src="../vibe_test_results.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

### Understanding the Metrics

- **Success Rate**: Percentage of correct skill activation decisions
- **Response Time**: Average time for the model to analyze and respond
- **Consistency Score**: How reliably the model makes the same decision
- **Model Comparison**: Side-by-side performance across different models

### Running Vibe Tests Locally

To generate your own vibe test results:

```bash
# Run vibe tests with default settings
ollamapy --vibetest

# Run comprehensive multi-model tests
ollamapy --multi-model-vibetest

# Specify iterations for more thorough testing
ollamapy --vibetest -n 10
```

The results will be automatically integrated into your local documentation.

### Test Categories

Vibe tests are organized into several categories:

#### Skill Activation Tests
Tests whether the AI correctly identifies when to activate a specific skill based on user input.

#### Parameter Extraction Tests
Tests whether the AI correctly extracts required parameters for skill execution.

#### Context Sensitivity Tests
Tests whether the AI responds appropriately to contextual cues in conversations.

#### Edge Case Tests
Tests model behavior with ambiguous, conflicting, or unusual inputs.

### Interpreting Results

#### Success Rates
- **90-100%**: Excellent performance, reliable for production use
- **80-89%**: Good performance, minor inconsistencies
- **70-79%**: Fair performance, may need refinement
- **Below 70%**: Poor performance, requires attention

#### Response Times
- **< 2 seconds**: Fast response, good user experience
- **2-5 seconds**: Moderate response time
- **> 5 seconds**: Slow response, may impact usability

#### Consistency Scores
- **90-100**: Highly consistent behavior
- **80-89**: Mostly consistent with occasional variations
- **70-79**: Moderate consistency
- **Below 70**: Inconsistent behavior