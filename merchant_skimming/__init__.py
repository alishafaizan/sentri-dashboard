# skimming_detection/__init__.py

"""
Digital Skimming Detection module for SENTRI+
Modular merchant-side skimming risk scoring.
"""

# def setup_logging():
#     import logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s %(levelname)s %(module)s %(message)s',
#         handlers=[
#             logging.FileHandler("audit.log"),
#             logging.StreamHandler()
#         ]
#     )

# Optionally, expose main CLI and pipeline functions for convenience
from .cli import main as cli_main
from .pipeline import run_pipeline