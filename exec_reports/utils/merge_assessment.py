"""
Utility functions for merging candidate data with assessment data.

This module provides functions to combine core candidate information
(employment history, education, etc.) with assessment data (ratings,
skill assessments, commentary) for shortlist reports.
"""

import json
from pathlib import Path
from typing import Dict, Any


def merge_candidate_with_assessment(
    candidate_data: Dict[str, Any],
    assessment_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge candidate data with their assessment data.

    Args:
        candidate_data: Dictionary containing candidate information
        assessment_data: Dictionary containing assessment ratings and commentary

    Returns:
        Merged dictionary containing all candidate and assessment fields
    """
    # Start with all candidate data
    merged = candidate_data.copy()

    # Add assessment data (excluding full_name to avoid duplication)
    for key, value in assessment_data.items():
        if key != "full_name":
            merged[key] = value

    return merged


def load_and_merge_files(
    candidate_file_path: str,
    assessment_file_path: str
) -> Dict[str, Any]:
    """
    Load candidate and assessment JSON files and merge them.

    Args:
        candidate_file_path: Path to candidate JSON file
        assessment_file_path: Path to assessment JSON file

    Returns:
        Merged dictionary containing all data

    Raises:
        FileNotFoundError: If either file doesn't exist
        json.JSONDecodeError: If either file contains invalid JSON
    """
    candidate_path = Path(candidate_file_path)
    assessment_path = Path(assessment_file_path)

    # Load candidate data
    with open(candidate_path, 'r', encoding='utf-8') as f:
        candidate_data = json.load(f)

    # Load assessment data
    with open(assessment_path, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)

    # Merge and return
    return merge_candidate_with_assessment(candidate_data, assessment_data)


def save_merged_candidate_assessment(
    candidate_file_path: str,
    assessment_file_path: str,
    output_path: str
) -> Dict[str, Any]:
    """
    Load, merge, and save candidate and assessment data to a new file.

    Args:
        candidate_file_path: Path to candidate JSON file
        assessment_file_path: Path to assessment JSON file
        output_path: Path where merged JSON should be saved

    Returns:
        Dictionary with success status and details:
        {
            "success": bool,
            "output_file": str,
            "message": str
        }
    """
    try:
        # Load and merge
        merged_data = load_and_merge_files(candidate_file_path, assessment_file_path)

        # Save to output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "output_file": str(output_file),
            "message": f"Successfully merged candidate and assessment data"
        }

    except FileNotFoundError as e:
        return {
            "success": False,
            "output_file": "",
            "message": f"File not found: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "output_file": "",
            "message": f"Invalid JSON in file: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "output_file": "",
            "message": f"Error merging files: {str(e)}"
        }


if __name__ == "__main__":
    # Example usage
    print("merge_assessment.py - Utility for merging candidate and assessment data")
    print("\nThis module provides functions to:")
    print("1. merge_candidate_with_assessment() - Merge two dictionaries")
    print("2. load_and_merge_files() - Load and merge JSON files")
    print("3. save_merged_candidate_assessment() - Load, merge, and save to new file")
