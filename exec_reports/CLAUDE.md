# Claude Code Instructions for Executive Reports

This file provides specific guidance for working with the Executive Reports MCP server codebase.

## Project Overview

The Executive Reports system is an MCP (Model Context Protocol) server built with FastMCP that automates the generation of professional executive recruitment reports. It processes candidate data and generates formatted Word documents for two use cases:

1. **Shortlist Reports**: Compare 10 candidates with skills matrices (7-step workflow)
2. **Candidate Reports**: Standalone detailed profiles (2-step workflow)

## MCP Usage Logging

All MCP tool invocations are automatically logged to a database for usage tracking, analytics, and audit purposes.

### Database Location

- **SQLite (default)**: `exec_reports/mcp_usage.db`
- **SQL Server (future)**: Configure via environment variables (see below)

### Logged Information

Each tool call records:
- **timestamp**: ISO format UTC timestamp
- **tool_name**: Name of the MCP tool invoked
- **parameters**: Full JSON of all input parameters
- **user_info**: Client/user context (username, hostname, platform)
- **success**: Boolean indicating if tool executed successfully
- **error_message**: Full error message if tool failed
- **execution_time_ms**: How long the tool took to execute (milliseconds)
- **output_preview**: First 500 characters of the tool's return value

### Configuration

#### SQLite (Default)
No configuration required. Database is created automatically on first use at:
```
/workspace/cr_automation/src/exec_reports/mcp_usage.db
```

#### SQL Server Migration (Future)
Set environment variables to switch from SQLite to SQL Server:

```bash
export DB_TYPE=sqlserver
export DB_HOST=your-server.database.windows.net
export DB_NAME=exec_reports_logs
export DB_USER=admin_user
export DB_PASSWORD=your_password
export DB_PORT=1433  # Optional, defaults to 1433
```

**Note**: SQL Server support requires `pyodbc`. Install with:
```bash
pip install pyodbc>=4.0.39
```

### Error Handling

If logging fails (database locked, disk full, connection error):
- Tool execution continues normally (logging failure doesn't break functionality)
- A warning message is appended to the tool's return value
- Error details are printed to stderr for debugging
- After 5 consecutive logging failures, logging is automatically disabled

### Querying Logs

#### Using Python
```python
import sqlite3
import json

conn = sqlite3.connect('exec_reports/mcp_usage.db')
cursor = conn.cursor()

# Get most recent tool calls
cursor.execute("""
    SELECT timestamp, tool_name, success, execution_time_ms
    FROM usage_logs
    ORDER BY timestamp DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} - {'✓' if row[2] else '✗'} ({row[3]}ms)")

conn.close()
```

#### Common Queries

**Most used tools:**
```sql
SELECT tool_name, COUNT(*) as usage_count
FROM usage_logs
GROUP BY tool_name
ORDER BY usage_count DESC;
```

**Error rate by tool:**
```sql
SELECT
    tool_name,
    COUNT(*) as total_calls,
    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures,
    ROUND(100.0 * SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate_pct
FROM usage_logs
GROUP BY tool_name
ORDER BY error_rate_pct DESC;
```

**Average execution time by tool:**
```sql
SELECT
    tool_name,
    AVG(execution_time_ms) as avg_ms,
    MIN(execution_time_ms) as min_ms,
    MAX(execution_time_ms) as max_ms,
    COUNT(*) as sample_size
FROM usage_logs
WHERE success = 1
GROUP BY tool_name
ORDER BY avg_ms DESC;
```

**Recent errors:**
```sql
SELECT timestamp, tool_name, error_message, parameters
FROM usage_logs
WHERE success = 0
ORDER BY timestamp DESC
LIMIT 20;
```

### Privacy & Security Considerations

**Full parameter logging**: All input parameters are logged in JSON format. This includes:
- Candidate names and personal information
- Company names and client details
- All assessment data and commentary

**Recommendations**:
- Restrict database file access to authorized users only
- Set appropriate file permissions: `chmod 600 mcp_usage.db`
- For production deployments with sensitive data:
  - Use SQL Server with encryption at rest
  - Implement row-level security
  - Set up regular backup procedures
  - Consider implementing data retention policies

### Technical Implementation

**Decorator-based logging** (`utils/mcp_logging.py`):
- `@log_mcp_tool` decorator wraps all MCP tool functions
- Automatically captures parameters using function signature inspection
- Measures execution time with microsecond precision
- Handles both successful and failed executions
- Supports both sync and async tools (use `@log_mcp_tool_async` for async)

**Database module** (`utils/logging_db.py`):
- `DatabaseLogger` class manages connections and schema
- Automatic schema initialization on first use
- Connection pooling not needed (SQLite uses file locking)
- SQL Server support uses `pyodbc` with parameterized queries
- Graceful degradation: errors don't affect tool functionality

### Maintenance

**Database growth**: Monitor database size over time. For high-traffic deployments:
```bash
# Check database size
ls -lh exec_reports/mcp_usage.db

# Archive old logs (example: move logs older than 90 days)
sqlite3 mcp_usage.db "DELETE FROM usage_logs WHERE timestamp < datetime('now', '-90 days')"
sqlite3 mcp_usage.db "VACUUM"
```

**Backup**: Regular backups recommended for audit trail:
```bash
# SQLite backup
cp mcp_usage.db "mcp_usage_backup_$(date +%Y%m%d).db"

# Or export to JSON
python -c "
import sqlite3, json
conn = sqlite3.connect('mcp_usage.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM usage_logs')
columns = [desc[0] for desc in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
with open('usage_logs_export.json', 'w') as f:
    json.dump(rows, f, indent=2)
"
```

## Architecture

### Core Components

- **server.py** (1630 lines): Main MCP server with tool definitions
  - 15+ MCP tools for report generation workflow
  - Built on FastMCP framework
  - Manages paths, data directories, and orchestration

- **replace.py** (180 lines): Template processing engine
  - `replace_text_in_runs()`: Handles placeholders split across Word runs
  - `replace_all_text()`: Processes entire document (paragraphs, tables, headers, footers)
  - `process_document_template()`: Main entry point for template processing

- **utils/shortlist_data.py**: Pydantic data models
  - `ShortlistMetadata`: Project-level metadata (client, consultants, skills)
  - `UnifiedCandidateData`: Comprehensive candidate data structure

- **utils/merge_data.py**: JSON file merging
  - `merge_candidates_data()`: Combines metadata + candidates into single JSON
  - Prefixes candidates as c1_, c2_, c3_, etc.

- **utils/merge_documents.py**: Word document assembly
  - XML-level copying for perfect format preservation
  - Combines overview + candidate profiles + end page

- **utils/table_edit.py**: Table formatting and coloring
  - Color-codes rating cells based on 1-10 scale
  - Creates bar chart effects in candidate detail tables

### Data Flow

```
1. Metadata JSON → data/{Role}_{Company}_{Year}/
2. Individual Candidate JSONs → same folder
3. Merge JSONs → merged_candidates_*.json
4. Template + JSON → process_document_template() → Word docs
5. Merge Word docs → final report
6. Apply colors → finished deliverable
```

### Directory Structure

```
exec_reports/
├── templates/          # Word templates with {placeholder} syntax
├── data/              # JSON files organized by project
│   └── {Role}_{Company}_{Year}/
├── outputs/           # Generated Word documents
│   ├── candidate_reports/
│   └── {ProjectName}/
└── utils/             # Supporting modules
```

## Working with This Codebase

### Key Design Patterns

1. **Path Resolution**: Tools accept both absolute and relative paths
   - Relative paths resolve to `data/` or `outputs/` automatically
   - Use `Path` objects for cross-platform compatibility

2. **JSON-based Data**: All candidate data stored as JSON
   - Validated against Pydantic models
   - Timestamped filenames for versioning
   - Organized into project folders

3. **Template Processing**: Placeholder replacement preserves formatting
   - Handles placeholders split across runs (Word formatting boundaries)
   - Processes all document parts (body, tables, headers, footers)
   - Case-sensitive exact matching

4. **Tool Composition**: Complex workflows built from simple tools
   - Each tool does one thing well
   - Tools chain together for complete workflows
   - Planning tools provide guidance

### Important Implementation Details

#### Placeholder Replacement (replace.py)
The most complex part is handling placeholders split across runs:

```python
# Word may split "{full_name}" across runs:
# Run 1: "{full_"
# Run 2: "name}"

# Algorithm:
# 1. Try simple replacement within runs
# 2. Reconstruct full text from all runs
# 3. Find placeholder positions
# 4. Replace across affected runs
```

**Why this matters**: Never modify `replace_text_in_runs()` without thorough testing, as Word's run structure is fragile.

#### Data Merging (merge_data.py)
Combines metadata and candidates for overview document:

```python
# Result structure:
{
  "client_company_name": "...",      # From metadata (no prefix)
  "role_skill_1": "...",             # From metadata
  "c1_full_name": "...",             # Candidate 1 (prefixed)
  "c1_employment_1_company": "...",  # Nested candidate data
  "c2_full_name": "...",             # Candidate 2
  # ... up to c10_
}
```

**Why this matters**: Templates must use correct prefixes (none for metadata, c1_/c2_/etc for candidates).

#### Document Merging (merge_documents.py)
Uses XML-level copying to preserve all formatting:

```python
# Copies elements, not content:
new_element = deepcopy(source._element)
target_doc._element.body.append(new_element)
```

**Why this matters**: Never use text-based copying - will lose formatting, tables, images, etc.

### Common Tasks

#### Adding a New MCP Tool

1. Add function with `@mcp.tool()` decorator in server.py
2. Provide comprehensive docstring (users see this!)
3. Add type hints for all parameters
4. Return JSON strings or plain text messages
5. Handle path resolution (relative to BASE_DIR, DATA_DIR, OUTPUTS_DIR)
6. Include error handling with helpful messages

Example:
```python
@mcp.tool()
def new_tool_name(
    required_param: str,
    optional_param: str = ""
) -> str:
    """
    Brief description of what this tool does.

    Detailed explanation of purpose and use cases.

    Args:
        required_param: What this parameter is for
        optional_param: What this optional parameter does

    Returns:
        Description of return value
    """
    try:
        # Implementation
        return f"Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

#### Adding New Candidate Fields

1. Update `UnifiedCandidateData` in `utils/shortlist_data.py`:
```python
new_field: str = Field(default="", description="Description of field")
```

2. Add parameter to `generate_individual_candidate()` in server.py:
```python
def generate_individual_candidate(
    # ... existing params
    new_field: str = "",
):
```

3. Add to data structure construction:
```python
candidate_data = UnifiedCandidateData(
    # ... existing fields
    new_field=new_field,
)
```

4. Update templates to include `{new_field}` placeholder

5. Test with sample data

#### Modifying Templates

Templates are Word documents with placeholders in `{field_name}` format.

**Important**:
- Use exact field names from Pydantic models
- Case-sensitive matching
- No spaces in placeholder names
- Test placeholder replacement with sample data
- For shortlist overview: metadata fields (no prefix), candidate fields (c1_, c2_, etc.)
- For candidate profiles: metadata (no prefix), candidate fields (candidate_ prefix)

#### Debugging Template Issues

```python
# Add debug output in replace.py:
print(f"Replacing: {placeholder} -> {value}")

# Or log all replacements:
replacements = {f'{{{k}}}': str(v) for k, v in data.items()}
print(f"Total replacements: {len(replacements)}")
```

**Common issues**:
- Placeholder not found: Check spelling, case, field name
- Partial replacement: Placeholder might be split across runs
- Missing data: Check JSON file has the field
- Wrong prefix: Verify template context (overview vs candidate profile)

### Testing

#### Manual Testing
```bash
# 1. Run server
python server.py

# 2. Use MCP client to call tools
# Example: generate_shortlist_metadata(...)

# 3. Check outputs
ls outputs/
ls data/
```

#### Test Data
Sample data exists in:
- `data/Chief_Financial_Officer_QBE_Insurance_Group_2025/`
- `data/Chief_Financial_Officer_Private_Health_Insurance_Sector_2025/`

#### Validation Points
- JSON files validate against Pydantic models
- File paths resolve correctly
- Templates exist and are accessible
- Placeholders match data model fields
- Output documents open without errors
- Formatting preserved after processing

## Code Standards

### Python Style
- Follow PEP 8
- Type hints on all function parameters and returns
- Docstrings for all MCP tools (user-facing)
- Clear variable names (avoid abbreviations)
- Error handling with informative messages

### Naming Conventions
- Files: `snake_case.py`
- Functions: `snake_case()`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- MCP tools: `descriptive_action_name()` (e.g., `generate_overview_document`)

### Path Handling
Always use `pathlib.Path` for cross-platform compatibility:

```python
# Good
from pathlib import Path
data_path = Path(candidate_data_path)
if not data_path.is_absolute():
    data_path = DATA_DIR / candidate_data_path

# Bad
import os
data_path = os.path.join("data", candidate_data_path)
```

### Error Messages
Provide actionable error messages:

```python
# Good
return f"Candidate data file not found: {data_path}\nAvailable files: {list(DATA_DIR.glob('*.json'))}"

# Bad
return "File not found"
```

## Security Considerations

### Input Validation
- All inputs validated through Pydantic models
- File paths validated to prevent directory traversal
- JSON parsing wrapped in try/except

### File Operations
- All file operations restricted to project directories
- Use `Path.resolve()` to normalize paths
- Check file existence before operations

### Dependencies
This project uses `python-docx` for Word document manipulation. This library:
- Parses Office Open XML format (DOCX files)
- Does NOT execute macros or embedded code
- Safe for processing untrusted documents (read-only operations)
- No known security vulnerabilities in version 1.2.0+

**Note**: The XML-level copying in `merge_documents.py` is safe because:
- It copies document structure, not executable code
- DOCX format is XML-based, not executable
- No macro or VBA support in python-docx

## Common Pitfalls

### 1. Run Splitting in Word Documents
**Problem**: Word splits text at formatting boundaries, breaking placeholders.

**Solution**: Use `replace_text_in_runs()` which handles this automatically.

**Don't**: Simple string replacement on run text.

### 2. Template Prefix Confusion
**Problem**: Using wrong prefix in templates (c1_ vs candidate_ vs none).

**Context matters**:
- Overview document: metadata (no prefix), candidates (c1_, c2_, ...)
- Candidate profile: metadata (no prefix), candidate (candidate_ prefix)
- Standalone candidate report: candidate (no prefix)

### 3. Path Resolution
**Problem**: Hard-coded paths break across environments.

**Solution**: Use relative paths that resolve automatically:
```python
# Tool accepts: "folder/file.json"
# Code resolves: DATA_DIR / "folder" / "file.json"
```

### 4. Data Model Changes
**Problem**: Adding field to model but forgetting to update tool parameters.

**Checklist**:
- [ ] Add to Pydantic model
- [ ] Add to tool parameters
- [ ] Add to data structure construction
- [ ] Update template
- [ ] Test end-to-end

### 5. Document Merging Order
**Problem**: Documents assembled in wrong order.

**Correct order**:
1. Overview (6 pages)
2. Candidate profiles (3 pages each, in order)
3. End page

**Why it matters**: Page numbers and table of contents rely on correct order.

## Extension Points

### Adding New Report Types
1. Create new template in `templates/`
2. Add tool to `server.py` with `@mcp.tool()`
3. Reuse `process_document_template()` for processing
4. Add to appropriate planning tool

### Custom Document Processing
Override `process_document_template()` for custom logic:
```python
def custom_process_document(data_path, template_path, output_dir):
    # Custom preprocessing
    data = custom_transform(load_json(data_path))

    # Use standard processing
    result = process_document_template(
        candidate_data_path=data_path,
        template_path=template_path,
        output_dir=output_dir
    )

    # Custom postprocessing
    if result["success"]:
        apply_custom_formatting(result["output_file"])

    return result
```

### Adding New Utility Functions
Add to appropriate module in `utils/`:
- `shortlist_data.py`: Data models and validation
- `merge_data.py`: JSON operations
- `merge_documents.py`: Word document operations
- `table_edit.py`: Table formatting

## Performance Considerations

### Document Processing
- Template processing is I/O bound (reading/writing files)
- XML parsing is CPU intensive for large documents
- Keep templates under 50 pages for best performance

### Data Operations
- JSON parsing is fast (< 100ms for typical files)
- Pydantic validation adds minimal overhead
- File system operations dominate timing

### Optimization Opportunities
- Cache template documents if processing multiple candidates
- Batch document operations when possible
- Use async/await for I/O operations (FastMCP supports this)

## Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Generated JSON
```python
import json
from pathlib import Path

# Pretty-print JSON
with open('data/project/candidate.json') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2))
```

### Check Document Structure
```python
from docx import Document

doc = Document('template.docx')
for i, para in enumerate(doc.paragraphs):
    print(f"{i}: {para.text[:50]}")
```

### Trace Placeholder Replacement
Add print statements in `replace_text_in_runs()` to see what's being replaced.

## Resources

### Documentation
- FastMCP: https://github.com/jlowin/fastmcp
- python-docx: https://python-docx.readthedocs.io/
- Pydantic: https://docs.pydantic.dev/

### Related Code
- `board_reports/`: Similar system for board reports (reference implementation)
- Parent project: CR Automation system

### Templates
- Located in `templates/` folder
- Open in Microsoft Word to view structure
- Placeholders use `{field_name}` syntax

## Questions & Support

When asking questions about this codebase:

1. **Workflow questions**: Refer to `shortlist_report_plan()` or `candidate_report_plan()` outputs
2. **Data structure questions**: Check Pydantic models in `utils/shortlist_data.py`
3. **Template questions**: Open template in Word and check placeholders
4. **File location questions**: Use `check_existing_projects()` tool
5. **Error messages**: Include full error text and context

## Key Takeaways

1. **MCP Server**: FastMCP-based tool server, not a web service
2. **Two Workflows**: Shortlist (complex, 7 steps) vs Candidate (simple, 2 steps)
3. **JSON Data**: All data stored as validated JSON files
4. **Template Processing**: Preserves formatting through XML-level operations
5. **Organized Structure**: Project folders keep related files together
6. **Tool Composition**: Simple tools combine for complex workflows

## Maintenance

### Regular Updates
- Keep dependencies up to date (especially fastmcp, python-docx)
- Test with new Word template versions
- Validate sample data against current models

### Known Issues
- None currently documented

### Future Enhancements
- Async document processing for better performance
- Template validation tool
- Data migration utilities for model changes
- Automated testing suite
