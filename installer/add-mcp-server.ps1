# PowerShell script to update Claude configuration JSON

# Parameters for the new MCP server entry
param (
    [Parameter(Mandatory=$true)]
    [string]$mcpName,
    
    [Parameter(Mandatory=$true)]
    [string]$mcpCommand,
    
    [Parameter(Mandatory=$true)]
    [string]$envFilePath,
    
    [Parameter(Mandatory=$false)]
    [switch]$withLangfuse,
    
    [Parameter(Mandatory=$false)]
    [int]$indentSize = 4
)

# Path to the configuration file
$configFilePath = "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json"
$backupFilePath = "$configFilePath.backup"

# Function to restore backup on failure
function Restore-Backup {
    if (Test-Path -Path $backupFilePath) {
        Write-Host "Restoring configuration from backup..."
        Copy-Item -Path $backupFilePath -Destination $configFilePath -Force
        Remove-Item -Path $backupFilePath -Force
        Write-Host "Backup restored successfully."
    }
}

# Function to compare MCP server configurations
function Compare-McpConfigurations {
    param (
        [object]$existing,
        [object]$new
    )
    
    # Compare command
    if ($existing.command -ne $new.command) {
        return $false
    }
    
    # Compare args arrays
    if ($existing.args.Count -ne $new.args.Count) {
        return $false
    }
    
    for ($i = 0; $i -lt $existing.args.Count; $i++) {
        if ($existing.args[$i] -ne $new.args[$i]) {
            return $false
        }
    }
    
    return $true
}

try {
    # Check if the directory exists, create it if not
    $configDir = Split-Path -Path $configFilePath -Parent
    if (-not (Test-Path -Path $configDir)) {
        Write-Host "Creating directory: $configDir"
        New-Item -Path $configDir -ItemType Directory -Force | Out-Null
    }

    # Check if the file exists, create it if not
    $configExists = Test-Path -Path $configFilePath
    if (-not $configExists) {
        Write-Host "Configuration file not found. Creating new configuration file..."
        $defaultConfig = @{
            mcpServers = @{}
        }
        $defaultConfigJson = ConvertTo-Json -InputObject $defaultConfig -Depth 10
        $defaultConfigJson | Set-Content -Path $configFilePath
    } else {
        # Create backup of the original file
        Write-Host "Creating backup of configuration file..."
        Copy-Item -Path $configFilePath -Destination $backupFilePath -Force
    }
    
    # Read the current JSON configuration
    $config = Get-Content -Path $configFilePath -Raw | ConvertFrom-Json

    # Check if the mcpServers property exists
    if (-not $config.mcpServers) {
        $config | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{}
    }

    # Build the args array based on parameters
    $argsArray = @("--env-file", $envFilePath)
    if ($withLangfuse) {
        $argsArray += "--with-langfuse"
        Write-Host "Adding --with-langfuse flag to MCP server configuration"
    }

    # Create the new MCP server entry
    $newMcpEntry = @{
        command = $mcpCommand
        args = $argsArray
    }

    # Check if the MCP server already exists
    if ($config.mcpServers.PSObject.Properties.Name -contains $mcpName) {
        Write-Host "MCP server '$mcpName' already exists. Checking for differences..."
        
        $existingEntry = $config.mcpServers.$mcpName
        
        # Compare configurations
        if (Compare-McpConfigurations -existing $existingEntry -new $newMcpEntry) {
            Write-Host "SKIP: MCP server '$mcpName' already has the same configuration"
            # Remove backup if it exists since no changes were made
            if (Test-Path -Path $backupFilePath) {
                Remove-Item -Path $backupFilePath -Force
            }
            exit 0
        } else {
            Write-Host "UPDATE: [$($existingEntry.command) $($existingEntry.args -join ' ')] -> [$($newMcpEntry.command) $($newMcpEntry.args -join ' ')]"

            # Update the existing entry
            $config.mcpServers.$mcpName = $newMcpEntry
            $actionTaken = "Updated"
        }
    } else {
        Write-Host "Adding new MCP server '$mcpName'..."
        # Add the new MCP server to the configuration
        $config.mcpServers | Add-Member -NotePropertyName $mcpName -NotePropertyValue $newMcpEntry -Force
        $actionTaken = "Added"
    }

    # Convert to JSON with specified indentation
    $jsonString = ConvertTo-Json -InputObject $config -Depth 10

    # Save the file
    $jsonString | Set-Content -Path $configFilePath

    # Remove backup after successful operation if it exists
    if (Test-Path -Path $backupFilePath) {
        Remove-Item -Path $backupFilePath -Force
    }
    
    Write-Host "SUCCESS: Successfully $($actionTaken.ToLower()) MCP server '$mcpName' in configuration file"
} catch {
    Write-Host "ERROR: Failed to update configuration file: $_"
    # Restore from backup if it exists
    Restore-Backup
    exit 1
}

# Add a trap to ensure backup is restored even if script is terminated unexpectedly
trap {
    Write-Host "ERROR: Script terminated unexpectedly: $_"
    Restore-Backup
    exit 1
}
