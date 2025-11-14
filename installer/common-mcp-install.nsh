; Common MCP Server installer template
; This file contains all the shared logic for MCP Server installers
; Include this file after defining the required constants

!ifndef COMMON_MCP_INSTALLER_NSH
!define COMMON_MCP_INSTALLER_NSH

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"

; Validate required defines
!ifndef PRODUCT_NAME
  !error "PRODUCT_NAME must be defined before including common-mcp-installer.nsh"
!endif
!ifndef PRODUCT_SHORT_NAME
  !error "PRODUCT_SHORT_NAME must be defined before including common-mcp-installer.nsh"
!endif
!ifndef DEFAULT_MCP_NAME
  !error "DEFAULT_MCP_NAME must be defined before including common-mcp-installer.nsh"
!endif
!ifndef PRODUCT_START_MENU_DIR
  !error "PRODUCT_START_MENU_DIR must be defined before including common-mcp-installer.nsh"
!endif
!ifndef PROCESS_NAME
  !error "PROCESS_NAME must be defined before including common-mcp-installer.nsh"
!endif

; Make INSTALL_LOCATION optional - use runtime detection if not defined
!ifndef INSTALL_LOCATION
  !define USE_RUNTIME_DETECTION
!endif
!ifndef INSTALLER_DIR
  !error "INSTALLER_DIR must be defined (path to PowerShell scripts directory)"
!endif

; Installer attributes
Name "${PRODUCT_NAME} ${VERSION}"
OutFile "${PRODUCT_SHORT_NAME}Installer-${VERSION}-setup.exe"

; Set default install directory and execution level
!ifdef USE_RUNTIME_DETECTION
  InstallDir "$PROGRAMFILES64\${PRODUCT_SHORT_NAME}"  ; Default fallback
  RequestExecutionLevel user  ; Will handle elevation in .onInit if needed
!else
  InstallDir "${INSTALL_LOCATION}\${PRODUCT_SHORT_NAME}"
  ; Set execution level based on install location
  !if `${INSTALL_LOCATION}` == `$PROGRAMFILES64`
    RequestExecutionLevel admin
  !else
    RequestExecutionLevel user
  !endif
!endif

; MUI Settings
!define MUI_ABORTWARNING

; Define mcpName as a global variable
Var mcpName

; Custom variables
Var Dialog
Var IsClaudeRunning

; Check if Claude is running function
Function CheckClaudeProcess
    nsExec::ExecToLog 'PowerShell -Command "if(Get-Process claude -ErrorAction SilentlyContinue){exit 1}else{exit 0}"'
    Pop $IsClaudeRunning

    ; In silent mode, try to close Claude automatically
    ${If} ${Silent}
        ${If} $IsClaudeRunning == "1"
            DetailPrint "Claude is running. Closing automatically for silent install..."
            nsExec::ExecToLog 'PowerShell -Command "Stop-Process -Name claude -Force -ErrorAction SilentlyContinue"'
            Sleep 2000
            
            ; Check again
            nsExec::ExecToLog 'PowerShell -Command "if(Get-Process claude -ErrorAction SilentlyContinue){exit 1}else{exit 0}"'
            Pop $IsClaudeRunning
            
            ${If} $IsClaudeRunning == "1"
                DetailPrint "Warning: Could not close Claude automatically"
                ; Continue anyway - don't fail the silent install
            ${Else}
                DetailPrint "Claude closed successfully"
            ${EndIf}
        ${EndIf}
    ${EndIf}
FunctionEnd

; Custom page for Claude check
Function ClaudeCheckPage
    ; First check if Claude is running
    Call CheckClaudeProcess
    
    ; If Claude is not running, skip this page entirely
    ${If} $IsClaudeRunning == "0"
        Abort ; Skip to next page
    ${EndIf}
    
    ; If we get here, Claude is running - show warning page
    nsDialogs::Create 1018
    Pop $Dialog
    
    ${If} $Dialog == error
        Abort
    ${EndIf}
    
    ${NSD_CreateLabel} 0 0 100% 20u "Claude is currently running"
    Pop $0
    
    ${NSD_CreateLabel} 0 25u 100% 60u "Please close Claude before continuing with the installation.$\r$\n$\r$\nClick Retry after closing Claude, or Cancel to exit the installer."
    Pop $0
    
    ${NSD_CreateButton} 50u 100u 50u 15u "Retry"
    Pop $0
    ${NSD_OnClick} $0 RetryClaudeCheck
    
    ${NSD_CreateButton} 120u 100u 50u 15u "Cancel"
    Pop $0
    ${NSD_OnClick} $0 CancelInstallation
    
    nsDialogs::Show
FunctionEnd

Function RetryClaudeCheck
    Call CheckClaudeProcess
    ${If} $IsClaudeRunning == "0"
        ; Claude is no longer running, continue to next page
        nsDialogs::OnBack
    ${Else}
        ; Claude is still running
        MessageBox MB_ICONEXCLAMATION "Claude is still running. Please close it before continuing."
    ${EndIf}
FunctionEnd

Function CancelInstallation
    Abort
FunctionEnd

Function ClaudeCheckLeave
    ; Double-check before leaving this page
    Call CheckClaudeProcess
    ${If} $IsClaudeRunning == "1"
        ; Claude is still running, prevent moving to next page
        MessageBox MB_ICONEXCLAMATION "Claude is still running. Please close it before continuing."
        Abort
    ${EndIf}
FunctionEnd

; Uninstaller Claude check function
Function un.CheckClaudeProcess
    nsExec::ExecToLog 'PowerShell -Command "if(Get-Process claude -ErrorAction SilentlyContinue){exit 1}else{exit 0}"'
    Pop $IsClaudeRunning
    
    ; In silent mode, try to close Claude automatically
    ${If} ${Silent}
        ${If} $IsClaudeRunning == "1"
            DetailPrint "Claude is running. Closing automatically for silent uninstall..."
            nsExec::ExecToLog 'PowerShell -Command "Stop-Process -Name claude -Force -ErrorAction SilentlyContinue"'
            Sleep 2000
            
            ; Check again  
            nsExec::ExecToLog 'PowerShell -Command "if(Get-Process claude -ErrorAction SilentlyContinue){exit 1}else{exit 0}"'
            Pop $IsClaudeRunning
        ${EndIf}
    ${EndIf}
FunctionEnd

; Macro for the installation logic
!macro MCP_INSTALL_SECTION
Section "Install"
    ; Check if process is running
    nsExec::ExecToLog 'PowerShell -Command "if(Get-Process ${PROCESS_NAME} -ErrorAction SilentlyContinue){exit 1}else{exit 0}"'
    Pop $0
    ${If} $0 == "1"
        ${IfNot} ${Silent}
            MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "${PRODUCT_NAME} is currently running. Please close it and click OK to continue." IDOK retry IDCANCEL abort
            abort:
                Abort
            retry:
                Goto -2
        ${Else}
            ; In silent mode, try to close the process
            DetailPrint "${PRODUCT_NAME} is running. Attempting to close..."
            nsExec::ExecToLog 'PowerShell -Command "Stop-Process -Name ${PROCESS_NAME} -Force -ErrorAction SilentlyContinue"'
            Sleep 2000
        ${EndIf}
    ${EndIf}
    
    SetOutPath "$INSTDIR"
    
    ; Create the installation directory
    CreateDirectory "$INSTDIR"    
    ; Copy main executable and required files
    File /r "dist\*.*"
    ; Copy .env file
    File .\.env

    ; Copy installer directory with PowerShell scripts
    File /r "${INSTALLER_DIR}\*.*"
    
    ; Run PowerShell scripts for configuration
    DetailPrint "Running configuration check..."
    nsExec::ExecToLog 'PowerShell -ExecutionPolicy Bypass -File "$INSTDIR\check-claude-config.ps1"'
    Pop $0
    ${If} $0 == "0"
        DetailPrint "Configuration check completed successfully"
    ${Else}
        DetailPrint "Configuration check returned code: $0"
        ${IfNot} ${Silent}
            DetailPrint "ERROR: PowerShell configuration script failed. Installation cannot continue."
        ${EndIf}
        Abort
    ${EndIf}
    
    DetailPrint "Adding MCP Server..."
    
    ; Check if we need the -withLangfuse parameter (optional define)
    !ifdef WITH_LANGFUSE
        nsExec::ExecToLog 'PowerShell -ExecutionPolicy Bypass -File "$INSTDIR\add-mcp-server.ps1" -mcpName "$mcpName" -mcpCommand "$INSTDIR\server\server.exe" -envFilePath "$INSTDIR\.env" -withLangfuse'
    !else
        nsExec::ExecToLog 'PowerShell -ExecutionPolicy Bypass -File "$INSTDIR\add-mcp-server.ps1" -mcpName "$mcpName" -mcpCommand "$INSTDIR\server\server.exe" -envFilePath "$INSTDIR\.env"'
    !endif
    
    Pop $0
    ${If} $0 == "0"
        DetailPrint "MCP Server added successfully"
    ${Else}
        DetailPrint "MCP Server addition returned code: $0"
        ${IfNot} ${Silent}
            DetailPrint "ERROR: PowerShell configuration script failed. Installation cannot continue."
        ${EndIf}
        Abort
    ${EndIf}
    
    ; Write the uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Save mcpName to a file for use by the uninstaller
    FileOpen $0 "$INSTDIR\mcpconfig.txt" w
    FileWrite $0 "$mcpName"
    FileClose $0
SectionEnd
!macroend

; Macro for the uninstallation logic
!macro MCP_UNINSTALL_SECTION
Section "Uninstall"
    ; Check if Claude is running
    Call un.CheckClaudeProcess
    ${If} $IsClaudeRunning == "1"
        ${IfNot} ${Silent}
            MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "Claude is currently running. Please close it and click OK to continue." IDOK un_retry IDCANCEL un_abort
            un_abort:
                Abort
            un_retry:
                Call un.CheckClaudeProcess
                ${If} $IsClaudeRunning == "1"
                    Goto -3
                ${EndIf}
        ${EndIf}
    ${EndIf}

    ; Read mcpName from file
    FileOpen $0 "$INSTDIR\mcpconfig.txt" r
    FileRead $0 $mcpName
    FileClose $0
    
    ; Remove Claude MCP server entry
    nsExec::ExecToLog 'PowerShell -ExecutionPolicy Bypass -File "$INSTDIR\remove-mcp-server.ps1" -mcpName "$mcpName"'
    
    ; Remove files
    RMDir /r "$INSTDIR"
SectionEnd
!macroend

; Macro to set up pages, language, and init functions
!macro MCP_SETUP_INSTALLER
; Pages
!insertmacro MUI_PAGE_WELCOME
Page custom ClaudeCheckPage ClaudeCheckLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

Function .onInit
    ; Initialize variables
    StrCpy $IsClaudeRunning "0"
    
    ; Set default mcpName
    StrCpy $mcpName "${DEFAULT_MCP_NAME}"
    
    ; Runtime detection of install location based on user privileges
    !ifdef USE_RUNTIME_DETECTION
        UserInfo::GetAccountType
        Pop $0
        
        ${If} $0 == "Admin"
            ; Administrator - install to Program Files
            StrCpy $INSTDIR "$PROGRAMFILES64\${PRODUCT_SHORT_NAME}"
            SetShellVarContext all  ; Install for all users
            DetailPrint "Installing for all users (Admin privileges detected)"
        ${ElseIf} $0 == "Power"
            ; Power user - can usually install to Program Files
            StrCpy $INSTDIR "$PROGRAMFILES64\${PRODUCT_SHORT_NAME}"
            SetShellVarContext all
            DetailPrint "Installing for all users (Power User privileges detected)"
        ${Else}
            ; Regular user or guest - install to user's local directory
            StrCpy $INSTDIR "$LOCALAPPDATA\${PRODUCT_SHORT_NAME}"
            SetShellVarContext current  ; Install for current user only
            DetailPrint "Installing for current user only (Standard User privileges detected)"
        ${EndIf}
    !else
        ; Static INSTALL_LOCATION was provided, use it
        DetailPrint "Using predefined installation location: $INSTDIR"
    !endif
FunctionEnd

Function un.onInit
    ; Initialize variables for uninstaller
    StrCpy $IsClaudeRunning "0"
FunctionEnd

; Insert the installation and uninstallation sections
!insertmacro MCP_INSTALL_SECTION
!insertmacro MCP_UNINSTALL_SECTION
!macroend

!endif ; COMMON_MCP_INSTALLER_NSH
