#!/usr/bin/env python3
"""Setup script for OllamaPy."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
README_PATH = Path(__file__).parent / "README.md"
with open(README_PATH, encoding="utf-8") as f:
    long_description = f.read()

# Core requirements
install_requires = [
    "requests>=2.25.0",
    "plotly>=5.0.0",
]

# Optional skill editor requirements
extras_require = {
    "editor": [
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "werkzeug>=2.3.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "isort>=5.12.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "safety>=2.3.0",
        "pre-commit>=3.0.0",
    ],
}

# All extra requirements
extras_require["all"] = sum(extras_require.values(), [])

setup(
    name="ollamapy",
    version="0.8.1",
    author="The Lazy Artist",
    author_email="noreply@github.com",
    description="A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities, dynamic skill generation, and interactive skill editing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ScienceIsVeryCool/OllamaPy",
    project_urls={
        "Documentation": "https://scienceisverycoool.github.io/OllamaPy",
        "Source": "https://github.com/ScienceIsVeryCool/OllamaPy",
        "Tracker": "https://github.com/ScienceIsVeryCool/OllamaPy/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "ollamapy=ollamapy.main:main",
        ],
    },
    keywords=[
        "ai",
        "chat",
        "ollama",
        "llm",
        "chatbot",
        "skills",
        "meta-reasoning",
        "terminal",
        "cli",
    ],
    include_package_data=True,
    zip_safe=False,
)