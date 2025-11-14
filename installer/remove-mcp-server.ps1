# PowerShell script to remove an MCP server from Claude configuration JSON
# Usage: .\remove-mcp-server.ps1 -mcpName "graphmcp"

param (
    [Parameter(Mandatory=$true)]
    [string]$mcpName
)

# Path to the configuration file
$configFilePath = "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json"

# Check if the file exists
if (-not (Test-Path -Path $configFilePath)) {
    Write-Host "ERROR: Configuration file not found at: $configFilePath"
    exit 1
}

# Read the current JSON configuration
$config = Get-Content -Path $configFilePath -Raw | ConvertFrom-Json

# Check if the mcpServers property exists
if (-not $config.mcpServers) {
    Write-Host "SKIP: No mcpServers section found in configuration file"
    exit 0
}

# Check if the MCP server exists
if ($config.mcpServers.PSObject.Properties.Name -contains $mcpName) {
    # Remove the property
    $config.mcpServers.PSObject.Properties.Remove($mcpName)
    
    # Convert to JSON and save
    $jsonString = ConvertTo-Json -InputObject $config -Depth 10
    $jsonString | Set-Content -Path $configFilePath
    
    Write-Host "SUCCESS: Successfully removed MCP server '$mcpName' from configuration file"
} else {
    Write-Host "SKIP: MCP server '$mcpName' not found in configuration file"
    exit 0
}
