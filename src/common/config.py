"""
This module contains configuration settings for the project, including paths to data files,
environment variables, and directories for caching and storing results.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# The project’s root directory (adjust if your environment requires a different reference).
_project_dir: Path = Path(__file__).resolve().parent.parent.parent

# Load environment variables from a .env file located in the project's root directory.
assert load_dotenv(dotenv_path=_project_dir / ".env"), "No .env file found in project root directory. See README."

# Retrieve the OpenAI API key and other tokens from environment variables.
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Define the data directory and related paths.
PROMPTS_DIR = _project_dir / "prompt_templates"

DATA_DIR: Path = _project_dir / "data"
DOCS_DIR: Path = DATA_DIR / "docs"
CASE_IDS_JSONL: Path = DATA_DIR / "ids.jsonl"
DOCS_TEXT_JSONL: Path = DATA_DIR / "documents.jsonl"
DOCS_PARSED_JSONL: Path = DATA_DIR / "documents_parsed.jsonl"
DOCS_LABELED_JSONL: Path = DATA_DIR / "documents_labeled.jsonl"
DOCS_AUGMENTED_JSONL: Path = DATA_DIR / "documents_augmented.jsonl"

# Define cache-related directories.
_cache_dir: Path = _project_dir / "cache"
SCRAPING_CACHE: Path = _cache_dir / "scraping_gzip"
GENERATION_CACHE: Path = _cache_dir / "generation_gzip"
