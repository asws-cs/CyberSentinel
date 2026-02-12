"""
This file is intentionally kept separate to respect the project structure,
but with SQLModel, the schema definitions in `backend.schemas` also serve
as the database models.

We import them here to make them accessible via the `models` module path,
maintaining a conventional structure.
"""
from schemas import Scan, ScanResult, Report

# This makes the models available through `backend.database.models.Scan`, etc.
__all__ = ["Scan", "ScanResult", "Report"]
