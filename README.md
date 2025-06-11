Blender Gemini Assistant:

This Blender addon integrates Google's Gemini Pro model to provide assistance through text and voice commands directly within the Blender interface.

Features
Text-based prompts: Type in your questions or commands and get a response from Gemini.

Voice recognition: Use your microphone to speak your commands to Gemini.

Seamless integration: The addon is accessible through a panel in the 3D Viewport's sidebar.

Installation:

Download the addon: Download the Gemini_Assistant.py file from this repository.

Install the addon in Blender:

Open Blender and go to Edit > Preferences > Add-ons.

Click on Install... and select the downloaded Gemini_Assistant.py file.

Enable the addon by checking the box next to "3D View: Gemini Assistant".

Configuration
1. Get a Gemini API Key
Go to Google AI Studio and create an API key.

2. Add the API Key to the Addon
In Blender, open the 3D Viewport and press N to open the sidebar.

Go to the "Gemini Assistant" tab.

Paste your Gemini API key into the "API Key" field.

3. Install Required Python Libraries
This addon requires the following Python libraries:

google-generativeai

SpeechRecognition

PyAudio

You need to install these libraries in Blender's Python environment.

Windows:

Open the Command Prompt.

Navigate to Blender's Python binary directory. It's usually located at:
C:\Program Files\Blender Foundation\Blender <version>\<version>\python\bin

Run the following commands:

python.exe -m pip install google-generativeai
python.exe -m pip install SpeechRecognition
python.exe -m pip install pyaudio

macOS:

Open the Terminal.

Navigate to Blender's Python binary directory:
/Applications/Blender.app/Contents/Resources/<version>/python/bin

Run the following commands:

./python3.10 -m pip install google-generativeai
./python3.10 -m pip install SpeechRecognition
./python3.10 -m pip install pyaudio

Linux:

Open the Terminal.

Navigate to Blender's Python binary directory:
/<blender_directory>/<version>/python/bin

Run the following commands:

./python3.10 -m pip install google-generativeai
./python3.10 -m pip install SpeechRecognition
./python3.10 -m pip install pyaudio

Usage
Text Input:

Type your prompt in the text field under the API key.

Click on "Send Prompt".

The response from Gemini will appear in the "Response" box.

Voice Input:

Click on "Start Listening".

The addon will start listening for your voice command.

Speak your prompt clearly.

The addon will automatically send the recognized text to Gemini and display the response.

How to upload to GitHub
Create a GitHub account: If you don't have one, sign up at https://github.com/.

Create a new repository:

Click on the "+" icon in the top right corner and select "New repository".

Give your repository a name (e.g., blender-gemini-assistant).

Add a description (optional).

Choose to make it public or private.

Click on "Create repository".

Upload the files:

On the repository page, click on "Add file" and select "Upload files".

Drag and drop the Gemini_Assistant.py and README.md files into the upload area.

Add a commit message (e.g., "Initial commit").

Click on "Commit changes".

Now you have a GitHub repository for your Blender addon that you can share with others!
