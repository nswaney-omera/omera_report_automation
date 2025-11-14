import json
import sys
import os
import glob
from datetime import datetime
from pathlib import Path

def get_json_files(folder_path):
    """
    Get metadata, candidate, and assessment JSON files from a folder, excluding merged files.

    Args:
        folder_path: Path to the folder containing JSON files

    Returns:
        tuple: (metadata_files, candidate_files, assessment_files) - lists of file paths
    """
    # Get all JSON files in the folder
    all_json_files = glob.glob(os.path.join(folder_path, "*.json"))

    # Separate metadata, candidate, and assessment files, excluding merged files
    metadata_files = [
        f for f in all_json_files
        if os.path.basename(f).startswith("metadata_")
    ]

    # Candidate files: NOT metadata, NOT merged, NOT assessment
    candidate_files = [
        f for f in all_json_files
        if not os.path.basename(f).startswith("metadata_")
        and not os.path.basename(f).startswith("merged_")
        and "_assessment_" not in os.path.basename(f)
        and not os.path.basename(f).endswith("_assessment.json")
    ]

    # Assessment files
    assessment_files = [
        f for f in all_json_files
        if "_assessment_" in os.path.basename(f) or os.path.basename(f).endswith("_assessment.json")
    ]

    return metadata_files, candidate_files, assessment_files

def extract_candidate_number(filepath):
    """
    Extract candidate number from filename for sorting.

    Args:
        filepath: Path to candidate file

    Returns:
        int: Candidate number or 999 if not found
    """
    try:
        # Extract number from filename like "candidate_1_..."
        basename = os.path.basename(filepath)
        parts = basename.split('_')
        if len(parts) >= 2 and parts[0] == 'candidate':
            return int(parts[1])
        return 999  # Put files without number at the end
    except:
        return 999

def find_assessment_for_candidate(candidate_file, assessment_files):
    """
    Find the matching assessment file for a candidate file based on name.

    Args:
        candidate_file: Path to candidate JSON file
        assessment_files: List of assessment JSON file paths

    Returns:
        str or None: Path to matching assessment file, or None if not found
    """
    candidate_basename = os.path.basename(candidate_file)
    # Extract the candidate name part (before timestamp)
    # Example: "John_Smith_20250124_143022.json" -> "John_Smith"
    parts = candidate_basename.replace('.json', '').split('_')

    # Find where the timestamp starts (8 digits for YYYYMMDD)
    candidate_name_parts = []
    for part in parts:
        if len(part) == 8 and part.isdigit():
            break
        candidate_name_parts.append(part)

    candidate_name = '_'.join(candidate_name_parts)

    # Look for assessment file with this candidate name
    for assessment_file in assessment_files:
        assessment_basename = os.path.basename(assessment_file)
        if candidate_name in assessment_basename and '_assessment_' in assessment_basename:
            return assessment_file

    return None


def merge_files(metadata_files, candidate_files, assessment_files):
    """
    Merge metadata, candidate, and assessment JSON files into a single JSON object.
    Metadata fields are added at root level (no prefix).
    Candidate fields get merged with their assessment data, then prefixed with c1_, c2_, c3_, etc.

    Args:
        metadata_files: List of metadata JSON filenames
        candidate_files: List of candidate JSON filenames
        assessment_files: List of assessment JSON filenames

    Returns:
        dict: Merged JSON object
    """
    merged_data = {}

    # Process metadata file (no prefix)
    if metadata_files:
        metadata_file = metadata_files[0]  # Use first/most recent metadata file
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                # Add metadata fields directly to merged_data (no prefix)
                merged_data.update(metadata)
        except Exception as e:
            raise Exception(f"Error processing metadata file {metadata_file}: {e}")

    # Sort candidate files by candidate number
    candidate_files.sort(key=extract_candidate_number)

    # Process candidate files with prefixes
    for i, filename in enumerate(candidate_files, 1):
        try:
            # Load candidate data
            with open(filename, 'r', encoding='utf-8') as f:
                candidate_data = json.load(f)

            # Find and merge assessment data if available
            assessment_file = find_assessment_for_candidate(filename, assessment_files)
            if assessment_file:
                try:
                    with open(assessment_file, 'r', encoding='utf-8') as f:
                        assessment_data = json.load(f)

                    # Merge assessment data into candidate data (excluding full_name to avoid duplication)
                    for key, value in assessment_data.items():
                        if key != "full_name":
                            candidate_data[key] = value
                except Exception as e:
                    # If assessment file exists but can't be read, warn but continue
                    print(f"Warning: Could not read assessment file {assessment_file}: {e}")

            # Add prefix to each field
            prefix = f"c{i}_"
            for key, value in candidate_data.items():
                prefixed_key = prefix + key
                merged_data[prefixed_key] = value

        except Exception as e:
            raise Exception(f"Error processing candidate file {filename}: {e}")

    return merged_data

def get_next_available_filename(folder_path, base_name):
    """
    Get the next available filename with incremental suffix if file exists.

    Args:
        folder_path: Directory where the file will be saved
        base_name: Base name for the output file (e.g., merged_candidates_CEO_Quantium_2025)

    Returns:
        str: Full path to the next available filename
    """
    # First, try the base name without suffix
    filename = os.path.join(folder_path, f"{base_name}.json")

    if not os.path.exists(filename):
        return filename

    # If it exists, try with _2, _3, etc.
    counter = 2
    while True:
        filename = os.path.join(folder_path, f"{base_name}_{counter}.json")
        if not os.path.exists(filename):
            return filename
        counter += 1

def merge_candidates_data(folder_name, base_path):
    """
    Merge metadata and candidate files from a folder into a single JSON file.
    This is the main function to be imported by other modules.

    Args:
        folder_name: Just the folder name (e.g., "CEO_Quantium_2025")
        base_path: Base path to data folder (shortlist_report_data or candidate_report_data)

    Returns:
        dict: Result dictionary with keys:
            - success (bool): Whether the operation succeeded
            - message (str): Success or error message
            - output_file (str): Path to the merged file (if successful)
            - num_candidates (int): Number of candidates merged (if successful)
            - candidate_files (list): List of candidate filenames merged (if successful)
    """
    try:
        # Construct full path
        folder_path = os.path.join(base_path, folder_name)
        folder_path = os.path.normpath(folder_path)

        # Check if folder exists
        if not os.path.exists(folder_path):
            return {
                "success": False,
                "message": f"Folder '{folder_path}' does not exist.",
                "output_file": None
            }

        if not os.path.isdir(folder_path):
            return {
                "success": False,
                "message": f"'{folder_path}' is not a directory.",
                "output_file": None
            }

        # Get metadata, candidate, and assessment files (excluding merged files)
        metadata_files, candidate_files, assessment_files = get_json_files(folder_path)

        # Check for required files
        if not metadata_files:
            return {
                "success": False,
                "message": "No metadata file found in folder. Please generate metadata first.",
                "output_file": None
            }

        if not candidate_files:
            return {
                "success": False,
                "message": "No candidate JSON files found in the folder. Please add candidates first.",
                "output_file": None
            }

        # Merge the files (assessment files are optional)
        merged_data = merge_files(metadata_files, candidate_files, assessment_files)

        if not merged_data:
            return {
                "success": False,
                "message": "No data was merged. Please check your input files.",
                "output_file": None
            }

        # Create base name for output file
        base_name = f"merged_candidates_{folder_name}"

        # Get the next available filename
        output_filename = get_next_available_filename(folder_path, base_name)

        # Save merged data
        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, indent=2, ensure_ascii=False)

        # Count candidates
        num_candidates = len([k for k in merged_data.keys() if k.endswith('_full_name') and k.startswith('c')])

        # Get list of candidate filenames for reporting
        candidate_filenames = [os.path.basename(f) for f in candidate_files]
        metadata_filename = os.path.basename(metadata_files[0])

        return {
            "success": True,
            "message": "Successfully merged data",
            "output_file": output_filename,
            "num_candidates": num_candidates,
            "total_fields": len(merged_data),
            "metadata_file": metadata_filename,
            "candidate_files": candidate_filenames
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error merging candidate files: {str(e)}",
            "output_file": None
        }
