import os


def setup_output_path(output_path: str):
    """Setting up the output path (UNIX)"""
    os.makedirs(output_path, exist_ok=True)
