from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ShortlistMetadata(BaseModel):
    """Metadata for the shortlist report - client info, role skills, consultant team"""

    # Basic Information
    client_company_name: str = Field(..., description="Name of the client company requesting the shortlist")
    candidate_target_role: str = Field(..., description="The specific role/position candidates are being considered for")
    report_generation_date: str = Field(default_factory=lambda: datetime.now().strftime("%d %B %Y"))

    # Client Information
    client_1_full_name: str = Field(default="", description="Full name of first client contact")
    client_1_position: str = Field(default="", description="Position/title of first client contact")
    client_2_full_name: str = Field(default="", description="Full name of second client contact")
    client_2_position: str = Field(default="", description="Position/title of second client contact")
    client_3_full_name: str = Field(default="", description="Full name of third client contact")
    client_3_position: str = Field(default="", description="Position/title of third client contact")

    # Assignment Team
    consultant_1_name: str = Field(default="", description="Name of lead consultant")
    consultant_1_position: str = Field(default="", description="Position of lead consultant")
    consultant_2_name: str = Field(default="", description="Name of second consultant")
    consultant_2_position: str = Field(default="", description="Position of second consultant")
    consultant_3_name: str = Field(default="", description="Name of third consultant")
    consultant_3_position: str = Field(default="", description="Position of third consultant")

    # Role Skills for Assessment Matrix (8 skills)
    role_skill_1: str = Field(default="", description="First key role skill")
    role_skill_2: str = Field(default="", description="Second key role skill")
    role_skill_3: str = Field(default="", description="Third key role skill")
    role_skill_4: str = Field(default="", description="Fourth key role skill")
    role_skill_5: str = Field(default="", description="Fifth key role skill")
    role_skill_6: str = Field(default="", description="Sixth key role skill")
    role_skill_7: str = Field(default="", description="Seventh key role skill")
    role_skill_8: str = Field(default="", description="Eighth key role skill")

class CandidateAssessment(BaseModel):
    """Assessment data for a candidate in a shortlist report - ratings and commentary"""

    # Basic Information (for linking to candidate)
    full_name: str = Field(..., description="Full name of candidate being assessed")

    # Skills Assessment (1-10 scale for 8 skills)
    assess_1: str = Field(default="5", description="Assessment score for role skill 1")
    assess_2: str = Field(default="5", description="Assessment score for role skill 2")
    assess_3: str = Field(default="5", description="Assessment score for role skill 3")
    assess_4: str = Field(default="5", description="Assessment score for role skill 4")
    assess_5: str = Field(default="5", description="Assessment score for role skill 5")
    assess_6: str = Field(default="5", description="Assessment score for role skill 6")
    assess_7: str = Field(default="5", description="Assessment score for role skill 7")
    assess_8: str = Field(default="5", description="Assessment score for role skill 8")

    # Detailed Skills Assessment (text descriptions for each skill)
    role_skill_1_assessment: str = Field(default="", description="Detailed assessment of role skill 1")
    role_skill_2_assessment: str = Field(default="", description="Detailed assessment of role skill 2")
    role_skill_3_assessment: str = Field(default="", description="Detailed assessment of role skill 3")
    role_skill_4_assessment: str = Field(default="", description="Detailed assessment of role skill 4")
    role_skill_5_assessment: str = Field(default="", description="Detailed assessment of role skill 5")
    role_skill_6_assessment: str = Field(default="", description="Detailed assessment of role skill 6")
    role_skill_7_assessment: str = Field(default="", description="Detailed assessment of role skill 7")
    role_skill_8_assessment: str = Field(default="", description="Detailed assessment of role skill 8")

    # Commentary (consultant's overall assessment)
    consultant_commentary_para_1: str = Field(default="", description="First paragraph of consultant commentary")
    consultant_commentary_para_2: str = Field(default="", description="Second paragraph of consultant commentary")
    consultant_commentary_para_3: str = Field(default="", description="Third paragraph of consultant commentary")


class UnifiedCandidateData(BaseModel):
    """Unified data structure for a candidate supporting both candidate report and shortlist report"""

    # Basic Information (required for naming)
    full_name: str = Field(..., description="Full name of candidate")

    # Basic Information (optional - for shortlist report)
    position: str = Field(default="", description="Current position of candidate")
    company: str = Field(default="", description="Current company of candidate")
    first_name: str = Field(default="", description="First name of candidate")
    last_name: str = Field(default="", description="Last name of candidate")
    internal_or_blank: str = Field(default="", description="INTERNAL marker if internal candidate")
    client_company_name: str = Field(default="", description="Name of the company the report is being written for")
    report_generation_date: str = Field(default="", description="Current date or specified date")
    candidate_target_role: str = Field(default="", description="Target role that the report is being written for")

    # Executive Summary (for candidate report)
    candidate_executive_summary: str = Field(default="", description="Executive summary/profile")

    # Employment History (up to 7 positions) - includes fields for both report types
    # Position 1 (Most Recent)
    employment_1_company_name: str = Field(default="", description="Most recent employer")
    employment_1_company_location: str = Field(default="", description="Company location (for summary)")
    employment_1_location: str = Field(default="", description="Location of role (for detailed section)")
    employment_1_start_year: str = Field(default="", description="Start year")
    employment_1_end_year: str = Field(default="", description="End year")
    employment_1_job_title: str = Field(default="", description="Job title")
    employment_1_start_date_full: str = Field(default="", description="Full start date (e.g., 'October 2020')")
    employment_1_end_date_full: str = Field(default="", description="Full end date (e.g., 'March 2023' or 'Present')")
    employment_1_date_range_full: str = Field(default="", description="Combined date range")
    employment_1_role_overview: str = Field(default="", description="Role overview")
    employment_1_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_1_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_1_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_1_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 2
    employment_2_company_name: str = Field(default="", description="Second employer")
    employment_2_company_location: str = Field(default="", description="Company location")
    employment_2_location: str = Field(default="", description="Location of role")
    employment_2_start_year: str = Field(default="", description="Start year")
    employment_2_end_year: str = Field(default="", description="End year")
    employment_2_job_title: str = Field(default="", description="Job title")
    employment_2_start_date_full: str = Field(default="", description="Full start date")
    employment_2_end_date_full: str = Field(default="", description="Full end date")
    employment_2_date_range_full: str = Field(default="", description="Combined date range")
    employment_2_role_overview: str = Field(default="", description="Role overview")
    employment_2_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_2_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_2_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_2_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 3
    employment_3_company_name: str = Field(default="", description="Third employer")
    employment_3_company_location: str = Field(default="", description="Company location")
    employment_3_location: str = Field(default="", description="Location of role")
    employment_3_start_year: str = Field(default="", description="Start year")
    employment_3_end_year: str = Field(default="", description="End year")
    employment_3_job_title: str = Field(default="", description="Job title")
    employment_3_start_date_full: str = Field(default="", description="Full start date")
    employment_3_end_date_full: str = Field(default="", description="Full end date")
    employment_3_date_range_full: str = Field(default="", description="Combined date range")
    employment_3_role_overview: str = Field(default="", description="Role overview")
    employment_3_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_3_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_3_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_3_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 4
    employment_4_company_name: str = Field(default="", description="Fourth employer")
    employment_4_company_location: str = Field(default="", description="Company location")
    employment_4_location: str = Field(default="", description="Location of role")
    employment_4_start_year: str = Field(default="", description="Start year")
    employment_4_end_year: str = Field(default="", description="End year")
    employment_4_job_title: str = Field(default="", description="Job title")
    employment_4_start_date_full: str = Field(default="", description="Full start date")
    employment_4_end_date_full: str = Field(default="", description="Full end date")
    employment_4_date_range_full: str = Field(default="", description="Combined date range")
    employment_4_role_overview: str = Field(default="", description="Role overview")
    employment_4_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_4_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_4_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_4_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 5
    employment_5_company_name: str = Field(default="", description="Fifth employer")
    employment_5_company_location: str = Field(default="", description="Company location")
    employment_5_location: str = Field(default="", description="Location of role")
    employment_5_start_year: str = Field(default="", description="Start year")
    employment_5_end_year: str = Field(default="", description="End year")
    employment_5_job_title: str = Field(default="", description="Job title")
    employment_5_start_date_full: str = Field(default="", description="Full start date")
    employment_5_end_date_full: str = Field(default="", description="Full end date")
    employment_5_date_range_full: str = Field(default="", description="Combined date range")
    employment_5_role_overview: str = Field(default="", description="Role overview")
    employment_5_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_5_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_5_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_5_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 6
    employment_6_company_name: str = Field(default="", description="Sixth employer")
    employment_6_company_location: str = Field(default="", description="Company location")
    employment_6_location: str = Field(default="", description="Location of role")
    employment_6_start_year: str = Field(default="", description="Start year")
    employment_6_end_year: str = Field(default="", description="End year")
    employment_6_job_title: str = Field(default="", description="Job title")
    employment_6_start_date_full: str = Field(default="", description="Full start date")
    employment_6_end_date_full: str = Field(default="", description="Full end date")
    employment_6_date_range_full: str = Field(default="", description="Combined date range")
    employment_6_role_overview: str = Field(default="", description="Role overview")
    employment_6_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_6_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_6_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_6_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Position 7
    employment_7_company_name: str = Field(default="", description="Seventh employer")
    employment_7_company_location: str = Field(default="", description="Company location")
    employment_7_location: str = Field(default="", description="Location of role")
    employment_7_start_year: str = Field(default="", description="Start year")
    employment_7_end_year: str = Field(default="", description="End year")
    employment_7_job_title: str = Field(default="", description="Job title")
    employment_7_start_date_full: str = Field(default="", description="Full start date")
    employment_7_end_date_full: str = Field(default="", description="Full end date")
    employment_7_date_range_full: str = Field(default="", description="Combined date range")
    employment_7_role_overview: str = Field(default="", description="Role overview")
    employment_7_responsibility_primary: str = Field(default="", description="Primary responsibility")
    employment_7_responsibility_secondary: str = Field(default="", description="Secondary responsibility")
    employment_7_achievement_primary: str = Field(default="", description="Primary achievement")
    employment_7_achievement_secondary: str = Field(default="", description="Secondary achievement")

    # Directorships/Committees (up to 3)
    directorship_committee_1_name: str = Field(default="", description="First directorship/committee")
    directorship_committee_1_year_range: str = Field(default="", description="Years of first directorship")
    directorship_committee_1_position: str = Field(default="", description="Position in first directorship")

    directorship_committee_2_name: str = Field(default="", description="Second directorship/committee")
    directorship_committee_2_year_range: str = Field(default="", description="Years of second directorship")
    directorship_committee_2_position: str = Field(default="", description="Position in second directorship")

    directorship_committee_3_name: str = Field(default="", description="Third directorship/committee")
    directorship_committee_3_year_range: str = Field(default="", description="Years of third directorship")
    directorship_committee_3_position: str = Field(default="", description="Position in third directorship")

    # Education (up to 5 qualifications)
    education_1_completion_year: str = Field(default="", description="Year of most recent qualification")
    education_1_qualification_name: str = Field(default="", description="Name of most recent qualification")
    education_1_institution_name: str = Field(default="", description="Institution of most recent qualification")

    education_2_completion_year: str = Field(default="", description="Year of second qualification")
    education_2_qualification_name: str = Field(default="", description="Name of second qualification")
    education_2_institution_name: str = Field(default="", description="Institution of second qualification")

    education_3_completion_year: str = Field(default="", description="Year of third qualification")
    education_3_qualification_name: str = Field(default="", description="Name of third qualification")
    education_3_institution_name: str = Field(default="", description="Institution of third qualification")

    education_4_completion_year: str = Field(default="", description="Year of fourth qualification")
    education_4_qualification_name: str = Field(default="", description="Name of fourth qualification")
    education_4_institution_name: str = Field(default="", description="Institution of fourth qualification")

    education_5_completion_year: str = Field(default="", description="Year of fifth qualification")
    education_5_qualification_name: str = Field(default="", description="Name of fifth qualification")
    education_5_institution_name: str = Field(default="", description="Institution of fifth qualification")

    # Professional Memberships & Certifications (for candidate report)
    professional_membership_1: str = Field(default="", description="First professional membership")
    professional_membership_2: str = Field(default="", description="Second professional membership")
    professional_membership_3: str = Field(default="", description="Third professional membership")
    professional_membership_4: str = Field(default="", description="Fourth professional membership")
    professional_membership_5: str = Field(default="", description="Fifth professional membership")

    # Professional Development & Training (for candidate report)
    professional_development_1: str = Field(default="", description="First professional development item")
    professional_development_2: str = Field(default="", description="Second professional development item")
    professional_development_3: str = Field(default="", description="Third professional development item")
    professional_development_4: str = Field(default="", description="Fourth professional development item")
    professional_development_5: str = Field(default="", description="Fifth professional development item")

    # Other Details (for shortlist report)
    current_location: str = Field(default="", description="Current location of candidate")
    previous_salary: str = Field(default="", description="Previous salary information")
    short_term_incentive: str = Field(default="", description="Short term incentive details")
    other_remuneration: str = Field(default="", description="Other remuneration details")
    notice_period: str = Field(default="", description="Notice period requirements")

    # Additional Information Sections (for candidate report)
    additional_section_1_heading: str = Field(default="", description="Heading for first additional section")
    additional_section_1_content: str = Field(default="", description="Content for first additional section")
    additional_section_2_heading: str = Field(default="", description="Heading for second additional section")
    additional_section_2_content: str = Field(default="", description="Content for second additional section")
    additional_section_3_heading: str = Field(default="", description="Heading for third additional section")
    additional_section_3_content: str = Field(default="", description="Content for third additional section")

# Example usage and validation
if __name__ == "__main__":
    # Test metadata creation
    metadata = ShortlistMetadata(
        client_company_name="Acme Corp",
        candidate_target_role="Chief Technology Officer"
    )

    # Test unified candidate creation
    candidate = UnifiedCandidateData(
        full_name="John Smith"
    )

    print("ShortlistMetadata Model Schema:")
    print(f"Metadata fields: {len(metadata.model_fields)}")

    print(f"\nUnifiedCandidateData Model Schema:")
    print(f"Candidate fields: {len(candidate.model_fields)}")

    print("\nModels successfully created and validated!")