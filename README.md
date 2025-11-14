# Installer V4 - Windows NSIS Installer for Executive Reports MCP

This directory contains the NSIS-based Windows installer for the Executive Reports MCP Server, following the proven pattern from genaicore-genaicore-claude-mcpservers.

## Overview

The installer v4 uses the **NSIS (Nullsoft Scriptable Install System)** to create a professional Windows installer that:

- ✅ Bundles Python runtime with PyInstaller (no Python required on target machine)
- ✅ Automatically configures Claude Desktop
- ✅ Detects admin/user privileges and installs to appropriate location
- ✅ Checks if Claude is running before installation
- ✅ Creates uninstaller for clean removal
- ✅ Integrates with GitHub Actions for automated builds

## Directory Structure

```
installer_v4/
├── exec_reports/              # Main package directory
│   ├── server.py             # FastMCP server (entry point)
│   ├── replace.py            # Template processing engine
│   ├── templates/            # Word document templates
│   ├── utils/                # Supporting modules
│   ├── data/                 # JSON data storage
│   ├── pyproject.toml        # Version and dependency management
│   ├── file_version_info.txt # Windows executable metadata
│   ├── installer.nsi         # NSIS installer configuration
│   └── .env.template         # Environment template
│
└── installer/                 # Shared installation scripts
    ├── common-mcp-install.nsh    # NSIS template (339 lines)
    ├── add-mcp-server.ps1        # Adds MCP to Claude config
    ├── remove-mcp-server.ps1     # Removes MCP from Claude config
    ├── check-claude-config.ps1   # Validates Claude config exists
    └── postinstall               # macOS postinstall script
```

## Architecture

### NSIS Installer Flow

1. **Welcome Page** - User greeting
2. **Claude Process Check** - Verifies Claude Desktop is not running
   - Silent mode: Auto-closes Claude
   - Interactive: Prompts user to close Claude
3. **Directory Selection** - Choose install location
   - Admin: `C:\Program Files\Exec-Reports-MCP-Server`
   - User: `%LOCALAPPDATA%\Exec-Reports-MCP-Server`
4. **Installation** - Copies files and runs configuration scripts
5. **Finish Page** - Installation complete

### Components

#### 1. Package Configuration (`exec_reports/installer.nsi`)

Minimal 15-line file that defines:
- `PRODUCT_NAME` - "Executive Reports MCP Server"
- `PRODUCT_SHORT_NAME` - "Exec-Reports-MCP-Server"
- `DEFAULT_MCP_NAME` - "exec-reports-mcp" (name in Claude config)
- `PROCESS_NAME` - "server" (process to check/kill)
- `INSTALLER_DIR` - "../installer" (path to PowerShell scripts)

#### 2. Common NSIS Template (`installer/common-mcp-install.nsh`)

Shared 339-line template providing:
- Installation wizard pages
- Claude process detection
- Privilege-based install location detection
- PowerShell script execution
- Uninstaller creation

#### 3. PowerShell Scripts (`installer/*.ps1`)

**add-mcp-server.ps1** (158 lines):
- Modifies `%APPDATA%\Roaming\Claude\claude_desktop_config.json`
- Creates backup before changes
- Compares existing vs new config (skip if identical)
- Adds MCP server entry with command and args
- Automatic rollback on error

**check-claude-config.ps1** (14 lines):
- Validates Claude config directory exists
- Returns exit code 0 on success

**remove-mcp-server.ps1** (41 lines):
- Reads MCP name from `mcpconfig.txt`
- Removes MCP server entry from Claude config
- Safe handling if config doesn't exist

#### 4. Version Management (`exec_reports/pyproject.toml`)

Single source of truth for:
- Version number (e.g., "1.0.0")
- Package name ("exec-reports-mcp")
- Dependencies
- Metadata (author, license, description)

The GitHub Actions workflow automatically extracts the version from this file.

#### 5. PyInstaller Metadata (`exec_reports/file_version_info.txt`)

Windows executable metadata displayed in file properties:
- Company: Quantium
- Product: Executive Reports MCP
- Version: 1.0.0
- Copyright: © 2025 Quantium

## Building the Installer

### Prerequisites

- Windows machine (or GitHub Actions)
- Python 3.10+
- NSIS 3.08
- PyInstaller

### Manual Build

```powershell
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller tomlkit

# 2. Navigate to package directory
cd installer_v4/exec_reports

# 3. Build with PyInstaller
pyinstaller --version-file=file_version_info.txt `
  --add-data "templates;templates" `
  --add-data "utils;utils" `
  --add-data "data;data" `
  --hidden-import=fastmcp `
  --hidden-import=pydantic `
  --hidden-import=docx `
  --hidden-import=lxml `
  server.py `
  --noconfirm

# 4. Create .env file
"# Executive Reports Configuration" | Out-File -FilePath ./.env -Encoding utf8

# 5. Build NSIS installer
& "C:\Program Files (x86)\NSIS\makensis.exe" /DVERSION="1.0.0" ./installer.nsi

# 6. Output: Exec-Reports-MCP-ServerInstaller-1.0.0-setup.exe
```

### Automated Build (GitHub Actions)

Trigger the workflow:
1. **Push to main/master** - Automatically builds on code changes
2. **Manual dispatch** - Go to Actions → "Build Windows Installer" → Run workflow
3. **With release** - Specify a release tag to upload to GitHub releases

The workflow:
- Runs on `windows-latest`
- Installs Python 3.10 and NSIS
- Extracts version from `pyproject.toml`
- Runs PyInstaller
- Builds NSIS installer
- Uploads artifact (90-day retention)
- Optionally uploads to GitHub release

## Installation Behavior

### User Installation

1. Runs `Exec-Reports-MCP-ServerInstaller-1.0.0-setup.exe`
2. Checks if Claude Desktop is running (prompts to close)
3. Detects user privileges:
   - **Admin**: Installs to `C:\Program Files\Exec-Reports-MCP-Server`
   - **User**: Installs to `%LOCALAPPDATA%\Exec-Reports-MCP-Server`
4. Copies PyInstaller bundle (server.exe + dependencies)
5. Copies `.env` file
6. Copies PowerShell scripts
7. Runs `check-claude-config.ps1` to verify Claude config
8. Runs `add-mcp-server.ps1` to add MCP server entry:
   ```json
   {
     "mcpServers": {
       "exec-reports-mcp": {
         "command": "C:\\Program Files\\Exec-Reports-MCP-Server\\server\\server.exe",
         "args": ["--env-file", "C:\\Program Files\\Exec-Reports-MCP-Server\\.env"]
       }
     }
   }
   ```
9. Creates `uninstall.exe`
10. Saves MCP name to `mcpconfig.txt` for uninstaller

### Silent Installation

```powershell
# Silent install
Exec-Reports-MCP-ServerInstaller-1.0.0-setup.exe /S

# Silent uninstall
"C:\Program Files\Exec-Reports-MCP-Server\uninstall.exe" /S
```

Silent mode automatically closes Claude Desktop if running.

### Uninstallation

1. Checks if Claude is running
2. Reads MCP name from `mcpconfig.txt`
3. Runs `remove-mcp-server.ps1` to remove MCP entry
4. Deletes all files and directories

## Customization

### Change Product Names

Edit `exec_reports/installer.nsi`:
```nsis
!define PRODUCT_NAME "Your Product Name"
!define PRODUCT_SHORT_NAME "Your-Product-Name"
!define DEFAULT_MCP_NAME "your-mcp-name"
```

### Change Version

Edit `exec_reports/pyproject.toml`:
```toml
[project]
version = "1.1.0"
```

Version is automatically used in:
- Installer filename
- Windows executable metadata
- GitHub release tags

### Add Dependencies

Edit `exec_reports/pyproject.toml`:
```toml
dependencies = [
    "fastmcp>=2.12.3",
    "your-package>=1.0.0",
]
```

Then update PyInstaller hidden imports in `.github/workflows/create-windows-installer.yml`:
```yaml
pyinstaller --hidden-import=your_package ...
```

### Add Environment Variables

Edit `exec_reports/.env.template`:
```bash
API_KEY=your_api_key
DATABASE_URL=your_database_url
```

These will be bundled with the installer.

## Comparison to Other Installer Versions

| Feature | installer_v2 | installer_v3 | **installer_v4** |
|---------|-------------|-------------|------------------|
| **Technology** | PyInstaller + Custom | Inno Setup | **NSIS** |
| **Template System** | No | No | **Yes (reusable)** |
| **Auto Version** | No | Partial | **Yes (from pyproject.toml)** |
| **Claude Config** | Manual | Custom | **PowerShell scripts** |
| **Privilege Detection** | No | No | **Yes (runtime)** |
| **Silent Mode** | No | Yes | **Yes (auto-close Claude)** |
| **GitHub Actions** | No | No | **Yes (full automation)** |
| **Proven Pattern** | No | No | **Yes (genaicore)** |

## Testing

### Local Testing

1. Build installer manually (see "Manual Build" above)
2. Run installer on clean Windows VM
3. Verify:
   - ✅ Installer runs without errors
   - ✅ Files copied to correct location
   - ✅ Claude Desktop config updated
   - ✅ Server executable runs: `server.exe`
   - ✅ Uninstaller works correctly

### GitHub Actions Testing

1. Push changes to `installer_v4/` directory
2. Check Actions tab for workflow run
3. Download artifact from workflow
4. Test installer on Windows machine

## Troubleshooting

### NSIS Errors

**Error: "Can't open installer.nsi"**
- Check file exists at `installer_v4/exec_reports/installer.nsi`
- Verify working directory is correct

**Error: "Can't find common-mcp-install.nsh"**
- Verify `INSTALLER_DIR` path in installer.nsi
- Check `installer/common-mcp-install.nsh` exists

### PyInstaller Errors

**Error: "Module not found"**
- Add to `--hidden-import` in workflow
- Check dependency is installed

**Error: "FileNotFoundError: templates"**
- Verify `--add-data "templates;templates"` in PyInstaller command
- Check templates directory exists

### PowerShell Script Errors

**Error: "Configuration file not found"**
- Claude Desktop may not be installed
- Check path: `%APPDATA%\Roaming\Claude\claude_desktop_config.json`

**Error: "Access denied"**
- Run installer as administrator
- Or install to user directory (%LOCALAPPDATA%)

## Migration from Previous Versions

### From installer_v2

1. Copy source files to `installer_v4/exec_reports/`
2. Create `pyproject.toml` with version info
3. Create `file_version_info.txt`
4. Create `installer.nsi` (use template above)
5. No need to modify source code

### From installer_v3 (Inno Setup)

1. Copy source files to `installer_v4/exec_reports/`
2. Replace `.iss` file with `installer.nsi`
3. Create `pyproject.toml`
4. PowerShell scripts remain similar

## Resources

- **NSIS Documentation**: https://nsis.sourceforge.io/Docs/
- **PyInstaller Guide**: https://pyinstaller.org/en/stable/
- **Reference Implementation**: `/workspace/genaicore-genaicore-claude-mcpservers/`
- **GitHub Actions Docs**: https://docs.github.com/en/actions

## Maintenance

### Regular Updates

- Keep dependencies updated in `pyproject.toml`
- Test with new Claude Desktop versions
- Update Windows metadata in `file_version_info.txt`

### Version Bumping

1. Update version in `pyproject.toml`
2. Commit changes
3. Push to trigger build
4. Tag release: `git tag exec-reports-mcp-v1.1.0 && git push --tags`

## Success Criteria

- ✅ Installer builds without errors
- ✅ Runs on clean Windows 10/11
- ✅ No Python installation required
- ✅ Claude Desktop config updated correctly
- ✅ Server executable runs: `server.exe`
- ✅ All MCP tools work through Claude Desktop
- ✅ Uninstaller removes all files and config entries
- ✅ Silent installation works
- ✅ GitHub Actions workflow succeeds

## Status

**Current Version**: 1.0.0
**Status**: ✅ Ready for testing
**Last Updated**: 2025-11-12
**Technology**: NSIS 3.08 + PyInstaller + PowerShell + GitHub Actions

---

**Next Steps:**
1. Test manual build locally
2. Push to GitHub to trigger automated build
3. Download artifact and test on Windows VM
4. Create GitHub release with installer
5. Distribute to users
