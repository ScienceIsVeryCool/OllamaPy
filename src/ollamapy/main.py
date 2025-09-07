"""Main module with Ollama chat functionality."""

import argparse
import sys
from typing import Optional, List
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .chat_session import ChatSession
from .terminal_interface import TerminalInterface
from .ai_query import AIQuery


def hello():
    """Return a hello message."""
    return "Hello, World!"


def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"


def chat(
    model: str = "gemma3:4b",
    system: str = "You are a helpful assistant.",
    analysis_model: str = "gemma3:4b",
):
    """Start a chat session with Ollama.

    Args:
        model: The model to use for chat (default: gemma3:4b)
        system: Optional system message to set context
        analysis_model: Optional separate model for action analysis (defaults to main model)
    """
    # Create the components
    client = OllamaClient()
    model_manager = ModelManager(client)
    analysis_engine = AnalysisEngine(analysis_model, client)
    chat_session = ChatSession(model, client, system)
    ai_query = AIQuery(client, model=analysis_model)

    # Create and run the terminal interface
    terminal_interface = TerminalInterface(
        model_manager, analysis_engine, chat_session, ai_query
    )
    terminal_interface.run()


def run_vibe_tests(
    model: str = "gemma3:4b", iterations: int = 1, analysis_model: str = "gemma3:4b"
):
    """Run built-in vibe tests.

    Args:
        model: The model to use for testing (default: gemma3:4b)
        iterations: Number of iterations per test (default: 1)
        analysis_model: Optional separate model for action analysis (defaults to main model)
    """
    from .vibe_tests import run_vibe_tests as run_tests

    return run_tests(model=model, iterations=iterations, analysis_model=analysis_model)


def run_multi_model_vibe_tests(iterations: int = 5, output_path: str = None):
    """Run vibe tests across multiple configured models for comprehensive comparison.

    Args:
        iterations: Number of iterations per test (default: 5)
        output_path: Path to save detailed JSON results for GitHub Pages
    """
    from .multi_model_vibe_tests import run_multi_model_tests

    return run_multi_model_tests(iterations=iterations, output_path=output_path)


def run_skill_gen(
    model: str = "gemma3:4b",
    analysis_model: Optional[str] = None,
    count: int = 1,
    ideas: Optional[list] = None,
):
    """Run automated skill generation.

    Args:
        model: The model to use for generation (default: gemma3:4b)
        analysis_model: Optional model for vibe testing (defaults to main model)
        count: Number of skills to generate (default: 1)
        ideas: Optional list of specific skill ideas
    """
    from .skill_generator import run_skill_generation

    return run_skill_generation(
        model=model, analysis_model=analysis_model, count=count, ideas=ideas
    )


def run_skill_editor(port: int = 5000, skills_directory: Optional[str] = None):
    """Run the interactive skill editor server.

    Args:
        port: Port to run the server on (default: 5000)
        skills_directory: Directory containing skill files (default: auto-detect)
    """
    try:
        from .skill_editor.api import SkillEditorAPI
    except ImportError as e:
        print(f"❌ Error: Missing dependencies for skill editor.")
        print(f"Please install Flask and flask-cors:")
        print(f"  pip install flask flask-cors")
        return False

    api = SkillEditorAPI(skills_directory=skills_directory, port=port)
    api.run()
    return True


def run_unified_documentation():
    """
    Generate complete unified documentation including vibe tests.
    This creates the exact same experience locally as on GitHub Pages.
    """
    import subprocess
    from pathlib import Path
    
    print("🚀 Generating Unified Documentation")
    print("=" * 60)
    
    # Step 1: Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    print("📊 Step 1/4: Running vibe tests...")
    # Run vibe tests and generate both JSON and HTML
    try:
        from .multi_model_vibe_tests import run_multi_model_tests
        results = run_multi_model_tests(
            iterations=5,
            output_path="docs/vibe_test_results.json"
        )
        print("✅ Vibe tests complete")
    except Exception as e:
        print(f"⚠️ Vibe tests failed: {e}")
        print("   Continuing with documentation generation...")
    
    print("\n📚 Step 2/4: Generating skills documentation...")
    # Generate skills showcase if needed
    try:
        from .skills import SKILL_REGISTRY
        skills_data = SKILL_REGISTRY.export_skills()
        # Generate skills HTML if you have a function for it
        print("✅ Skills documentation complete")
    except Exception as e:
        print(f"⚠️ Skills documentation failed: {e}")
    
    print("\n🏗️ Step 3/4: Building MkDocs site...")
    # Build the MkDocs site
    try:
        result = subprocess.run(
            ["mkdocs", "build"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ MkDocs site built successfully")
        else:
            print(f"⚠️ MkDocs build warning: {result.stderr}")
    except FileNotFoundError:
        print("❌ MkDocs not installed. Install with: pip install mkdocs mkdocs-material")
        return False
    
    print("\n🌐 Step 4/4: Serving documentation locally...")
    print("=" * 60)
    print("📍 Documentation available at: http://localhost:8000")
    print("📍 This is identical to: https://scienceisverycool.github.io/OllamaPy/")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Serve the site
    try:
        subprocess.run(["mkdocs", "serve"])
        return True
    except KeyboardInterrupt:
        print("\n👋 Documentation server stopped")
        return True
    except Exception as e:
        print(f"❌ Error serving documentation: {e}")
        return False


def generate_documentation(
    vibe_models: Optional[List[str]] = None,
    vibe_iterations: int = 5,
    output_dir: str = "./site",
    docs_dir: str = "./docs",
    with_coverage: bool = False,
    use_cached_vibe_tests: bool = False,
    serve: bool = False,
    serve_port: int = 8000
):
    """Generate unified documentation for the project.
    
    Args:
        vibe_models: List of models to test (None = use config)
        vibe_iterations: Number of iterations per vibe test
        output_dir: Directory for generated site
        docs_dir: Directory for documentation artifacts
        with_coverage: Run tests with coverage
        use_cached_vibe_tests: Use existing vibe test results
        serve: Serve documentation after generation
        serve_port: Port for documentation server
    """
    from .docs_generator import DocsGenerator, DocsConfig
    
    # Create configuration
    config = DocsConfig({
        "vibe_models": vibe_models.split(",") if vibe_models and isinstance(vibe_models, str) else vibe_models,
        "vibe_iterations": vibe_iterations,
        "output_dir": output_dir,
        "docs_output_dir": docs_dir,
        "with_coverage": with_coverage,
        "use_cached_vibe_tests": use_cached_vibe_tests,
        "serve": serve,
        "serve_port": serve_port,
        "run_vibe_tests": not use_cached_vibe_tests,
        "generate_skills_docs": True,
        "generate_vibe_showcase": True,
        "build_mkdocs": True
    })
    
    # Create and run generator
    generator = DocsGenerator(config)
    return generator.generate_all()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OllamaPy v0.8.1 - Terminal chat interface for Ollama with AI skills system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollamapy                          # Start chat with default model (gemma3:4b)
  ollamapy --model llama3.2:3b      # Use a specific model
  ollamapy --analysis-model gemma2:2b --model llama3.2:7b  # Use small model for analysis, large for chat
  ollamapy --system "You are a helpful coding assistant"  # Set system message
  ollamapy --vibetest               # Run vibe tests with default settings
  ollamapy --vibetest -n 5          # Run vibe tests with 5 iterations each
  ollamapy --vibetest --model llama3.2:3b -n 3  # Custom model and iterations
  ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b  # Separate models for testing
  ollamapy --skillgen               # Generate a new skill automatically
  ollamapy --skillgen --count 5     # Generate 5 new skills
  ollamapy --skillgen --idea "analyze CSV data"  # Generate specific skill
  ollamapy --skillgen --count 3 --model llama3.2:7b  # Use specific model
  ollamapy --skill-editor           # Launch interactive skill editor web interface
  ollamapy --skill-editor --port 8080  # Use custom port for skill editor
  ollamapy --generate-docs          # Generate all documentation
  ollamapy --generate-docs --serve  # Generate and serve locally
  ollamapy --generate-docs --vibe-models "gemma2:2b,llama3.2:3b" # Test specific models
  ollamapy --generate-docs --use-cached-vibe-tests # Use cached results
        """,
    )

    parser.add_argument(
        "--model",
        "-m",
        default="gemma3:4b",
        help="Model to use for chat responses (default: gemma3:4b)",
    )

    parser.add_argument(
        "--analysis-model",
        "-a",
        help="Model to use for action analysis (defaults to main model if not specified). Use a smaller, faster model for better performance.",
    )

    parser.add_argument(
        "--system", "-s", help="System message to set context for the AI"
    )

    parser.add_argument(
        "--hello", action="store_true", help="Just print hello and exit (for testing)"
    )

    parser.add_argument(
        "--vibetest",
        action="store_true",
        help="Run built-in vibe tests to evaluate AI decision-making consistency",
    )

    parser.add_argument(
        "--multi-model-vibetest",
        action="store_true",
        help="Run vibe tests across multiple configured models for comprehensive comparison",
    )

    parser.add_argument(
        "--skillgen",
        action="store_true",
        help="Generate new skills automatically using AI",
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of skills to generate (default: 1, used with --skillgen)",
    )

    parser.add_argument(
        "--idea",
        "-i",
        action="append",
        help="Specific skill idea to generate (can be used multiple times)",
    )

    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations for vibe tests (default: 1)",
    )

    parser.add_argument(
        "--skill-editor",
        action="store_true",
        help="Launch interactive skill editor web interface",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=5000,
        help="Port for skill editor server (default: 5000)",
    )

    parser.add_argument(
        "--skills-dir",
        help="Directory containing skill files (auto-detected if not specified)",
    )
    
    # Documentation generation arguments
    parser.add_argument(
        "--generate-docs",
        action="store_true",
        help="Generate unified documentation including vibe tests, skills docs, and MkDocs site"
    )
    
    parser.add_argument(
        "--docs-output",
        default="./site",
        help="Output directory for generated documentation site (default: ./site)"
    )
    
    parser.add_argument(
        "--vibe-models",
        help="Comma-separated list of models for vibe testing (e.g., 'gemma2:2b,llama3.2:3b')"
    )
    
    parser.add_argument(
        "--vibe-iterations",
        type=int,
        default=5,
        help="Number of iterations for vibe tests in documentation (default: 5)"
    )
    
    parser.add_argument(
        "--use-cached-vibe-tests",
        action="store_true",
        help="Use cached vibe test results instead of running new tests"
    )
    
    parser.add_argument(
        "--with-coverage",
        action="store_true",
        help="Run tests with coverage reporting during documentation generation"
    )
    
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve generated documentation locally after building"
    )
    
    parser.add_argument(
        "--serve-port",
        type=int,
        default=8000,
        help="Port for documentation server (default: 8000)"
    )
    
    parser.add_argument(
        "--unified-docs",
        action="store_true",
        help="Generate and serve complete unified documentation (vibe tests + all docs)"
    )

    args = parser.parse_args()

    if args.hello:
        print(hello())
        print(greet("Python"))
    elif args.vibetest:
        success = run_vibe_tests(
            model=args.model,
            iterations=args.iterations,
            analysis_model=args.analysis_model,
        )
        sys.exit(0 if success else 1)
    elif args.multi_model_vibetest:
        # Save results to docs for GitHub Pages integration
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        output_path = project_root / "docs" / "vibe_test_results.json"

        success = run_multi_model_vibe_tests(
            iterations=args.iterations, output_path=str(output_path)
        )

        if success:
            print(f"🚀 Running vibe test showcase generator...")
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "python3",
                        str(
                            project_root / "scripts" / "generate_vibe_test_showcase.py"
                        ),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Vibe test showcase generated successfully!")
                else:
                    print(f"❌ Error generating showcase: {result.stderr}")
            except Exception as e:
                print(f"❌ Error running showcase generator: {e}")

        sys.exit(0 if success else 1)
    elif args.skillgen:
        analysis_model = args.analysis_model if args.analysis_model else args.model
        success = run_skill_gen(
            model=args.model,
            analysis_model=analysis_model,
            count=args.count,
            ideas=args.idea,
        )
        sys.exit(0 if success else 1)
    elif args.skill_editor:
        success = run_skill_editor(port=args.port, skills_directory=args.skills_dir)
        sys.exit(0 if success else 1)
    elif args.generate_docs:
        success = generate_documentation(
            vibe_models=args.vibe_models,
            vibe_iterations=args.vibe_iterations,
            output_dir=args.docs_output,
            docs_dir="./docs",
            with_coverage=args.with_coverage,
            use_cached_vibe_tests=args.use_cached_vibe_tests,
            serve=args.serve,
            serve_port=args.serve_port
        )
        sys.exit(0 if success else 1)
    elif args.unified_docs:
        success = run_unified_documentation()
        sys.exit(0 if success else 1)
    else:
        chat(
            model=args.model,
            system=args.system,
            analysis_model=args.analysis_model if args.analysis_model else "gemma3:4b",
        )


if __name__ == "__main__":
    main()
