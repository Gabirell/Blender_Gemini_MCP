bl_info = {
    "name": "Gemini Assistant",
    "author": "Gabriel Netto",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Gemini Assistant",
    "description": "Integrates Google Gemini for text and voice commands",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
import speech_recognition as sr
import google.generativeai as genai
import threading
import queue

# --- Properties ---

class GeminiProperties(bpy.types.PropertyGroup):
    api_key: bpy.props.StringProperty(
        name="API Key",
        description="Your Google Gemini API Key",
        subtype="PASSWORD",
    )
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Enter your prompt here",
    )
    response: bpy.props.StringProperty(
        name="Response",
        description="Response from Gemini",
    )
    is_listening: bpy.props.BoolProperty(
        name="Is Listening",
        description="Is the plugin listening for voice input",
        default=False,
    )

# --- Operators ---

class GEMINI_OT_send_prompt(bpy.types.Operator):
    """Sends the prompt to Gemini"""
    bl_label = "Send Prompt"
    bl_idname = "gemini.send_prompt"

    def execute(self, context):
        props = context.scene.gemini_properties
        if not props.api_key:
            self.report({'ERROR'}, "Please enter your Gemini API Key")
            return {'CANCELLED'}

        genai.configure(api_key=props.api_key)
        model = genai.GenerativeModel('gemini-pro')

        try:
            response = model.generate_content(props.prompt)
            props.response = response.text
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class GEMINI_OT_listen_voice(bpy.types.Operator):
    """Listens for voice input"""
    bl_label = "Start Listening"
    bl_idname = "gemini.listen_voice"

    def modal(self, context, event):
        props = context.scene.gemini_properties
        if not props.is_listening:
            return {'FINISHED'}

        if not self.q.empty():
            try:
                result = self.q.get_nowait()
                if isinstance(result, str):
                    props.prompt = result
                    GEMINI_OT_send_prompt.execute(self, context)
                elif isinstance(result, Exception):
                    self.report({'ERROR'}, f"Error: {result}")
            except queue.Empty:
                pass
            props.is_listening = False
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.gemini_properties
        if props.is_listening:
            props.is_listening = False
            return {'FINISHED'}

        self.q = queue.Queue()
        self.r = sr.Recognizer()

        def voice_callback(recognizer, audio):
            try:
                self.q.put(recognizer.recognize_google(audio))
            except sr.UnknownValueError:
                self.q.put(Exception("Google Speech Recognition could not understand audio"))
            except sr.RequestError as e:
                self.q.put(Exception(f"Could not request results from Google Speech Recognition service; {e}"))

        def listen_in_background():
            with sr.Microphone() as source:
                self.r.adjust_for_ambient_noise(source)
                audio = self.r.listen(source)
                voice_callback(self.r, audio)

        props.is_listening = True
        self.report({'INFO'}, "Listening for voice input...")

        self.thread = threading.Thread(target=listen_in_background)
        self.thread.daemon = True
        self.thread.start()

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# --- UI Panel ---

class GEMINI_PT_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport"""
    bl_label = "Gemini Assistant"
    bl_idname = "GEMINI_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini Assistant'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_properties

        layout.prop(props, "api_key")
        layout.separator()
        layout.prop(props, "prompt", text="")
        layout.operator("gemini.send_prompt")
        layout.separator()
        layout.operator("gemini.listen_voice", text="Start Listening" if not props.is_listening else "Stop Listening")
        if props.is_listening:
            layout.label(text="Listening...")
        layout.separator()
        layout.label(text="Response:")
        layout.box().label(text=props.response)

# --- Registration ---

classes = (
    GeminiProperties,
    GEMINI_OT_send_prompt,
    GEMINI_OT_listen_voice,
    GEMINI_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gemini_properties = bpy.props.PointerProperty(type=GeminiProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gemini_properties

if __name__ == "__main__":
    register()
