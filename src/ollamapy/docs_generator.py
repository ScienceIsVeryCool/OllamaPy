"""Unified documentation generator that orchestrates all doc generation tasks."""

import json
import subprocess
import shutil
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .vibe_test_runner import VribeTestRunner
from .skillgen_report import SkillDocumentationGenerator


class DocsConfig:
    """Configuration for documentation generation."""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize configuration with defaults."""
        config = config_dict or {}
        
        # Vibe test settings
        self.vibe_models = config.get("vibe_models", None)  # None means use config file
        self.vibe_iterations = config.get("vibe_iterations", 5)
        self.run_vibe_tests = config.get("run_vibe_tests", True)
        self.use_cached_vibe_tests = config.get("use_cached_vibe_tests", False)
        
        # Output settings
        self.output_dir = Path(config.get("output_dir", "./site"))
        self.docs_output_dir = Path(config.get("docs_output_dir", "./docs"))
        
        # Coverage settings
        self.with_coverage = config.get("with_coverage", False)
        self.coverage_command = config.get("coverage_command", "pytest --cov=ollamapy --cov-report=html")
        
        # MkDocs settings
        self.build_mkdocs = config.get("build_mkdocs", True)
        self.mkdocs_config = config.get("mkdocs_config", "mkdocs.yml")
        
        # Server settings
        self.serve = config.get("serve", False)
        self.serve_port = config.get("serve_port", 8000)
        
        # Component flags
        self.generate_skills_docs = config.get("generate_skills_docs", True)
        self.generate_vibe_showcase = config.get("generate_vibe_showcase", True)
        

class DocsGenerator:
    """Orchestrates all documentation generation tasks."""
    
    def __init__(self, config: Optional[DocsConfig] = None):
        """Initialize the documentation generator.
        
        Args:
            config: Configuration object for doc generation
        """
        self.config = config or DocsConfig()
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {}
        self.timestamp = datetime.now().isoformat()
        
        # Ensure output directories exist
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.docs_output_dir.mkdir(parents=True, exist_ok=True)
        
    def run_vibe_tests(self) -> Dict[str, Any]:
        """Run or load vibe tests.
        
        Returns:
            Vibe test results
        """
        print("\n" + "=" * 80)
        print("📊 VIBE TESTS")
        print("=" * 80)
        
        vibe_results_path = self.config.docs_output_dir / "vibe_test_results.json"
        
        if self.config.use_cached_vibe_tests and vibe_results_path.exists():
            print("📂 Using cached vibe test results...")
            with open(vibe_results_path, "r") as f:
                return json.load(f)
                
        if not self.config.run_vibe_tests:
            print("⏭️ Skipping vibe tests (disabled in config)")
            return {}
            
        print(f"🧪 Running vibe tests...")
        print(f"   Models: {self.config.vibe_models or 'from config file'}")
        print(f"   Iterations: {self.config.vibe_iterations}")
        
        # Create vibe test runner
        runner = VribeTestRunner(
            models=self.config.vibe_models,
            output_dir=str(self.config.docs_output_dir)
        )
        
        # Run tests with progress callback
        def progress_callback(current, total, model_name):
            print(f"   [{current}/{total}] Testing {model_name}...")
            
        results = runner.run_all_models(
            iterations=self.config.vibe_iterations,
            progress_callback=progress_callback
        )
        
        # Save results
        runner.save_results(str(vibe_results_path))
        
        # Get formatted results for docs
        return runner.get_results_for_docs()
        
    def generate_skills_documentation(self, vibe_results: Dict[str, Any]) -> bool:
        """Generate skills documentation.
        
        Args:
            vibe_results: Results from vibe tests to integrate
            
        Returns:
            True if successful
        """
        print("\n" + "=" * 80)
        print("📚 SKILLS DOCUMENTATION")
        print("=" * 80)
        
        if not self.config.generate_skills_docs:
            print("⏭️ Skipping skills documentation (disabled in config)")
            return True
            
        try:
            print("📝 Generating skills documentation...")
            
            # Create documentation generator
            generator = SkillDocumentationGenerator()
            
            # Generate markdown documentation
            md_output = self.config.docs_output_dir / "skills.md"
            print(f"   Creating Markdown: {md_output}")
            generator.generate_markdown_documentation(str(md_output))
            
            # Generate HTML documentation with vibe test results
            html_output = self.config.docs_output_dir / "skills.html"
            print(f"   Creating HTML: {html_output}")
            
            # Pass vibe results to HTML generation
            generator.generate_html_documentation(
                str(html_output),
                vibe_results=vibe_results
            )
            
            print("✅ Skills documentation generated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error generating skills documentation: {e}")
            return False
            
    def generate_vibe_showcase(self) -> bool:
        """Generate vibe test showcase HTML.
        
        Returns:
            True if successful
        """
        print("\n" + "=" * 80)
        print("🎨 VIBE TEST SHOWCASE")
        print("=" * 80)
        
        if not self.config.generate_vibe_showcase:
            print("⏭️ Skipping vibe showcase (disabled in config)")
            return True
            
        try:
            print("🎨 Generating vibe test showcase...")
            
            # Import and run the showcase generator
            from scripts.generate_vibe_test_showcase import generate_showcase
            
            # Generate showcase
            showcase_path = self.config.docs_output_dir / "vibe_tests.html"
            results_path = self.config.docs_output_dir / "vibe_test_results.json"
            
            if not results_path.exists():
                print("⚠️ No vibe test results found, skipping showcase")
                return True
                
            success = generate_showcase(
                results_file=str(results_path),
                output_file=str(showcase_path)
            )
            
            if success:
                print(f"✅ Vibe showcase generated: {showcase_path}")
            else:
                print("❌ Failed to generate vibe showcase")
                
            return success
            
        except ImportError:
            # Try running as subprocess if import fails
            print("   Running showcase generator as subprocess...")
            script_path = self.project_root / "scripts" / "generate_vibe_test_showcase.py"
            
            if not script_path.exists():
                print(f"❌ Showcase generator script not found: {script_path}")
                return False
                
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Vibe showcase generated successfully")
                return True
            else:
                print(f"❌ Error generating showcase: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating vibe showcase: {e}")
            return False
            
    def generate_skills_showcase(self) -> bool:
        """Generate skills showcase HTML.
        
        Returns:
            True if successful
        """
        print("\n" + "=" * 80)
        print("🎯 SKILLS SHOWCASE")
        print("=" * 80)
        
        try:
            print("🎯 Generating skills showcase...")
            
            # Try to import the module first
            try:
                from scripts.generate_skills_showcase import generate_showcase
                
                showcase_path = self.config.docs_output_dir / "skills_showcase.html"
                success = generate_showcase(output_file=str(showcase_path))
                
                if success:
                    print(f"✅ Skills showcase generated: {showcase_path}")
                    return True
                    
            except ImportError:
                # Fall back to subprocess
                script_path = self.project_root / "scripts" / "generate_skills_showcase.py"
                
                if not script_path.exists():
                    print(f"⚠️ Skills showcase script not found: {script_path}")
                    return True  # Not critical, continue
                    
                result = subprocess.run(
                    ["python3", str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root)
                )
                
                if result.returncode == 0:
                    print("✅ Skills showcase generated successfully")
                    return True
                else:
                    print(f"⚠️ Error generating showcase: {result.stderr}")
                    return True  # Not critical
                    
        except Exception as e:
            print(f"⚠️ Error generating skills showcase: {e}")
            return True  # Not critical, continue
            
    def run_tests_with_coverage(self) -> bool:
        """Run tests with coverage if enabled.
        
        Returns:
            True if successful or skipped
        """
        print("\n" + "=" * 80)
        print("🧪 TEST COVERAGE")
        print("=" * 80)
        
        if not self.config.with_coverage:
            print("⏭️ Skipping coverage (disabled in config)")
            return True
            
        try:
            print(f"🧪 Running tests with coverage...")
            print(f"   Command: {self.config.coverage_command}")
            
            result = subprocess.run(
                self.config.coverage_command.split(),
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                print("✅ Tests passed with coverage")
                
                # Copy coverage report to output dir if it exists
                coverage_dir = self.project_root / "htmlcov"
                if coverage_dir.exists():
                    coverage_output = self.config.output_dir / "coverage"
                    shutil.copytree(coverage_dir, coverage_output, dirs_exist_ok=True)
                    print(f"   Coverage report copied to: {coverage_output}")
                    
                return True
            else:
                print(f"❌ Tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
            
    def build_mkdocs_site(self) -> bool:
        """Build MkDocs site if enabled.
        
        Returns:
            True if successful or skipped
        """
        print("\n" + "=" * 80)
        print("📖 MKDOCS BUILD")
        print("=" * 80)
        
        if not self.config.build_mkdocs:
            print("⏭️ Skipping MkDocs build (disabled in config)")
            return True
            
        try:
            print("📖 Building MkDocs site...")
            
            # Check if mkdocs.yml exists
            mkdocs_config_path = self.project_root / self.config.mkdocs_config
            if not mkdocs_config_path.exists():
                print(f"⚠️ MkDocs config not found: {mkdocs_config_path}")
                return True  # Not critical
                
            # Build the site
            result = subprocess.run(
                ["mkdocs", "build", "-f", str(mkdocs_config_path), 
                 "--site-dir", str(self.config.output_dir / "mkdocs")],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                print(f"✅ MkDocs site built: {self.config.output_dir / 'mkdocs'}")
                return True
            else:
                print(f"⚠️ MkDocs build warning: {result.stderr}")
                return True  # Not critical
                
        except FileNotFoundError:
            print("⚠️ MkDocs not installed, skipping site build")
            return True  # Not critical
        except Exception as e:
            print(f"⚠️ Error building MkDocs: {e}")
            return True  # Not critical
            
    def create_index_page(self) -> bool:
        """Create an index page linking to all generated documentation.
        
        Returns:
            True if successful
        """
        print("\n" + "=" * 80)
        print("🏠 INDEX PAGE")
        print("=" * 80)
        
        try:
            print("📄 Creating documentation index page...")
            
            index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OllamaPy Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        .docs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .doc-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 2px solid #e9ecef;
        }}
        .doc-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        .doc-card h3 {{
            color: #495057;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .doc-card p {{
            color: #6c757d;
            line-height: 1.6;
        }}
        .doc-card a {{
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .doc-card a:hover {{
            background: #764ba2;
        }}
        .meta {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            text-align: center;
        }}
        .status {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-left: 0.5rem;
        }}
        .status.available {{
            background: #d4edda;
            color: #155724;
        }}
        .status.not-available {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OllamaPy Documentation Hub</h1>
        
        <p style="font-size: 1.1rem; color: #495057; line-height: 1.8;">
            Welcome to the unified documentation for OllamaPy. All documentation has been 
            automatically generated and organized for easy access.
        </p>
        
        <div class="docs-grid">
"""
            
            # Add cards for each documentation type
            docs_items = [
                {
                    "title": "📚 Skills Documentation",
                    "description": "Comprehensive documentation of all available AI skills with examples and parameters.",
                    "file": "skills.html",
                    "alt_file": "skills.md"
                },
                {
                    "title": "🧪 Vibe Test Results",
                    "description": "Multi-model vibe test results showing consistency and performance across different models.",
                    "file": "vibe_tests.html",
                    "alt_file": "vibe_test_results.json"
                },
                {
                    "title": "🎯 Skills Showcase",
                    "description": "Interactive showcase of skill capabilities and demonstrations.",
                    "file": "skills_showcase.html",
                    "alt_file": None
                },
                {
                    "title": "📖 MkDocs Site",
                    "description": "Full project documentation built with MkDocs including guides and API reference.",
                    "file": "mkdocs/index.html",
                    "alt_file": None
                },
                {
                    "title": "📊 Test Coverage",
                    "description": "Code coverage report from test suite execution.",
                    "file": "coverage/index.html",
                    "alt_file": None
                }
            ]
            
            for item in docs_items:
                # Check if the file exists
                file_path = self.config.output_dir / item["file"]
                alt_path = self.config.docs_output_dir / item["file"] if item["file"] else None
                
                if alt_path and alt_path.exists():
                    file_path = alt_path
                elif item["alt_file"]:
                    alt_file_path = self.config.docs_output_dir / item["alt_file"]
                    if alt_file_path.exists():
                        file_path = alt_file_path
                        
                available = file_path.exists() if file_path else False
                status = "available" if available else "not-available"
                status_text = "Available" if available else "Not Generated"
                
                if available:
                    # Make path relative to index
                    if file_path.is_relative_to(self.config.output_dir):
                        link = file_path.relative_to(self.config.output_dir)
                    else:
                        # Copy to output dir
                        dest = self.config.output_dir / file_path.name
                        shutil.copy2(file_path, dest)
                        link = dest.name
                else:
                    link = "#"
                    
                index_content += f"""
            <div class="doc-card">
                <h3>{item['title']} <span class="status {status}">{status_text}</span></h3>
                <p>{item['description']}</p>
                {"<a href='" + str(link) + "'>View Documentation →</a>" if available else "<p style='color: #6c757d; font-style: italic;'>Not available</p>"}
            </div>
"""
            
            index_content += f"""
        </div>
        
        <div class="meta">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>OllamaPy v0.8.0 | <a href="https://github.com/yourusername/ollamapy" style="color: #667eea;">GitHub Repository</a></p>
        </div>
    </div>
</body>
</html>
"""
            
            index_path = self.config.output_dir / "index.html"
            with open(index_path, "w") as f:
                f.write(index_content)
                
            print(f"✅ Index page created: {index_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating index page: {e}")
            return False
            
    def serve_documentation(self):
        """Serve the generated documentation locally."""
        print("\n" + "=" * 80)
        print("🌐 DOCUMENTATION SERVER")
        print("=" * 80)
        
        # Create a handler class with the correct directory
        docs_directory = str(self.config.output_dir)
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=docs_directory, **kwargs)
                
        try:
            with socketserver.TCPServer(("", self.config.serve_port), Handler) as httpd:
                
                url = f"http://localhost:{self.config.serve_port}"
                print(f"📡 Serving documentation at: {url}")
                print(f"   Press Ctrl+C to stop the server")
                
                # Try to open browser
                try:
                    webbrowser.open(url)
                except:
                    pass
                    
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n✋ Server stopped")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            
    def generate_all(self) -> bool:
        """Generate all documentation.
        
        Returns:
            True if all critical components succeeded
        """
        print("\n" + "=" * 80)
        print("🚀 OLLAMAPY DOCUMENTATION GENERATOR")
        print("=" * 80)
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"📁 Docs directory: {self.config.docs_output_dir}")
        
        success = True
        
        # Run vibe tests
        vibe_results = {}
        if self.config.run_vibe_tests or self.config.use_cached_vibe_tests:
            vibe_results = self.run_vibe_tests()
            self.results["vibe_tests"] = vibe_results
            
        # Generate skills documentation
        if self.config.generate_skills_docs:
            if not self.generate_skills_documentation(vibe_results):
                success = False
                
        # Generate vibe showcase
        if self.config.generate_vibe_showcase and vibe_results:
            self.generate_vibe_showcase()
            
        # Generate skills showcase
        self.generate_skills_showcase()
        
        # Run tests with coverage
        if self.config.with_coverage:
            self.run_tests_with_coverage()
            
        # Build MkDocs
        if self.config.build_mkdocs:
            self.build_mkdocs_site()
            
        # Create index page
        self.create_index_page()
        
        # Copy docs to output (but don't overwrite our new index)
        print("\n📋 Copying documentation files to output directory...")
        for file in self.config.docs_output_dir.glob("*.html"):
            dest_file = self.config.output_dir / file.name
            # Don't overwrite our newly created index
            if file.name == "index.html" and dest_file.exists():
                # Skip copying the old index over our new one
                continue
            shutil.copy2(file, dest_file)
            print(f"   Copied: {file.name}")
            
        for file in self.config.docs_output_dir.glob("*.json"):
            shutil.copy2(file, self.config.output_dir / file.name)
            print(f"   Copied: {file.name}")
            
        print("\n" + "=" * 80)
        if success:
            print("✅ DOCUMENTATION GENERATION COMPLETE!")
        else:
            print("⚠️ DOCUMENTATION GENERATION COMPLETED WITH WARNINGS")
        print(f"📁 Output available at: {self.config.output_dir}")
        print("=" * 80)
        
        # Serve if requested
        if self.config.serve:
            self.serve_documentation()
            
        return success