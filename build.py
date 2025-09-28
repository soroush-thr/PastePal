"""
Build script for PastePal
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        # Use list format for subprocess to handle paths with spaces
        if isinstance(command, str):
            # Split the command into parts for better handling
            import shlex
            command_parts = shlex.split(command)
        else:
            command_parts = command
            
        # Print the actual command being run
        print(f"Executing: {' '.join(command_parts)}")
        
        result = subprocess.run(command_parts, check=True, capture_output=True, text=True, cwd=os.getcwd())
        print("SUCCESS!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error:", e.stderr)
        return False
    except FileNotFoundError as e:
        print(f"ERROR: Command not found: {e}")
        return False


def clean_build_directories():
    """Clean previous build directories"""
    print("Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    # Install from requirements.txt
    if os.path.exists('requirements.txt'):
        success = run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing Python dependencies"
        )
        if not success:
            return False
    
    # Install PyInstaller if not already installed
    success = run_command(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        "Installing PyInstaller"
    )
    return success


def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Use the spec file
    success = run_command(
        [sys.executable, "-m", "PyInstaller", "pastepal.spec"],
        "Building executable with PyInstaller"
    )
    return success


def create_installer():
    """Create Windows installer using Inno Setup"""
    print("Creating Windows installer...")
    
    # Check if Inno Setup is available
    inno_setup_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    inno_setup_exe = None
    for path in inno_setup_paths:
        if os.path.exists(path):
            inno_setup_exe = path
            break
    
    if not inno_setup_exe:
        print("Inno Setup not found. Skipping installer creation.")
        print("You can create an installer manually using the files in dist/")
        return True
    
    # Create installer script
    installer_script = create_installer_script()
    
    # Write installer script
    with open('installer.iss', 'w') as f:
        f.write(installer_script)
    
    # Run Inno Setup
    success = run_command(
        f'"{inno_setup_exe}" installer.iss',
        "Creating Windows installer with Inno Setup"
    )
    
    # Clean up installer script
    if os.path.exists('installer.iss'):
        os.remove('installer.iss')
    
    return success


def create_installer_script():
    """Create Inno Setup installer script"""
    return f"""
[Setup]
AppName=PastePal
AppVersion=1.0.0
AppPublisher=PastePal Team
AppPublisherURL=https://github.com/pastepal/pastepal
AppSupportURL=https://github.com/pastepal/pastepal/issues
AppUpdatesURL=https://github.com/pastepal/pastepal/releases
DefaultDirName={{autopf}}\\PastePal
DefaultGroupName=PastePal
AllowNoIcons=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=PastePal-Setup-1.0.0
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\\PastePal\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\PastePal"; Filename: "{{app}}\\PastePal.exe"
Name: "{{group}}\\{{cm:UninstallProgram,PastePal}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\PastePal"; Filename: "{{app}}\\PastePal.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\PastePal"; Filename: "{{app}}\\PastePal.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\PastePal.exe"; Description: "{{cm:LaunchProgram,PastePal}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{app}}\\pastepal.db"
Type: filesandordirs; Name: "{{app}}\\logs"
"""


def create_portable_package():
    """Create portable package"""
    print("Creating portable package...")
    
    portable_dir = "dist/PastePal-Portable"
    
    # Create portable directory
    os.makedirs(portable_dir, exist_ok=True)
    
    # Copy executable and dependencies
    if os.path.exists("dist/PastePal"):
        shutil.copytree("dist/PastePal", portable_dir, dirs_exist_ok=True)
    
    # Create portable launcher script
    launcher_script = """@echo off
echo Starting PastePal...
start "" "PastePal.exe"
"""
    
    with open(os.path.join(portable_dir, "StartPastePal.bat"), 'w') as f:
        f.write(launcher_script)
    
    # Create README for portable version
    readme_content = """# PastePal Portable

This is the portable version of PastePal. No installation required!

## How to use:
1. Double-click "StartPastePal.bat" to start the application
2. Or double-click "PastePal.exe" directly

## Features:
- Advanced clipboard management
- Global hotkeys (Alt+V to show window)
- Text transformation tools
- Pin important items
- Dark/Light themes
- And much more!

## Data Storage:
Your clipboard history is stored in "pastepal.db" in this folder.
You can safely move this entire folder to any location.

## Support:
Visit https://github.com/pastepal/pastepal for more information.
"""
    
    with open(os.path.join(portable_dir, "README.txt"), 'w') as f:
        f.write(readme_content)
    
    print(f"Portable package created in: {portable_dir}")


def main():
    """Main build function"""
    print("PastePal Build Script")
    print("====================")
    
    # Check if we're in the right directory
    if not os.path.exists('pastepal'):
        print("ERROR: Please run this script from the PastePal root directory")
        return 1
    
    # Clean previous builds
    clean_build_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("ERROR: Failed to install dependencies")
        return 1
    
    # Build executable
    if not build_executable():
        print("ERROR: Failed to build executable")
        return 1
    
    # Create portable package
    create_portable_package()
    
    # Create installer (optional)
    if input("\nCreate Windows installer? (y/n): ").lower().startswith('y'):
        create_installer()
    
    print("\n" + "="*50)
    print("BUILD COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\nOutput files:")
    print("- Executable: dist/PastePal/PastePal.exe")
    print("- Portable: dist/PastePal-Portable/")
    if os.path.exists("dist/PastePal-Setup-1.0.0.exe"):
        print("- Installer: dist/PastePal-Setup-1.0.0.exe")
    
    print("\nYou can now distribute these files!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
