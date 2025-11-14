# Executive Reports Server

An MCP (Model Context Protocol) server for generating professional executive recruitment reports. Supports both shortlist reports (comparing multiple candidates) and standalone candidate reports.

## Overview

The Executive Reports Server automates the generation of two types of executive recruitment documents:

1. **Shortlist Reports**: Compare up to 10 candidates with skills matrices, detailed profiles, and consultant commentary
2. **Candidate Reports**: Standalone detailed profiles for individual candidates

The system uses Word document templates with placeholder substitution, manages candidate data as JSON files, and provides a complete workflow from data entry to final formatted documents.

## Project Structure

```
exec_reports/
├── server.py                 # Main MCP server with FastMCP tools
├── replace.py                # Template processing and placeholder replacement
├── templates/                # Word document templates
│   ├── c_template.docx      # Candidate report template
│   ├── s_overview.docx      # Shortlist overview (first 6 pages)
│   ├── s_singular_candidate.docx  # Individual candidate profile (3 pages)
│   └── s_end_page.docx      # Shortlist end page
├── data/                     # Candidate and metadata JSON files
│   └── {Role}_{Company}_{Year}/  # Project folders
│       ├── metadata_*.json   # Shortlist metadata
│       ├── {Name}_*.json     # Individual candidates
│       └── merged_*.json     # Combined data for overview
├── outputs/                  # Generated Word documents
│   ├── candidate_reports/   # Standalone candidate reports
│   └── {Project}/           # Shortlist documents by project
└── utils/                    # Utility modules
    ├── shortlist_data.py    # Pydantic data models
    ├── merge_data.py        # JSON data merging
    ├── merge_documents.py   # Word document merging
    └── table_edit.py        # Table formatting and coloring
```

## Key Features

### Shortlist Reports

- Compare up to 10 candidates side-by-side
- Skills assessment matrix with color-coded ratings (1-10 scale)
- Detailed 3-page profiles for each candidate
- Client and consultant team information
- Automated document assembly and formatting

### Candidate Reports

- Comprehensive standalone profiles
- Employment history with achievements
- Education, directorships, and professional development
- Skills assessments and consultant commentary
- Single-step generation process

### Data Management

- Organized folder structure by role, company, and year
- JSON-based candidate data with validation
- Reusable data for both report types
- Automated file naming with timestamps

### Document Processing

- Preserves Word formatting during placeholder replacement
- Handles placeholders split across runs
- Processes tables, headers, footers, and nested structures
- XML-level copying for perfect formatting preservation

## Installation

### Prerequisites

- Python 3.8+
- Required packages (see `/workspace/cr_automation/requirements.txt`)

### Key Dependencies

```
fastmcp>=2.12.3      # MCP server framework
python-docx>=1.2.0   # Word document manipulation
pydantic>=2.11.9     # Data validation
```

### Setup

```bash
# From the cr_automation root directory
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

## Usage

### Running the Server

The server is designed to be used as an MCP server:

```bash
# From the exec_reports directory
python server.py
```

Or configure it as an MCP server in your MCP client configuration.

### Available Tools

The server exposes the following MCP tools:

#### Planning & Information

- `shortlist_report_plan()` - Complete workflow guide for shortlist reports
- `candidate_report_plan()` - Complete workflow guide for candidate reports
- `check_existing_projects()` - List projects and candidate counts
- `read_project_metadata(folder_name)` - View metadata and role skills

#### Shortlist Report Workflow

1. `generate_shortlist_metadata(...)` - Create project metadata
2. `generate_individual_candidate(...)` - Add candidates one by one
3. `merge_shortlist_candidates(folder_name)` - Combine data for overview
4. `generate_overview_document(...)` - Create overview document
5. `generate_candidate_document(...)` - Create individual profiles
6. `merge_shortlist_documents_tool(...)` - Assemble final report
7. `apply_shortlist_table_colors(...)` - Apply color formatting

#### Candidate Report Workflow

1. `generate_individual_candidate(...)` - Create candidate data
2. `process_candidate_report(candidate_data_path)` - Generate report

### Example: Shortlist Report

```python
# Step 1: Create metadata
generate_shortlist_metadata(
    client_company_name="Acme Corporation",
    candidate_target_role="Chief Financial Officer",
    client_1_full_name="Jane Doe",
    client_1_position="CEO",
    consultant_1_name="John Smith",
    consultant_1_position="Senior Consultant",
    role_skill_1="Financial Strategy",
    role_skill_2="Leadership",
    # ... up to role_skill_7
)
# Creates: data/Chief_Financial_Officer_Acme_Corporation_2025/

# Step 2: Add candidates (repeat for 10 candidates)
generate_individual_candidate(
    full_name="Alice Johnson",
    candidate_target_role="Chief Financial Officer",
    client_company_name="Acme Corporation",
    employment_1_company_name="Global Finance Ltd",
    employment_1_job_title="CFO",
    # ... extensive candidate data
)

# Step 3: Merge data
merge_shortlist_candidates("Chief_Financial_Officer_Acme_Corporation_2025")

# Step 4-6: Generate and merge documents
# (See shortlist_report_plan for complete workflow)

# Step 7: Apply colors
apply_shortlist_table_colors(
    folder_name="Chief_Financial_Officer_Acme_Corporation_2025",
    document_path="shortlist_report_merged_20250124_143022.docx"
)
```

### Example: Candidate Report

```python
# Step 1: Create candidate data
generate_individual_candidate(
    full_name="Bob Williams",
    candidate_target_role="CEO",
    client_company_name="Tech Innovations",
    candidate_executive_summary="Bob Williams is an accomplished...",
    # ... comprehensive candidate information
)

# Step 2: Generate report
process_candidate_report(
    candidate_data_path="CEO_Tech_Innovations_2025/Bob_Williams_20250124_143022.json"
)
# Creates: outputs/candidate_reports/Bob_Williams_20250124_143022_report_20250124_143045.docx
```

## Data Models

The system uses Pydantic models for data validation:

### ShortlistMetadata

- Client company and target role information
- Client contacts (up to 3)
- Consultant team (up to 3)
- Role skills for assessment matrix (7 skills)

### UnifiedCandidateData

- Basic information (name, current role, location)
- Employment history (up to 7 positions with detailed information)
- Education (up to 5 qualifications)
- Directorships/committees (up to 3)
- Professional memberships (up to 5)
- Professional development (up to 5)
- Skills assessments (7 skills with ratings and detailed commentary)
- Consultant commentary (3 paragraphs)
- Additional sections (up to 3 custom sections)

## Template System

### Placeholders

Templates use curly brace syntax: `{placeholder_name}`

Example placeholders:

- `{full_name}` - Candidate's full name
- `{company}` - Current company
- `{employment_1_job_title}` - First employment position title
- `{role_skill_1}` - First role skill name
- `{assess_1}` - Rating for first skill (1-10)

### Template Types

**c_template.docx** - Candidate Report Template

- Single comprehensive document
- All candidate fields directly accessible

**s_overview.docx** - Shortlist Overview Template

- Title page, contents, summary matrix
- Uses metadata fields (no prefix) and candidate fields (c1*, c2*, etc.)

**s_singular_candidate.docx** - Candidate Profile Template

- 3-page individual profile
- Uses both metadata and candidate\_ prefixed fields

**s_end_page.docx** - Shortlist End Page

- Contact information and closing

## Color Coding System

Shortlist reports use color-coded rating cells:

| Rating | Color                   | Description          |
| ------ | ----------------------- | -------------------- |
| 1-2    | Light tan (#FADBB7)     | Very Low             |
| 3-4    | Tan (#D1B399)           | Less Than Required   |
| 5-6    | Gold (#BB8E66)          | At Required Level    |
| 7-8    | Orange (#F2BA6E)        | Above Required Level |
| 9-10   | Bright orange (#F97012) | Very High            |

## Best Practices

### Data Quality

- Use web search to verify candidate information
- Fill all fields or use clear placeholders like [CLIENT NAME]
- Provide detailed assessments (2-4 sentences minimum)
- Be critical in ratings - use the full 1-10 scale
- Average candidates should score 5-6, not 9-10

### Folder Organization

- Consistent naming: {Role}_{Company}_{Year}
- One project folder per search assignment
- All candidates for a project in the same folder
- Metadata file required before adding candidates

### Document Assembly

- Always generate overview before candidate documents
- Keep track of candidate document order
- Apply colors as the final step
- Use project-specific output folders

## Troubleshooting

### Common Issues

**"No metadata found"**

- Create metadata with `generate_shortlist_metadata()` first

**"Candidate data file not found"**

- Check file path and folder name
- Use `check_existing_projects()` to see available files

**"Template file not found"**

- Verify templates exist in `templates/` folder
- Check template file names match expectations

**Placeholders not replaced**

- Ensure placeholder names match exactly (case-sensitive)
- Check for typos in field names
- Verify data exists in JSON file

**Colors not applied**

- Run `apply_shortlist_table_colors()` after document generation
- Verify document path is correct
- Check that tables contain numeric ratings

## Development

### Adding New Fields

1. Update `UnifiedCandidateData` model in `utils/shortlist_data.py`
2. Add field to `generate_individual_candidate()` parameters in `server.py`
3. Update template documents to include `{new_field}` placeholder
4. Test with sample data

### Creating New Templates

1. Create Word document with desired formatting
2. Add placeholders using `{field_name}` syntax
3. Save as `.docx` in `templates/` folder
4. Test placeholder replacement with sample data

### Running Tests

```bash
# Test with sample data
python server.py
# Call tools through MCP client

# Manual testing
python replace.py  # Uses hardcoded paths in __main__
```

## Technical Details

### Placeholder Replacement Algorithm

- Handles placeholders split across Word runs (formatting boundaries)
- Preserves all formatting (bold, italic, fonts, colors)
- Processes paragraphs, tables, headers, footers
- Case-sensitive exact matching

### Document Merging

- XML-level element copying for format preservation
- Maintains page breaks between sections
- Preserves table structures, borders, and styling
- Handles nested elements correctly

### Data Merging

- Combines metadata (no prefix) with candidates (c1*, c2*, etc.)
- Sorts candidates by number for consistent ordering
- Excludes already-merged files to prevent duplication
- Validates folder structure and file naming

## Recent Changes: Assessment Data Refactoring

### Overview

Assessment data (ratings, skill assessments, commentary) has been separated from core candidate data to:

- Reduce work for candidate-only reports
- Provide cleaner separation of concerns
- Make assessment data optional and only required for shortlists

### What Changed

1. **New Data Model**: `CandidateAssessment` - Contains all assessment-related fields
2. **Updated Model**: `UnifiedCandidateData` - Assessment fields removed
3. **New Tool**: `generate_candidate_assessments()` - Creates assessment templates
4. **New Utility**: `utils/merge_assessment.py` - Merges candidate and assessment data
5. **Updated Workflow**: Shortlist workflow now has 8 steps (was 7)

### New Workflow

#### Shortlist Reports (with assessments):

```
1. generate_shortlist_metadata() → metadata with role skills
2. generate_individual_candidate() → add candidates (no assessments)
3. generate_candidate_assessments() → create assessment templates ← NEW STEP
4. [Fill in assessment data in JSON files]
5. merge_shortlist_candidates() → merges all data including assessments
6. generate_overview_document() → overview with skills matrix
7. generate_candidate_document() → candidate profiles
8. merge_shortlist_documents_tool() → final assembly
9. apply_shortlist_table_colors() → color formatting
```

#### Candidate Reports (without assessments):

```
1. generate_individual_candidate() → candidate data only
2. process_candidate_report() → generate report
(No assessment data needed!)
```

### File Structure

Projects now contain separate assessment files:

```
data/CEO_Quantium_2025/
├── metadata_Quantium_20250124.json
├── John_Smith_20250124_143022.json                # Candidate data
├── John_Smith_assessment_20250124_150000.json     # Assessment data (NEW)
├── Jane_Doe_20250124_143045.json
└── Jane_Doe_assessment_20250124_150000.json       # Assessment data (NEW)
```

### Benefits

1. **Less Work**: Candidate-only reports don't require role skills or assessments
2. **Flexibility**: Assessment data is optional and created only when needed
3. **Organization**: Clear separation between factual data and evaluation
4. **Automation**: Assessment data automatically merged when generating documents

### Breaking Changes

**`generate_individual_candidate()` - Removed parameters:**

- `assess_1` through `assess_7`
- `role_skill_1_assessment` through `role_skill_7_assessment`
- `consultant_commentary_para_1` through `consultant_commentary_para_3`

**Solution**: Use the new `generate_candidate_assessments()` tool to create assessment data separately.

### Migration Guide

For existing workflows, add the new assessment generation step:

**Old workflow (7 steps):**

```
1. Metadata → 2. Candidates → 3. Merge → 4-7. Generate documents
```

**New workflow (8 steps):**

```
1. Metadata → 2. Candidates → 3. Assessments → 4. Merge → 5-8. Generate documents
```

The merge step automatically combines assessment data with candidate data.

## Related Projects

- `board_reports/` - Similar system for board member reports
- Parent project: CR Automation system

## License

[Add license information]

## Contributors

[Add contributor information]

## Support

For issues or questions:

1. Check the workflow guides: `shortlist_report_plan()` and `candidate_report_plan()`
2. Use `check_existing_projects()` for troubleshooting
3. Review template placeholders against data models
4. Consult the code documentation in `server.py`
