;NSIS Installer Script for StressSense
;This script creates a professional Windows installer

!include "MUI2.nsh"
!include "FileFunc.nsh"

;General Configuration
Name "StressSense"
OutFile "StressSense_Installer.exe"
Unicode True
InstallDir "$PROGRAMFILES\StressSense"
InstallDirRegKey HKCU "Software\StressSense" ""
RequestExecutionLevel admin

;Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico" ; Add an icon file if available
!define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp" ; Add header image if available
!define MUI_WELCOMEFINISHPAGE_BITMAP "wizard.bmp" ; Add wizard image if available

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
VIAddVersionKey "ProductName" "StressSense"
VIAddVersionKey "CompanyName" "Your Company"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "FileDescription" "Employee Stress Detection System"

;Installer Sections
Section "StressSense" SecApp
    SectionIn RO

    SetOutPath "$INSTDIR"

    ;Copy all files from dist directory
    DetailPrint "Installing StressSense..."
    File /r "dist\*.*"

    ;Create desktop shortcut
    CreateShortCut "$DESKTOP\StressSense.lnk" "$INSTDIR\StressSense.exe" "" "$INSTDIR\StressSense.exe" 0

    ;Create start menu entries
    CreateDirectory "$SMPROGRAMS\StressSense"
    CreateShortCut "$SMPROGRAMS\StressSense\StressSense.lnk" "$INSTDIR\StressSense.exe"
    CreateShortCut "$SMPROGRAMS\StressSense\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ;Store installation folder
    WriteRegStr HKCU "Software\StressSense" "" $INSTDIR

    ;Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "DisplayName" "StressSense"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "DisplayVersion" "1.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "Publisher" "Your Company"
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "NoModify" 1
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense" "NoRepair" 1

SectionEnd

;Uninstaller Section
Section "Uninstall"

    ;Stop and uninstall service if running
    ExecWait '"$INSTDIR\StressSense.exe" /uninstall_service'

    ;Remove files
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"

    ;Remove shortcuts
    Delete "$DESKTOP\StressSense.lnk"
    RMDir /r "$SMPROGRAMS\StressSense"

    ;Remove registry entries
    DeleteRegKey HKCU "Software\StressSense"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressSense"

SectionEnd

;Installer Functions
Function .onInit
    ;Check if already installed
    ReadRegStr $R0 HKCU "Software\StressSense" ""
    ${If} $R0 != ""
        MessageBox MB_YESNO "StressSense is already installed. Do you want to reinstall?" IDYES continue
        Abort
        continue:
    ${EndIf}

    ;Check Windows version (Windows 10+ required)
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK "StressSense requires Windows 10 or later."
        Abort
    ${EndIf}
FunctionEnd

;Uninstaller Functions
Function un.onInit
    MessageBox MB_YESNO "Are you sure you want to completely remove StressSense and all of its components?" IDYES continue
    Abort
    continue:
FunctionEnd