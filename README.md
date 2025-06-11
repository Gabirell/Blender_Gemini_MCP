Blender Gemini MCP Assistant

This Blender addon integrates Google's Gemini Pro model to provide assistance through text and voice commands directly within the Blender interface. It is structured as a multi-file addon for easy installation and maintenance.

Features:

    Text-based prompts: Type in your questions or commands and get a response from Gemini.

    Voice recognition: Use your microphone to speak your commands to Gemini.

    Seamless integration: The addon is accessible through a panel in the 3D Viewport's sidebar.

Installation
    1. Download the Addon ZIP
    Download the Blender_Gemini_MCP_Plugin.zip file from the Releases page of this repository.

    2. Install the Addon in Blender
    Open Blender and go to Edit > Preferences > Add-ons.

    Click on Install....

    Navigate to and select the downloaded Blender_Gemini_MCP_Plugin.zip file. Do not unzip it.

    Enable the addon by checking the box next to "3D View: Gemini MCP Assistant".

Configuration
    1. Get a Gemini API Key
    Go to Google AI Studio and create an API key.

    2. Add the API Key to the Addon
    In Blender, open the 3D Viewport and press N to open the sidebar.

    Go to the "Gemini MCP" tab.

    Paste your Gemini API key into the "API Key" field.

    3. Install Required Python Libraries
    This addon requires third-party Python libraries to function. You must install them into Blender's internal Python environment.

How to Install Libraries:

Find the path to Blender's Python executable. (Remember to change the version number to your own and to find the correct path if you installed it elsewhere)

Windows: C:\Program Files\Blender Foundation\Blender <version>\<version>\python\bin

macOS: /Applications/Blender.app/Contents/Resources/<version>/python/bin

Linux: /<blender_directory>/<version>/python/bin

Open your system's command line (Command Prompt on Windows, Terminal on macOS/Linux).

Navigate to the directory from step 1.

Run the following commands:

# For Windows
python.exe -m pip install --upgrade pip
python.exe -m pip install google-generativeai
python.exe -m pip install SpeechRecognition
python.exe -m pip install PyAudio

# For macOS/Linux
./python3.10 -m pip install --upgrade pip
./python3.10 -m pip install google-generativeai
./python3.10 -m pip install SpeechRecognition
./python3.10 -m pip install PyAudio

Note: The exact python executable name (python.exe or ./python3.10) may vary depending on your Blender and OS version.

Usage
Text Input:

Type your prompt in the text field.

Click "Send Prompt".

The response will appear in the box below.

Voice Input:

Click "Start Listening". The status will change to "Listening...".

Speak your prompt clearly into your microphone.

The addon will automatically transcribe your speech, send it to Gemini, and display the response.

Hope you enjoy it!v