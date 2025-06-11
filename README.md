Blender Gemini MCP Assistant

This addon integrates Google's Gemini AI directly into Blender, allowing you to use natural language to generate and execute Python scripts, ask for help, and control the 3D environment.

Features:

Blender-Aware Context: Gemini is instructed to act as a Blender expert. It knows it's inside Blender and provides relevant answers and code.

Code Execution: When Gemini generates a Python script, an "Execute Code" button appears, allowing you to run the script and modify your scene directly.

Dynamic Model Selection: Choose any available Gemini model from a list that updates automatically when you enter your API key. Always use the latest and most powerful models.

Popup Window: Press Alt+G anywhere in the 3D View to open a quick prompt window, so you don't need to keep the sidebar open.

Installation:

1. Download the Addon
Go to the Releases page of this repository.

Download the latest Blender_Gemini_MCP_Plugin.zip file.

2. Install the Addon in Blender
Open Blender and go to Edit > Preferences > Add-ons.

Click Install....

Navigate to and select the Blender_Gemini_MCP_Plugin.zip file you just downloaded. Do not unzip it.

Enable the addon by checking the box next to "Gemini MCP Assistant".

3. Install Required Python Libraries
This addon will not work without its required third-party libraries. You must install them into Blender's internal Python environment.

How to Install:

Find the path to Blender's Python executable.

Windows: C:\Program Files\Blender Foundation\Blender <version>\<version>\python\bin

macOS: /Applications/Blender.app/Contents/Resources/<version>/python/bin

Linux: /<blender_install_dir>/<version>/python/bin

Open your system's command line (Command Prompt on Windows, Terminal on macOS/Linux).

Navigate to the directory from step 1 using the cd command. For example, on Windows:

cd "C:\Program Files\Blender Foundation\Blender 4.1\4.1\python\bin"

Run the following commands to install the libraries:

# For Windows
python.exe -m pip install --upgrade pip
python.exe -m pip install google-generativeai SpeechRecognition PyAudio

# For macOS / Linux
./python3.11 -m pip install --upgrade pip
./python3.11 -m pip install google-generativeai SpeechRecognition PyAudio

Note: The Python executable name (python.exe, ./python3.11, etc.) might differ slightly depending on your Blender version.

Configuration:

Get a Gemini API Key:

Go to Google AI Studio and create a free API key.

Set up the Addon in Blender:

Go to Edit > Preferences > Add-ons.

Find "Gemini MCP Assistant" in the list and expand it.

Paste your API key into the "Gemini API Key" field.

The list of available models will refresh automatically. You can select your preferred model from the dropdown menu.

How to Use:

Main Panel:
Open the 3D Viewport's sidebar by pressing N.

Go to the "Gemini MCP" tab.

Type your prompt (e.g., "Create a sphere and add a subdivision surface modifier") and click "Send Prompt".

The response will appear in the panel. If it contains code, the "Execute Code" button will appear.

Popup Window:

In the 3D Viewport, press Alt+G.

A small window will pop up. Type your prompt there and press Enter or click "OK".

The response will be processed and will appear in the main panel.

Code Execution
After Gemini provides a response containing a Python script, click the Execute Code button that appears at the bottom of the panel.

The script will run immediately, affecting your current scene.
