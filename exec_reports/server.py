from fastmcp import FastMCP
import json
import os
from pathlib import Path
from utils.shortlist_data import ShortlistMetadata, UnifiedCandidateData, CandidateAssessment
from replace import process_document_template
from utils.merge_data import merge_candidates_data
from utils.table_edit import apply_table_colors
from utils.merge_doc import merge_shortlist_documents
from utils.table_merge import merge_duplicate_first_column_cells
from utils.mcp_logging import log_mcp_tool
from datetime import datetime
from utils.logging_db import _logger

import requests
import json
import socket
import getpass
from datetime import datetime

# Create the MCP server
mcp = FastMCP("Executive Reports Server")

# Base directory for exec_reports module
BASE_DIR = Path(__file__).parent.resolve()

# Data directory for all report types
DATA_DIR = BASE_DIR / "data"

# Template paths
SHORTLIST_OVERVIEW_TEMPLATE = BASE_DIR / "templates" / "s_overview.docx"
SHORTLIST_CANDIDATE_TEMPLATE = BASE_DIR / "templates" / "s_singular_candidate.docx"
SHORTLIST_END_PAGE = BASE_DIR / "templates" / "s_end_page.docx"
CANDIDATE_REPORT_TEMPLATE = BASE_DIR / "templates" / "c_template.docx"

# Output directory
OUTPUTS_DIR = BASE_DIR / "outputs"

# ============================================================================
# DATA CREATION TOOLS
# ============================================================================

@mcp.tool()
@log_mcp_tool
def generate_shortlist_metadata(
    client_company_name: str,
    candidate_target_role: str,
    client_1_full_name: str = "",
    client_1_position: str = "",
    client_2_full_name: str = "",
    client_2_position: str = "",
    client_3_full_name: str = "",
    client_3_position: str = "",
    consultant_1_name: str = "",
    consultant_1_position: str = "",
    consultant_2_name: str = "",
    consultant_2_position: str = "",
    consultant_3_name: str = "",
    consultant_3_position: str = "",
    role_skill_1: str = "",
    role_skill_2: str = "",
    role_skill_3: str = "",
    role_skill_4: str = "",
    role_skill_5: str = "",
    role_skill_6: str = "",
    role_skill_7: str = "",
    role_skill_8: str = "",
) -> str:
    """
    Generate shortlist metadata (client info, consultant team, and 8 role skills for assessment).

    CHARACTER ENCODING: Use ONLY standard ASCII characters (straight quotes ', regular hyphens -)
    AVOID: Curly quotes "", em-dashes —, smart apostrophes '

    Args:
        client_company_name: Client organization name (REQUIRED)
        candidate_target_role: Target position being filled (REQUIRED)
        role_skill_1 to role_skill_8: The 8 assessment skills (REQUIRED)
        client/consultant fields: Contact information (optional but recommended)

    Returns:
        Success message with file path
    """
    try:
        current_year = datetime.now().year
        clean_role = "".join(c for c in candidate_target_role if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        clean_company = "".join(c for c in client_company_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        folder_name = f"{clean_role}_{clean_company}_{current_year}"
        metadata_folder = DATA_DIR / folder_name

        shortlist_metadata = ShortlistMetadata(
            client_company_name=client_company_name,
            candidate_target_role=candidate_target_role,
            client_1_full_name=client_1_full_name,
            client_1_position=client_1_position,
            client_2_full_name=client_2_full_name,
            client_2_position=client_2_position,
            client_3_full_name=client_3_full_name,
            client_3_position=client_3_position,
            consultant_1_name=consultant_1_name,
            consultant_1_position=consultant_1_position,
            consultant_2_name=consultant_2_name,
            consultant_2_position=consultant_2_position,
            consultant_3_name=consultant_3_name,
            consultant_3_position=consultant_3_position,
            role_skill_1=role_skill_1,
            role_skill_2=role_skill_2,
            role_skill_3=role_skill_3,
            role_skill_4=role_skill_4,
            role_skill_5=role_skill_5,
            role_skill_6=role_skill_6,
            role_skill_7=role_skill_7,
            role_skill_8=role_skill_8,
        )

        data_dict = shortlist_metadata.model_dump()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metadata_filename = f"metadata_{clean_company}_{timestamp}.json"
        metadata_output_path = metadata_folder / metadata_filename

        metadata_folder.mkdir(parents=True, exist_ok=True)

        with open(metadata_output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)

        return f"""
Metadata saved: {metadata_output_path}

Project: {folder_name}
Role Skills: {role_skill_1}, {role_skill_2}, {role_skill_3}, {role_skill_4}, {role_skill_5}, {role_skill_6}, {role_skill_7}, {role_skill_8}
        """

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
@log_mcp_tool
def generate_individual_candidate(
    full_name: str,
    candidate_target_role: str,
    client_company_name: str,
    report_generation_date: str,
    candidate_number: int = 1,
    position: str = "",
    company: str = "",
    first_name: str = "",
    last_name: str = "",
    internal_or_blank: str = "",
    current_location: str = "",
    previous_salary: str = "",
    short_term_incentive: str = "",
    other_remuneration: str = "",
    notice_period: str = "",
    candidate_executive_summary: str = "",
    # Employment history (up to 7 positions)
    employment_1_company_name: str = "",
    employment_1_company_location: str = "",
    employment_1_location: str = "",
    employment_1_start_year: str = "",
    employment_1_end_year: str = "",
    employment_1_job_title: str = "",
    employment_1_start_date_full: str = "",
    employment_1_end_date_full: str = "",
    employment_1_date_range_full: str = "",
    employment_1_role_overview: str = "",
    employment_1_responsibility_primary: str = "",
    employment_1_responsibility_secondary: str = "",
    employment_1_achievement_primary: str = "",
    employment_1_achievement_secondary: str = "",
    employment_2_company_name: str = "",
    employment_2_company_location: str = "",
    employment_2_location: str = "",
    employment_2_start_year: str = "",
    employment_2_end_year: str = "",
    employment_2_job_title: str = "",
    employment_2_start_date_full: str = "",
    employment_2_end_date_full: str = "",
    employment_2_date_range_full: str = "",
    employment_2_role_overview: str = "",
    employment_2_responsibility_primary: str = "",
    employment_2_responsibility_secondary: str = "",
    employment_2_achievement_primary: str = "",
    employment_2_achievement_secondary: str = "",
    employment_3_company_name: str = "",
    employment_3_company_location: str = "",
    employment_3_location: str = "",
    employment_3_start_year: str = "",
    employment_3_end_year: str = "",
    employment_3_job_title: str = "",
    employment_3_start_date_full: str = "",
    employment_3_end_date_full: str = "",
    employment_3_date_range_full: str = "",
    employment_3_role_overview: str = "",
    employment_3_responsibility_primary: str = "",
    employment_3_responsibility_secondary: str = "",
    employment_3_achievement_primary: str = "",
    employment_3_achievement_secondary: str = "",
    employment_4_company_name: str = "",
    employment_4_company_location: str = "",
    employment_4_location: str = "",
    employment_4_start_year: str = "",
    employment_4_end_year: str = "",
    employment_4_job_title: str = "",
    employment_4_start_date_full: str = "",
    employment_4_end_date_full: str = "",
    employment_4_date_range_full: str = "",
    employment_4_role_overview: str = "",
    employment_4_responsibility_primary: str = "",
    employment_4_responsibility_secondary: str = "",
    employment_4_achievement_primary: str = "",
    employment_4_achievement_secondary: str = "",
    employment_5_company_name: str = "",
    employment_5_company_location: str = "",
    employment_5_location: str = "",
    employment_5_start_year: str = "",
    employment_5_end_year: str = "",
    employment_5_job_title: str = "",
    employment_5_start_date_full: str = "",
    employment_5_end_date_full: str = "",
    employment_5_date_range_full: str = "",
    employment_5_role_overview: str = "",
    employment_5_responsibility_primary: str = "",
    employment_5_responsibility_secondary: str = "",
    employment_5_achievement_primary: str = "",
    employment_5_achievement_secondary: str = "",
    employment_6_company_name: str = "",
    employment_6_company_location: str = "",
    employment_6_location: str = "",
    employment_6_start_year: str = "",
    employment_6_end_year: str = "",
    employment_6_job_title: str = "",
    employment_6_start_date_full: str = "",
    employment_6_end_date_full: str = "",
    employment_6_date_range_full: str = "",
    employment_6_role_overview: str = "",
    employment_6_responsibility_primary: str = "",
    employment_6_responsibility_secondary: str = "",
    employment_6_achievement_primary: str = "",
    employment_6_achievement_secondary: str = "",
    employment_7_company_name: str = "",
    employment_7_company_location: str = "",
    employment_7_location: str = "",
    employment_7_start_year: str = "",
    employment_7_end_year: str = "",
    employment_7_job_title: str = "",
    employment_7_start_date_full: str = "",
    employment_7_end_date_full: str = "",
    employment_7_date_range_full: str = "",
    employment_7_role_overview: str = "",
    employment_7_responsibility_primary: str = "",
    employment_7_responsibility_secondary: str = "",
    employment_7_achievement_primary: str = "",
    employment_7_achievement_secondary: str = "",
    # Directorships (up to 3)
    directorship_committee_1_name: str = "",
    directorship_committee_1_year_range: str = "",
    directorship_committee_1_position: str = "",
    directorship_committee_2_name: str = "",
    directorship_committee_2_year_range: str = "",
    directorship_committee_2_position: str = "",
    directorship_committee_3_name: str = "",
    directorship_committee_3_year_range: str = "",
    directorship_committee_3_position: str = "",
    # Education (up to 5)
    education_1_completion_year: str = "",
    education_1_qualification_name: str = "",
    education_1_institution_name: str = "",
    education_2_completion_year: str = "",
    education_2_qualification_name: str = "",
    education_2_institution_name: str = "",
    education_3_completion_year: str = "",
    education_3_qualification_name: str = "",
    education_3_institution_name: str = "",
    education_4_completion_year: str = "",
    education_4_qualification_name: str = "",
    education_4_institution_name: str = "",
    education_5_completion_year: str = "",
    education_5_qualification_name: str = "",
    education_5_institution_name: str = "",
    # Professional memberships (up to 5)
    professional_membership_1: str = "",
    professional_membership_2: str = "",
    professional_membership_3: str = "",
    professional_membership_4: str = "",
    professional_membership_5: str = "",
    # Professional development (up to 5)
    professional_development_1: str = "",
    professional_development_2: str = "",
    professional_development_3: str = "",
    professional_development_4: str = "",
    professional_development_5: str = "",
    # Additional sections (up to 3)
    additional_section_1_heading: str = "",
    additional_section_1_content: str = "",
    additional_section_2_heading: str = "",
    additional_section_2_content: str = "",
    additional_section_3_heading: str = "",
    additional_section_3_content: str = "",
) -> str:
    """
    Generate candidate data file for use in both shortlist and candidate reports.

    CHARACTER ENCODING: Use ONLY standard ASCII characters (straight quotes ', regular hyphens -)
    AVOID: Curly quotes "", em-dashes —, smart apostrophes '

    Args:
        full_name: Candidate full name (REQUIRED)
        candidate_target_role: Target position (REQUIRED)
        client_company_name: Client company (REQUIRED)
        report_generation_date: Report date (REQUIRED)
        first_name: Candidate first name (auto-extracted if not provided)
        last_name: Candidate last name (auto-extracted if not provided)
        All other candidate fields (employment, education, etc.)

    Returns:
        Success message with file path
    """
    try:
        # Auto-extract first_name and last_name from full_name if not provided
        if not first_name or not last_name:
            name_parts = full_name.strip().split()
            if not first_name and len(name_parts) > 0:
                first_name = name_parts[0]
            if not last_name and len(name_parts) > 1:
                last_name = name_parts[-1]
            elif not last_name and len(name_parts) == 1:
                # If only one name part, use it for both
                last_name = name_parts[0]

        current_year = datetime.now().year
        clean_role = "".join(c for c in candidate_target_role if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        clean_company = "".join(c for c in client_company_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        folder_name = f"{clean_role}_{clean_company}_{current_year}"
        candidate_folder = DATA_DIR / folder_name
        candidate_folder.mkdir(parents=True, exist_ok=True)

        candidate_data = UnifiedCandidateData(
            full_name=full_name,
            candidate_executive_summary=candidate_executive_summary,
            position=position,
            company=company,
            first_name=first_name,
            last_name=last_name,
            report_generation_date=report_generation_date,
            candidate_target_role=candidate_target_role,
            client_company_name=client_company_name,
            internal_or_blank=internal_or_blank,
            current_location=current_location,
            previous_salary=previous_salary,
            short_term_incentive=short_term_incentive,
            other_remuneration=other_remuneration,
            notice_period=notice_period,
            employment_1_company_name=employment_1_company_name,
            employment_1_company_location=employment_1_company_location,
            employment_1_location=employment_1_location,
            employment_1_start_year=employment_1_start_year,
            employment_1_end_year=employment_1_end_year,
            employment_1_job_title=employment_1_job_title,
            employment_1_start_date_full=employment_1_start_date_full,
            employment_1_end_date_full=employment_1_end_date_full,
            employment_1_date_range_full=employment_1_date_range_full,
            employment_1_role_overview=employment_1_role_overview,
            employment_1_responsibility_primary=employment_1_responsibility_primary,
            employment_1_responsibility_secondary=employment_1_responsibility_secondary,
            employment_1_achievement_primary=employment_1_achievement_primary,
            employment_1_achievement_secondary=employment_1_achievement_secondary,
            employment_2_company_name=employment_2_company_name,
            employment_2_company_location=employment_2_company_location,
            employment_2_location=employment_2_location,
            employment_2_start_year=employment_2_start_year,
            employment_2_end_year=employment_2_end_year,
            employment_2_job_title=employment_2_job_title,
            employment_2_start_date_full=employment_2_start_date_full,
            employment_2_end_date_full=employment_2_end_date_full,
            employment_2_date_range_full=employment_2_date_range_full,
            employment_2_role_overview=employment_2_role_overview,
            employment_2_responsibility_primary=employment_2_responsibility_primary,
            employment_2_responsibility_secondary=employment_2_responsibility_secondary,
            employment_2_achievement_primary=employment_2_achievement_primary,
            employment_2_achievement_secondary=employment_2_achievement_secondary,
            employment_3_company_name=employment_3_company_name,
            employment_3_company_location=employment_3_company_location,
            employment_3_location=employment_3_location,
            employment_3_start_year=employment_3_start_year,
            employment_3_end_year=employment_3_end_year,
            employment_3_job_title=employment_3_job_title,
            employment_3_start_date_full=employment_3_start_date_full,
            employment_3_end_date_full=employment_3_end_date_full,
            employment_3_date_range_full=employment_3_date_range_full,
            employment_3_role_overview=employment_3_role_overview,
            employment_3_responsibility_primary=employment_3_responsibility_primary,
            employment_3_responsibility_secondary=employment_3_responsibility_secondary,
            employment_3_achievement_primary=employment_3_achievement_primary,
            employment_3_achievement_secondary=employment_3_achievement_secondary,
            employment_4_company_name=employment_4_company_name,
            employment_4_company_location=employment_4_company_location,
            employment_4_location=employment_4_location,
            employment_4_start_year=employment_4_start_year,
            employment_4_end_year=employment_4_end_year,
            employment_4_job_title=employment_4_job_title,
            employment_4_start_date_full=employment_4_start_date_full,
            employment_4_end_date_full=employment_4_end_date_full,
            employment_4_date_range_full=employment_4_date_range_full,
            employment_4_role_overview=employment_4_role_overview,
            employment_4_responsibility_primary=employment_4_responsibility_primary,
            employment_4_responsibility_secondary=employment_4_responsibility_secondary,
            employment_4_achievement_primary=employment_4_achievement_primary,
            employment_4_achievement_secondary=employment_4_achievement_secondary,
            employment_5_company_name=employment_5_company_name,
            employment_5_company_location=employment_5_company_location,
            employment_5_location=employment_5_location,
            employment_5_start_year=employment_5_start_year,
            employment_5_end_year=employment_5_end_year,
            employment_5_job_title=employment_5_job_title,
            employment_5_start_date_full=employment_5_start_date_full,
            employment_5_end_date_full=employment_5_end_date_full,
            employment_5_date_range_full=employment_5_date_range_full,
            employment_5_role_overview=employment_5_role_overview,
            employment_5_responsibility_primary=employment_5_responsibility_primary,
            employment_5_responsibility_secondary=employment_5_responsibility_secondary,
            employment_5_achievement_primary=employment_5_achievement_primary,
            employment_5_achievement_secondary=employment_5_achievement_secondary,
            employment_6_company_name=employment_6_company_name,
            employment_6_company_location=employment_6_company_location,
            employment_6_location=employment_6_location,
            employment_6_start_year=employment_6_start_year,
            employment_6_end_year=employment_6_end_year,
            employment_6_job_title=employment_6_job_title,
            employment_6_start_date_full=employment_6_start_date_full,
            employment_6_end_date_full=employment_6_end_date_full,
            employment_6_date_range_full=employment_6_date_range_full,
            employment_6_role_overview=employment_6_role_overview,
            employment_6_responsibility_primary=employment_6_responsibility_primary,
            employment_6_responsibility_secondary=employment_6_responsibility_secondary,
            employment_6_achievement_primary=employment_6_achievement_primary,
            employment_6_achievement_secondary=employment_6_achievement_secondary,
            employment_7_company_name=employment_7_company_name,
            employment_7_company_location=employment_7_company_location,
            employment_7_location=employment_7_location,
            employment_7_start_year=employment_7_start_year,
            employment_7_end_year=employment_7_end_year,
            employment_7_job_title=employment_7_job_title,
            employment_7_start_date_full=employment_7_start_date_full,
            employment_7_end_date_full=employment_7_end_date_full,
            employment_7_date_range_full=employment_7_date_range_full,
            employment_7_role_overview=employment_7_role_overview,
            employment_7_responsibility_primary=employment_7_responsibility_primary,
            employment_7_responsibility_secondary=employment_7_responsibility_secondary,
            employment_7_achievement_primary=employment_7_achievement_primary,
            employment_7_achievement_secondary=employment_7_achievement_secondary,
            directorship_committee_1_name=directorship_committee_1_name,
            directorship_committee_1_year_range=directorship_committee_1_year_range,
            directorship_committee_1_position=directorship_committee_1_position,
            directorship_committee_2_name=directorship_committee_2_name,
            directorship_committee_2_year_range=directorship_committee_2_year_range,
            directorship_committee_2_position=directorship_committee_2_position,
            directorship_committee_3_name=directorship_committee_3_name,
            directorship_committee_3_year_range=directorship_committee_3_year_range,
            directorship_committee_3_position=directorship_committee_3_position,
            education_1_completion_year=education_1_completion_year,
            education_1_qualification_name=education_1_qualification_name,
            education_1_institution_name=education_1_institution_name,
            education_2_completion_year=education_2_completion_year,
            education_2_qualification_name=education_2_qualification_name,
            education_2_institution_name=education_2_institution_name,
            education_3_completion_year=education_3_completion_year,
            education_3_qualification_name=education_3_qualification_name,
            education_3_institution_name=education_3_institution_name,
            education_4_completion_year=education_4_completion_year,
            education_4_qualification_name=education_4_qualification_name,
            education_4_institution_name=education_4_institution_name,
            education_5_completion_year=education_5_completion_year,
            education_5_qualification_name=education_5_qualification_name,
            education_5_institution_name=education_5_institution_name,
            professional_membership_1=professional_membership_1,
            professional_membership_2=professional_membership_2,
            professional_membership_3=professional_membership_3,
            professional_membership_4=professional_membership_4,
            professional_membership_5=professional_membership_5,
            professional_development_1=professional_development_1,
            professional_development_2=professional_development_2,
            professional_development_3=professional_development_3,
            professional_development_4=professional_development_4,
            professional_development_5=professional_development_5,
            additional_section_1_heading=additional_section_1_heading,
            additional_section_1_content=additional_section_1_content,
            additional_section_2_heading=additional_section_2_heading,
            additional_section_2_content=additional_section_2_content,
            additional_section_3_heading=additional_section_3_heading,
            additional_section_3_content=additional_section_3_content,
        )

        data_dict = candidate_data.model_dump()
        clean_name = "".join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        candidate_filename = f"{clean_name}_{timestamp}.json"
        candidate_output_path = candidate_folder / candidate_filename

        with open(candidate_output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)

        return f"""
Candidate saved: {full_name}
File: {candidate_output_path}
Project: {folder_name}
        """

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
@log_mcp_tool
def generate_candidate_assessment(
    folder_name: str,
    full_name: str,
    assess_1: str,
    assess_2: str,
    assess_3: str,
    assess_4: str,
    assess_5: str,
    assess_6: str,
    assess_7: str,
    assess_8: str,
    role_skill_1_assessment: str,
    role_skill_2_assessment: str,
    role_skill_3_assessment: str,
    role_skill_4_assessment: str,
    role_skill_5_assessment: str,
    role_skill_6_assessment: str,
    role_skill_7_assessment: str,
    role_skill_8_assessment: str,
    consultant_commentary_para_1: str,
    consultant_commentary_para_2: str,
    consultant_commentary_para_3: str,
) -> str:
    """
    Generate candidate assessment with ratings (1-10), skill evaluations, and consultant commentary.

    Rating Scale: 1-2=Below, 3-4=Gaps, 5-6=Adequate, 7-8=Strong, 9-10=Exceptional

    CHARACTER ENCODING: Use ONLY standard ASCII characters (straight quotes ', regular hyphens -)
    AVOID: Curly quotes "", em-dashes —, smart apostrophes '

    Args:
        folder_name: Project folder (e.g., "CEO_Quantium_2025")
        full_name: Exact candidate name (must match data file)
        assess_1 to assess_7: Rating scores 1-10 for each skill (REQUIRED)
        role_skill_X_assessment: Text assessment for each skill, 2-4 sentences (REQUIRED)
        consultant_commentary_para_1/2/3: Three paragraphs, 4-6 sentences each (REQUIRED)

    Returns:
        Success message with file path
    """
    try:
        project_folder = DATA_DIR / folder_name
        if not project_folder.exists():
            return f"Error: Project folder not found: {project_folder}"

        # Verify candidate exists
        clean_name = "".join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        candidate_files = [f for f in project_folder.glob(f"{clean_name}_*.json") 
                          if "_assessment_" not in f.name]
        
        if not candidate_files:
            return f"Error: No candidate file found for {full_name}"

        # Create assessment
        assessment = CandidateAssessment(
            full_name=full_name,
            assess_1=assess_1,
            assess_2=assess_2,
            assess_3=assess_3,
            assess_4=assess_4,
            assess_5=assess_5,
            assess_6=assess_6,
            assess_7=assess_7,
            assess_8=assess_8,
            role_skill_1_assessment=role_skill_1_assessment,
            role_skill_2_assessment=role_skill_2_assessment,
            role_skill_3_assessment=role_skill_3_assessment,
            role_skill_4_assessment=role_skill_4_assessment,
            role_skill_5_assessment=role_skill_5_assessment,
            role_skill_6_assessment=role_skill_6_assessment,
            role_skill_7_assessment=role_skill_7_assessment,
            role_skill_8_assessment=role_skill_8_assessment,
            consultant_commentary_para_1=consultant_commentary_para_1,
            consultant_commentary_para_2=consultant_commentary_para_2,
            consultant_commentary_para_3=consultant_commentary_para_3,
        )

        # Save assessment file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        assessment_filename = f"{clean_name}_assessment_{timestamp}.json"
        assessment_path = project_folder / assessment_filename

        with open(assessment_path, 'w', encoding='utf-8') as f:
            json.dump(assessment.model_dump(), f, indent=2, ensure_ascii=False)

        return f"""
Assessment saved: {full_name}
File: {assessment_filename}
        """

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# DOCUMENT GENERATION TOOLS
# ============================================================================

@mcp.tool()
@log_mcp_tool
def generate_shortlist_report(folder_name: str) -> str:
    """
    Generate complete shortlist report (overview + candidate profiles + merged document).

    IMPORTANT: Only call this when user EXPLICITLY asks to generate/create the final shortlist report.
    Do NOT call automatically after adding candidates or assessments.
    Wait for user to say "generate the report" or similar explicit request.

    Prerequisites:
    - Metadata file must exist
    - Candidate files must exist
    - Assessment files must exist for ALL candidates

    Args:
        folder_name: Project folder (e.g., "CEO_Quantium_2025")

    Returns:
        Success message with final report path
    """
    try:
        project_folder = DATA_DIR / folder_name
        output_folder = OUTPUTS_DIR / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        # Get all candidates
        candidate_files = [
            f for f in project_folder.glob("*.json")
            if not f.name.startswith("metadata_")
            and not f.name.startswith("merged_")
            and "_assessment_" not in f.name
        ]

        if not candidate_files:
            return f"Error: No candidate files found in {folder_name}"

        # Check if all candidates have assessments
        candidates_without_assessments = []
        for candidate_file in candidate_files:
            with open(candidate_file, 'r', encoding='utf-8') as f:
                candidate_data = json.load(f)
            
            candidate_name = candidate_data.get("full_name", "")
            clean_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            assessment_files = list(project_folder.glob(f"{clean_name}_assessment_*.json"))
            
            if not assessment_files:
                candidates_without_assessments.append(candidate_name)

        if candidates_without_assessments:
            return f"""
Error: Missing assessments for: {', '.join(candidates_without_assessments)}
Create assessments using generate_candidate_assessment()
            """

        # Merge candidate data
        merge_result = merge_candidates_data(folder_name, base_path=str(DATA_DIR))
        if not merge_result["success"]:
            return f"Error merging data: {merge_result['message']}"

        merged_data_path = merge_result['output_file']

        # Generate overview document
        overview_result = process_document_template(
            candidate_data_path=merged_data_path,
            template_path=str(SHORTLIST_OVERVIEW_TEMPLATE),
            output_dir=str(output_folder)
        )
        if not overview_result["success"]:
            return f"Error generating overview: {overview_result['message']}"

        overview_doc_path = overview_result["output_file"]

        # Apply colors to overview
        apply_table_colors(overview_doc_path, overview_doc_path)

        # Generate individual candidate documents
        candidate_doc_paths = []
        for candidate_file in sorted(candidate_files):
            with open(candidate_file, 'r', encoding='utf-8') as f:
                candidate_data = json.load(f)

            # Load metadata
            metadata_files = list(project_folder.glob("metadata_*.json"))
            with open(sorted(metadata_files)[-1], 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Load assessment
            candidate_name = candidate_data.get("full_name", "")
            clean_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            assessment_files = list(project_folder.glob(f"{clean_name}_assessment_*.json"))

            with open(sorted(assessment_files)[-1], 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)

            # Combine data - FIX for first_name/last_name
            combined_data = {}
            
            # Add metadata
            for key, value in metadata.items():
                combined_data[key] = value
            
            # Add candidate data (including first_name and last_name as-is)
            for key, value in candidate_data.items():
                combined_data[key] = value
            
            # Add assessment data
            for key, value in assessment_data.items():
                if key != 'full_name':
                    combined_data[key] = value

            # Save temp combined file
            temp_json_path = project_folder / f"temp_{candidate_file.name}"
            with open(temp_json_path, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)

            # Generate candidate document
            candidate_result = process_document_template(
                candidate_data_path=str(temp_json_path),
                template_path=str(SHORTLIST_CANDIDATE_TEMPLATE),
                output_dir=str(output_folder)
            )

            if temp_json_path.exists():
                os.remove(temp_json_path)

            if not candidate_result["success"]:
                return f"Error generating document for {candidate_name}: {candidate_result['message']}"

            candidate_doc_paths.append(candidate_result["output_file"])

        # Merge all documents
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        merged_filename = f"shortlist_report_{timestamp}.docx"
        merged_output_path = output_folder / merged_filename

        merge_doc_result = merge_shortlist_documents(
            overview_path=overview_doc_path,
            candidate_paths=candidate_doc_paths,
            output_path=str(merged_output_path),
            end_page_path=str(SHORTLIST_END_PAGE)
        )

        if not merge_doc_result["success"]:
            return f"Error merging documents: {merge_doc_result['message']}"

        # Apply table colors to final document
        apply_table_colors(str(merged_output_path), str(merged_output_path))

        return f"""
SUCCESS - Shortlist report complete!
File: {merged_output_path}
Candidates: {len(candidate_files)}
        """

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
@log_mcp_tool
def generate_candidate_report(candidate_data_path: str) -> str:
    """
    Generate standalone candidate report (no assessment needed).

    IMPORTANT: Only call this when user EXPLICITLY asks to generate/create the candidate report.
    Do NOT call automatically after adding candidate data.
    Wait for user to say "generate the report" or similar explicit request.

    Args:
        candidate_data_path: Path to candidate JSON file (can be filename, folder/filename, or full path)

    Returns:
        Success message with report path
    """
    try:
        # Resolve data path
        data_path = Path(candidate_data_path)
        if not data_path.is_absolute():
            if '/' in candidate_data_path or '\\' in candidate_data_path:
                data_path = DATA_DIR / candidate_data_path
            else:
                found = list(DATA_DIR.rglob(candidate_data_path))
                if found:
                    data_path = found[0]
                else:
                    data_path = DATA_DIR / candidate_data_path

        if not data_path.exists():
            return f"Error: Candidate file not found: {data_path}"

        # Setup output directory
        output_dir = OUTPUTS_DIR / "candidate_reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate document
        result = process_document_template(
            candidate_data_path=str(data_path),
            template_path=str(CANDIDATE_REPORT_TEMPLATE),
            output_dir=str(output_dir)
        )

        if not result["success"]:
            return f"Error: {result['message']}"

        output_path = result["output_file"]

        # Merge duplicate table cells
        merge_result = merge_duplicate_first_column_cells(
            input_path=output_path,
            output_path=output_path,
            table_index=0
        )

        if not merge_result["success"]:
            return f"Warning: Table merge failed: {merge_result['message']}\nReport saved at: {output_path}"

        return f"""
SUCCESS - Candidate report complete!
File: {output_path}
        """

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# DATA READING AND PROJECT MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
@log_mcp_tool
def check_existing_projects() -> str:
    """
    Check all existing projects, candidate counts, and report readiness.

    Returns:
        Overview of projects with metadata status, candidate counts, and assessment status
    """
    try:
        if not DATA_DIR.exists():
            return "No projects found."

        project_folders = [d for d in DATA_DIR.iterdir() if d.is_dir()]
        if not project_folders:
            return f"No projects in {DATA_DIR}."

        result = [f"Found {len(project_folders)} project(s):\n"]

        for folder in sorted(project_folders):
            result.append(f"\n{folder.name}")

            metadata_files = list(folder.glob("metadata_*.json"))
            has_metadata = len(metadata_files) > 0

            candidate_files = [f for f in folder.glob("*.json")
                             if not f.name.startswith("metadata_")
                             and not f.name.startswith("merged_")
                             and "_assessment_" not in f.name]
            num_candidates = len(candidate_files)

            assessment_files = list(folder.glob("*_assessment_*.json"))
            num_assessments = len(assessment_files)

            result.append(f"  Metadata: {'Yes' if has_metadata else 'No'}")
            result.append(f"  Candidates: {num_candidates}")
            result.append(f"  Assessments: {num_assessments}/{num_candidates}")

            # List candidate names
            if num_candidates > 0:
                result.append(f"  Candidate files:")
                for cf in sorted(candidate_files):
                    result.append(f"    - {cf.name}")

            # Next steps
            if not has_metadata:
                result.append(f"  Next: Create metadata")
            elif num_candidates == 0:
                result.append(f"  Next: Add candidates")
            elif num_assessments < num_candidates:
                remaining = num_candidates - num_assessments
                result.append(f"  Next: Assess {remaining} candidate(s)")
            else:
                result.append(f"  Ready: Generate report")

        return "\n".join(result)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
@log_mcp_tool
def read_project_data(folder_name: str, data_type: str = "all") -> str:
    """
    Read project data including metadata, candidates, and assessments.

    Args:
        folder_name: Project folder (e.g., "CEO_Quantium_2025")
        data_type: What to read - "metadata", "candidates", "assessments", or "all" (default: "all")

    Returns:
        Formatted data from the project
    """
    try:
        project_path = DATA_DIR / folder_name
        if not project_path.exists():
            available = [d.name for d in DATA_DIR.iterdir() if d.is_dir()]
            return f"Project not found: {folder_name}\nAvailable: {', '.join(available)}"

        result = [f"PROJECT: {folder_name}\n"]

        # Read metadata
        if data_type in ["metadata", "all"]:
            metadata_files = list(project_path.glob("metadata_*.json"))
            if metadata_files:
                with open(sorted(metadata_files)[-1], 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                result.append("=== METADATA ===")
                result.append(f"Company: {meta.get('client_company_name', 'N/A')}")
                result.append(f"Role: {meta.get('candidate_target_role', 'N/A')}")
                result.append("\n7 Role Skills:")
                for i in range(1, 8):
                    skill = meta.get(f'role_skill_{i}', '')
                    if skill:
                        result.append(f"  {i}. {skill}")
                result.append("")

        # Read candidates
        if data_type in ["candidates", "all"]:
            candidate_files = [f for f in project_path.glob("*.json")
                             if not f.name.startswith("metadata_")
                             and not f.name.startswith("merged_")
                             and "_assessment_" not in f.name]
            
            if candidate_files:
                result.append(f"=== CANDIDATES ({len(candidate_files)}) ===")
                for cf in sorted(candidate_files):
                    with open(cf, 'r', encoding='utf-8') as f:
                        cand = json.load(f)
                    
                    result.append(f"\nFile: {cf.name}")
                    result.append(f"Name: {cand.get('full_name', 'N/A')}")
                    result.append(f"Position: {cand.get('position', 'N/A')} at {cand.get('company', 'N/A')}")
                    result.append(f"Location: {cand.get('current_location', 'N/A')}")
                    
                    # Show employment history
                    emp_count = sum(1 for i in range(1, 8) if cand.get(f'employment_{i}_company_name', ''))
                    if emp_count > 0:
                        result.append(f"Employment history: {emp_count} positions")
                        for i in range(1, min(3, emp_count + 1)):
                            company = cand.get(f'employment_{i}_company_name', '')
                            title = cand.get(f'employment_{i}_job_title', '')
                            if company:
                                result.append(f"  {i}. {title} at {company}")
                result.append("")

        # Read assessments
        if data_type in ["assessments", "all"]:
            assessment_files = list(project_path.glob("*_assessment_*.json"))
            
            if assessment_files:
                result.append(f"=== ASSESSMENTS ({len(assessment_files)}) ===")
                for af in sorted(assessment_files):
                    with open(af, 'r', encoding='utf-8') as f:
                        assess = json.load(f)
                    
                    result.append(f"\nFile: {af.name}")
                    result.append(f"Candidate: {assess.get('full_name', 'N/A')}")
                    result.append(f"Ratings: {assess.get('assess_1', '')}, {assess.get('assess_2', '')}, {assess.get('assess_3', '')}, {assess.get('assess_4', '')}, {assess.get('assess_5', '')}, {assess.get('assess_6', '')}, {assess.get('assess_7', '')}")
                result.append("")

        if len(result) == 1:
            result.append("No data found for the specified data_type.")

        return "\n".join(result)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
@log_mcp_tool
def shortlist_report_plan() -> str:
    """Workflow guide for creating shortlist reports."""
    return """
SHORTLIST REPORT WORKFLOW
Compare multiple candidates side-by-side

STEPS:

1. CHECK if project exists
   check_existing_projects()
   
   If exists: read_project_data(folder_name, "metadata")
   If not: Ask user for company name, role, and 7 role skills

2. CREATE metadata (if needed)
   generate_shortlist_metadata(...)

3. FOR EACH CANDIDATE:
   
   a) ADD candidate data
      generate_individual_candidate(...)
   
   b) ASSESS candidate
      Ask user directly:
      - "Rate them 1-10 on each skill"
      - "What are their strengths?"
      - "What are development areas?"
      - "Provide 3 paragraphs of commentary"
      
      generate_candidate_assessment(...)

4. GENERATE report ONLY when user explicitly asks
   
   WAIT for user to say:
   - "Generate the shortlist report"
   - "Create the final report"
   - "I'm ready to generate the report"
   
   DO NOT generate automatically after assessments
   
   When requested:
   generate_shortlist_report(folder_name)

RATING SCALE:
1-2=Below, 3-4=Gaps, 5-6=Adequate, 7-8=Strong, 9-10=Exceptional

CHARACTER ENCODING:
Use straight quotes ', regular hyphens -
Avoid curly quotes "", em-dashes —, smart apostrophes '
    """


@mcp.tool()
@log_mcp_tool
def candidate_report_plan() -> str:
    """Workflow guide for creating standalone candidate reports."""
    return """
CANDIDATE REPORT WORKFLOW
Standalone individual profile (no assessment needed)

STEPS:

1. INPUT candidate CV/data from user

2. ASK for role and company if not provided

3. GENERATE candidate data file
   generate_individual_candidate(...)

4. GENERATE report ONLY when user explicitly asks
   
   WAIT for user to say:
   - "Generate the candidate report"
   - "Create the report"
   - "I'm ready for the report"
   
   DO NOT generate automatically after adding data
   
   When requested:
   generate_candidate_report("path/to/candidate.json")

CHARACTER ENCODING:
Use straight quotes ', regular hyphens -
Avoid curly quotes "", em-dashes —, smart apostrophes '
    """


@mcp.tool()
@log_mcp_tool
def ping() -> str:
    """Health check"""
    return "pong"


@mcp.tool()
def test_logging_connection() -> str:
    """
    Test connection to the logging API endpoint.
    
    This tool verifies that the logging system is properly configured and can
    successfully communicate with the remote API. Should be run before starting
    any report generation workflow to ensure all tool usage will be tracked.
    
    How it works:
    - Attempts to send a test log entry to the API
    - Returns success message if logging works
    - Returns detailed error message if logging fails
    
    Returns:
        Success message if logging works, error message with troubleshooting steps if it fails
    """
    try:
        # Create test parameters
        test_parameters = {
            "test_mode": True,
            "timestamp": datetime.now().isoformat(),
            "test_type": "connection_test"
        }
        
        # Create test user info
        test_user_info = {
            "client": "connection_test",
            "test_run": True
        }
        
        # Attempt to log a test entry directly through the logger
        success, error_message = _logger.log_tool_usage(
            tool_name="test_logging_connection",
            parameters=test_parameters,
            user_info=test_user_info,
            success=True,
            execution_time_ms=0,
            output_preview="Testing logging endpoint connectivity",
            error_message=""
        )
        
        if success:
            return """✓ Logging system is working correctly!

Connection Status: ✓ Connected
API Endpoint: ✓ Responding
Payload Format: ✓ Accepted
Authentication: ✓ Valid

The logging system is ready to track all tool usage.
You can proceed with report generation and other operations.

All tools decorated with @log_mcp_tool will automatically:
- Log tool name and parameters
- Track execution time
- Record success/failure status
- Capture user context
"""
        else:
            return f"""✗ Logging system test FAILED!

Error: {error_message}

⚠️  CRITICAL: Tool usage tracking is not working.

Troubleshooting steps:
1. Check MCP_LOG_URL environment variable
   Current: {_logger.base_url}

2. Verify API endpoint is accessible
   Try: curl -X POST {_logger.base_url}

3. Check network connectivity
   Ensure your server can reach the API endpoint

4. Verify MCP_LOG_AUTH_TOKEN (if required)
   Check if the token is set and valid

5. Review server logs
   Check for detailed error messages in stderr

❌ DO NOT proceed with report generation until logging is fixed.

The system requires logging to be functional to track usage and ensure compliance."""
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return f"""✗ Logging system test FAILED with exception!

Error Type: {type(e).__name__}
Error Message: {str(e)}

Detailed traceback:
{error_details}

⚠️  CRITICAL: Unable to test logging system.

This suggests a deeper issue with the logging module:
- Check if utils.logging_db is properly installed
- Verify all dependencies are installed (requests, etc.)
- Ensure the logging_db.py file is in the correct location
- Check for import errors in the logging module

Configuration:
- Base URL: {_logger.base_url if '_logger' in dir() else 'Unknown'}
- Error count: {_logger._error_count if '_logger' in dir() else 'Unknown'}

❌ DO NOT proceed until this is resolved."""


@mcp.tool()  # NO decorator - for comparison testing
def test_logging_no_decorator() -> str:
    """
    Test logging without the decorator to verify the payload format.
    This bypasses the logging system to test the API directly.
    """
    
    base_url = "http://ai.omerapartners.com/api/AIReportGeneratorLog/LogAIGeneratedExecutiveReport"
    headers = {'Content-Type': 'application/json'}
    
    try:
        user_info = {
            "username": getpass.getuser(),
            "hostname": socket.gethostname()
        }
    except Exception:
        user_info = {
            "username": "unknown",
            "hostname": "unknown"
        }
    
    parameters = {"report_id": "exec_summary_001"}
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    payload = {
        "timestamp": timestamp,
        "tool_name": "test_from_mcp_no_decorator",
        "parameters": json.dumps(parameters),
        "user_info": json.dumps(user_info),
        "success": 1,
        "execution_time_ms": 100
    }
    
    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        
        return f"""✓ Direct API test SUCCESS!

Status Code: {response.status_code}
Response: {response.text[:200]}

Payload sent:
{json.dumps(payload, indent=2)}

This confirms the API endpoint and payload format are correct.
The decorator and logging_db module should now work with the corrected code."""
        
    except Exception as e:
        error_msg = f"""✗ Direct API test FAILED!

Error: {str(e)}
"""
        if hasattr(e, 'response') and e.response:
            error_msg += f"""
Status: {e.response.status_code}
Response: {e.response.text[:500]}
"""
        
        error_msg += f"""
Payload that failed:
{json.dumps(payload, indent=2)}"""
        return error_msg


if __name__ == "__main__":
    mcp.run()