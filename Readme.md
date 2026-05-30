Python Script Runner & Packager V2.0 (UV Python Tool)
A lightweight GUI tool built with tkinter and uv to simplify running and packaging Python scripts. It automatically detects dependencies and uses uv for lightning-fast execution and compiling, freeing you from managing complex virtual environments.

1. Features
Auto Dependency Detection: Uses ast to parse import statements and automatically extracts third-party packages (filters out standard libraries for Python 3.8+).

Smart Name Mapping: Automatically maps common module names to their correct pip package names (e.g., cv2 becomes opencv-python, PIL becomes Pillow).

Seamless uv Integration: Uses uv run to dynamically fetch dependencies and run scripts in isolated environments, keeping your system clean.

One-Click EXE Packaging: Automatically injects pyinstaller and required dependencies to build a single, windowless .exe file.

Real-time Console: Built-in asynchronous log window to track execution and packaging progress without freezing the UI.

2. Prerequisites
IMPORTANT: You must have uv (a lightning-fast Python package installer written in Rust) installed and added to your system environment variables.

Install uv on Windows:
Open Terminal or PowerShell and run:

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

(For other operating systems, please refer to the uv official documentation)

3. Getting Started
Option 1: Use the Standalone EXE (Recommended)
Download UVToolApp.exe from the Releases page.

Double-click to run. No installation required.

Option 2: Run from Source
Clone or download this repository.

Since the GUI only uses Python standard libraries, you can run it directly without installing anything else:


python "python tool v2.0.py"


4. How to Use
Click "Browse..." to select your target .py script.

The tool will automatically analyze and fill in the required third-party packages. You can also manually add or edit them in the text box (separated by spaces).

Click "▶ Run" to test your script.

Once verified, click "📦 Pack to EXE" . The generated .exe file will be saved in a dist folder located in the same directory as your original script.

Notes:
Packaging Parameters: The tool defaults to pyinstaller --onefile --noconsole. If your script is a CLI tool that needs a terminal window, or if it requires extra resource files, you will need to modify these parameters in the source code.

Python Version: For maximum compatibility with older Windows systems, the tool is hardcoded to use Python 3.8.20 (--python 3.8.20). You can easily change this target version within the run_script and pack_exe functions in the source code.


