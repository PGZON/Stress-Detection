;NSIS Installer Script for StressSense+
;This script creates a professional Windows installer

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

;General Configuration
Name "StressSense+"
OutFile "StressSense+_Installer.exe"
Unicode True
InstallDir "$PROGRAMFILES64\StressSense+"
InstallDirRegKey HKCU "Software\StressSense+" ""
RequestExecutionLevel admin

;Modern UI Configuration
!define MUI_ABORTWARNING
;!define MUI_ICON "icon.ico"  ; Removed - icon file format issue
;!define MUI_UNICON "icon.ico"  ; Removed - icon file format issue

;Header
!define MUI_HEADERIMAGE
;!define MUI_HEADERIMAGE_BITMAP "icon.ico"  ; Removed - icon file format issue
;!define MUI_HEADERIMAGE_UNBITMAP "icon.ico"  ; Removed - icon file format issue

;Welcome/Finish Page
!define MUI_WELCOMEPAGE_TITLE "Welcome to the StressSense+ Setup Wizard"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of StressSense+, an employee stress detection system that monitors stress levels through webcam analysis.$\r$\n$\r$\nIt is recommended that you close all other applications before continuing.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_TITLE "Completing the StressSense+ Setup Wizard"
!define MUI_FINISHPAGE_TEXT "StressSense+ has been successfully installed on your computer.$\r$\n$\r$\nThe stress detection service has been installed and started automatically. Your system is now monitoring employee stress levels.$\r$\n$\r$\nClick Finish to exit the wizard."
!define MUI_FINISHPAGE_RUN "$INSTDIR\StressSense+.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch StressSense+ now"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View README"

;Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;Languages
!insertmacro MUI_LANGUAGE "English"

;Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "StressSense+"
VIAddVersionKey "CompanyName" "Your Company"
VIAddVersionKey "LegalCopyright" "© 2025 Your Company"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "FileDescription" "StressSense+ Employee Stress Detection System"

;Installer Sections
Section "StressSense+" SecApp
    SectionIn RO

    SetOutPath "$INSTDIR"

    ;Copy all files from dist directory
    DetailPrint "Installing StressSense+ files..."
    File /r "dist\*.*"

    ;Copy additional files
    File "license.txt"
    File ".env"

    ;Install and start the Windows service
    DetailPrint "Installing Windows service..."
    nsExec::ExecToLog '"$INSTDIR\install_service.exe" install'
    Pop $0
    ${If} $0 != 0
        DetailPrint "Warning: Service installation may have failed (exit code: $0)"
        MessageBox MB_OK "Warning: The stress detection service could not be installed automatically. You may need to install it manually after setup completes."
    ${Else}
        DetailPrint "Service installed successfully"
    ${EndIf}

    ;Create desktop shortcut
    DetailPrint "Creating desktop shortcut..."
    CreateShortCut "$DESKTOP\StressSense+.lnk" "$INSTDIR\StressSense+.exe" "" "$INSTDIR\StressSense+.exe" 0

    ;Create start menu entries
    DetailPrint "Creating start menu entries..."
    CreateDirectory "$SMPROGRAMS\StressSense+"
    CreateShortCut "$SMPROGRAMS\StressSense+\StressSense+.lnk" "$INSTDIR\StressSense+.exe"
    CreateShortCut "$SMPROGRAMS\StressSense+\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ;Store installation folder
    WriteRegStr HKCU "Software\StressSense+" "" $INSTDIR

    ;Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "DisplayName" "StressSense+"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "DisplayVersion" "1.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "Publisher" "Your Company"
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "NoModify" 1
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "NoRepair" 1
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+" "EstimatedSize" "$0"

SectionEnd

;Uninstaller Section
Section "Uninstall"

    ;Stop and uninstall service if running
    DetailPrint "Stopping and uninstalling service..."
    nsExec::ExecToLog '"$INSTDIR\install_service.exe" uninstall'
    Pop $0
    ${If} $0 != 0
        DetailPrint "Warning: Service uninstallation may have failed (exit code: $0)"
    ${EndIf}

    ;Remove files
    DetailPrint "Removing files..."
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"

    ;Remove shortcuts
    DetailPrint "Removing shortcuts..."
    Delete "$DESKTOP\StressSense+.lnk"
    RMDir /r "$SMPROGRAMS\StressSense+"

    ;Remove registry entries
    DetailPrint "Removing registry entries..."
    DeleteRegKey HKCU "Software\StressSense+"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense+"

SectionEnd

;Installer Functions
Function .onInit
    ;Check if already installed
    ReadRegStr $R0 HKCU "Software\StressSense+" ""
    ${If} $R0 != ""
        MessageBox MB_YESNO "StressSense+ is already installed. Do you want to reinstall?" IDYES continue
        Abort
        continue:
    ${EndIf}

    ;Check Windows version (Windows 10+ required)
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK "StressSense+ requires Windows 10 or later.$\r$\n$\r$\nYour system does not meet the minimum requirements."
        Abort
    ${EndIf}

    ;Check for administrator privileges
    userInfo::getAccountType
    pop $0
    ${If} $0 != "admin"
        MessageBox MB_OK "Administrator privileges are required to install StressSense+.$\r$\n$\r$\nPlease run the installer as an administrator."
        Abort
    ${EndIf}

    ;Check if dist directory exists
    IfFileExists "dist\*.*" dist_ok
        MessageBox MB_OK "Installation files not found. Please run build_exe.bat first."
        Abort
    dist_ok:
FunctionEnd

;Uninstaller Functions
Function un.onInit
    ;Check for administrator privileges
    userInfo::getAccountType
    pop $0
    ${If} $0 != "admin"
        MessageBox MB_OK "Administrator privileges are required to uninstall StressSense+.$\r$\n$\r$\nPlease run the uninstaller as an administrator."
        Abort
    ${EndIf}

    MessageBox MB_YESNO "Are you sure you want to completely remove StressSense+ and all of its components?$\r$\n$\r$\nThis will stop the background service and remove all files." IDYES continue
    Abort
    continue:
FunctionEnd