"""Vercel entrypoint for the FastAPI application."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app
