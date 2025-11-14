!define PRODUCT_NAME "Executive Reports MCP Server"
!define PRODUCT_SHORT_NAME "Exec-Reports-MCP-Server"
!define DEFAULT_MCP_NAME "exec-reports-mcp"
!define PRODUCT_START_MENU_DIR "Executive Reports MCP Server"
!define PROCESS_NAME "server"
#!define INSTALL_LOCATION $PROGRAMFILES64  ; or "${LOCALAPPDATA}"
!define INSTALLER_DIR "..\installer"

!ifndef VERSION
  !define VERSION "1.0.0"
!endif

!include "${INSTALLER_DIR}\common-mcp-install.nsh"
!insertmacro MCP_SETUP_INSTALLER
