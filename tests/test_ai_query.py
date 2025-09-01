"""Test suite for the enhanced OllamaPy features."""

from src.ollamapy.ai_query import AIQuery
from src.ollamapy.ollama_client import OllamaClient


def test_enhanced_ollamapy():
    """Test the enhanced OllamaPy features"""

    # Initialize client and AI query interface
    client = OllamaClient()

    if not client.is_available():
        print("❌ Ollama server not available. Please start Ollama first.")
        return

    ai = AIQuery(client, model="gemma3:4b")

    print("🚀 Testing Enhanced OllamaPy with 4 Query Types\n")
    print("=" * 60)

    # Test 1: Multiple Choice Query
    print("\n📊 TEST 1: Multiple Choice Query")
    print("-" * 40)

    result = ai.multiple_choice(
        question="What's the best deployment strategy for a microservices application?",
        options=[
            "Blue-green deployment",
            "Rolling update",
            "Canary deployment",
            "Recreate deployment",
        ],
        context="We have a high-traffic e-commerce platform with 50+ microservices",
    )

    print(f"Question: What's the best deployment strategy?")
    print(f"Answer: {result.letter}. {result.value}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Context Compressed: {result.context_compressed}")

    # Test 2: Single Word Query
    print("\n📝 TEST 2: Single Word Query")
    print("-" * 40)

    result = ai.single_word(
        question="What programming language is most used in this project?",
        context="Files: app.py, main.py, test_utils.py, requirements.txt, Dockerfile",
    )

    print(f"Question: What programming language is most used?")
    print(f"Answer: {result.word}")
    print(f"Confidence: {result.confidence:.0%}")

    # Test 3: Open Response Query
    print("\n📰 TEST 3: Open Response Query")
    print("-" * 40)

    result = ai.open(
        prompt="Explain the benefits of using Docker containers",
        context="We're considering containerizing our Python web application",
    )

    print(f"Prompt: Explain the benefits of using Docker containers")
    print(f"Response Preview: {result.content[:200]}...")
    print(f"Response Length: {len(result.content)} characters")

    # Test 4: File Write Query
    print("\n📄 TEST 4: File Write Query")
    print("-" * 40)

    result = ai.file_write(
        requirements="Create a simple Python configuration file with database and API settings",
        context="Application uses PostgreSQL and connects to a REST API",
    )

    print(f"Requirements: Create a Python configuration file")
    print(f"Generated Content Preview:\n{result.content[:300]}...")
    print(f"Content Length: {len(result.content)} characters")

    # Test 5: Context Compression
    print("\n🗜️ TEST 5: Context Compression")
    print("-" * 40)

    large_context = "Lorem ipsum " * 2000  # Simulate large context

    result = ai.multiple_choice(
        question="Should we use compression?",
        options=["Yes", "No"],
        context=large_context,
        auto_compress=True,
    )

    print(f"Original Context Size: {len(large_context)} characters")
    print(f"Compression Applied: {result.context_compressed}")
    print(f"Compression Rounds: {result.compression_rounds}")
    print(f"Answer: {result.letter}. {result.value}")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    test_enhanced_ollamapy()
