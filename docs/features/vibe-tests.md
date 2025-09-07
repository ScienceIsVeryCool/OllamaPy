# Vibe Tests

## AI Consistency & Performance Analysis

Vibe tests evaluate the consistency and reliability of AI models by testing their ability to correctly identify when to use various skills. Each test presents the AI with prompts that should or shouldn't trigger specific skills, measuring accuracy and response time.

### Latest Test Results

The results below are automatically generated from the most recent vibe test run. They show performance metrics across different models and test scenarios.

<div id="vibe-test-container" style="width: 100%; height: 1200px; border: none; border-radius: 8px; overflow: hidden;">
    <iframe 
        id="vibe-test-iframe"
        src="../vibe_test_results.html" 
        width="100%" 
        height="100%" 
        style="border: none;"
        onload="handleIframeLoad()"
        onerror="showFallback()"
    ></iframe>
</div>

<div id="vibe-test-fallback" style="display: none; padding: 20px; border: 2px dashed #ccc; border-radius: 8px; text-align: center; background: #f9f9f9;">
    <h3>🔬 Vibe Test Results</h3>
    <p>Vibe test results are generated during the build process and will be available here once generated.</p>
    <div style="margin: 20px 0;">
        <strong>To view results:</strong>
        <ul style="list-style: none; padding: 0; margin: 10px 0;">
            <li>🏠 <strong>Locally:</strong> Run <code>ollamapy --unified-docs</code> to generate and serve</li>
            <li>🌐 <strong>Online:</strong> Visit the <a href="https://scienceisverycool.github.io/OllamaPy/" target="_blank">live documentation</a></li>
        </ul>
    </div>
    <p><em>Fresh vibe tests are automatically generated with each deployment to ensure accuracy.</em></p>
</div>

<script>
function handleIframeLoad() {
    const iframe = document.getElementById('vibe-test-iframe');
    const fallback = document.getElementById('vibe-test-fallback');
    
    // Check if iframe actually loaded content
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (iframeDoc.body.children.length === 0 || 
            iframeDoc.body.innerHTML.trim() === '') {
            showFallback();
        }
    } catch (e) {
        // Cross-origin restriction or other error - try to detect by checking if src exists
        fetch(iframe.src).then(response => {
            if (!response.ok) {
                showFallback();
            }
        }).catch(() => {
            showFallback();
        });
    }
}

function showFallback() {
    document.getElementById('vibe-test-container').style.display = 'none';
    document.getElementById('vibe-test-fallback').style.display = 'block';
}
</script>

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