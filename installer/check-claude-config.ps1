# PowerShell script to check if a configuration file exists

# Define the path to the configuration file using environment variables
$configFilePath = "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json"

# Check if the file exists
if (Test-Path -Path $configFilePath) {
    Write-Host "Configuration file exists at: $configFilePath"
    # Add any additional actions you want to perform if the file exists
} else {
    Write-Host "Configuration file not found at: $configFilePath"
    # Add any actions you want to perform if the file doesn't exist
}
