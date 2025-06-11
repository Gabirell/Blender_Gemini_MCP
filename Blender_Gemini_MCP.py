# Blender_Gemini_MCP.py

import bpy
import threading
import textwrap
from . import Blender_Gemini_MCP_utils as utils

class GeminiProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(name="Prompt", default="")
    response: bpy.props.StringProperty(name="Response", default="Awaiting prompt...")
    popup_prompt: bpy.props.StringProperty(name="Popup Prompt", default="")

class GEMINI_OT_send_prompt(bpy.types.Operator):
    bl_label = "Send Prompt"
    bl_idname = "gemini.send_prompt"
    
    from_popup: bpy.props.BoolProperty(default=False)
    _timer = None
    _thread = None
    _thread_result = {}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.gemini_properties

        if not prefs.api_key:
            self.report({'ERROR'}, "Please set your Gemini API Key in the addon preferences.")
            return {'CANCELLED'}
            
        prompt_text = props.popup_prompt if self.from_popup else props.prompt
        if not prompt_text:
            self.report({'INFO'}, "Prompt is empty.")
            return {'CANCELLED'}
        
        props.response = "Generating response..."
        self._thread_result.clear()

        def threaded_function(api_key, model, prompt, result_container):
            print("Gemini Thread: Starting request...")
            try:
                response_text = utils.send_prompt_to_gemini(api_key, model, prompt)
                result_container['result'] = response_text
                print("Gemini Thread: Request successful.")
            except Exception as e:
                error_msg = f"An unexpected error occurred in the thread: {e}"
                result_container['error'] = error_msg
                print(f"Gemini Thread: {error_msg}")

        self._thread = threading.Thread(target=threaded_function, args=(prefs.api_key, prefs.model_list, prompt_text, self._thread_result))
        self._thread.start()

        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        if self.from_popup:
            props.popup_prompt = ""

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self._thread.is_alive():
                props = context.scene.gemini_properties
                if 'error' in self._thread_result:
                    props.response = self._thread_result['error']
                elif 'result' in self._thread_result:
                    props.response = self._thread_result['result']
                else:
                    props.response = "Task finished, but no result was returned. Check the console."
                
                context.window_manager.event_timer_remove(self._timer)
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}

class GEMINI_OT_execute_code(bpy.types.Operator):
    bl_label = "Execute Code"
    bl_idname = "gemini.execute_code"

    def execute(self, context):
        props = context.scene.gemini_properties
        code_to_run = utils.extract_python_code(props.response)

        if code_to_run:
            try:
                exec(code_to_run, {'bpy': bpy})
                self.report({'INFO'}, "Code executed successfully.")
            except Exception as e:
                error_message = f"Error executing Python code: {e}"
                self.report({'ERROR'}, error_message)
                props.response += f"\n\n--- EXECUTION ERROR ---\n{error_message}"
        else:
            self.report({'WARNING'}, "No Python code block found in the response.")
        
        return {'FINISHED'}

class GEMINI_OT_popup_window(bpy.types.Operator):
    bl_label = "Gemini Prompt"
    bl_idname = "gemini.popup_window"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_properties
        layout.prop(props, "popup_prompt", text="")

    def execute(self, context):
        bpy.ops.gemini.send_prompt('EXEC_DEFAULT', from_popup=True)
        return {'FINISHED'}

class GEMINI_PT_panel(bpy.types.Panel):
    bl_label = "Gemini MCP Assistant"
    bl_idname = "GEMINI_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini MCP'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_properties
        prefs = context.preferences.addons[__package__].preferences
        
        if not prefs.api_key:
            layout.label(text="Please set API Key in Preferences.", icon='ERROR')
            return

        layout.label(text="Enter Prompt:")
        layout.prop(props, "prompt", text="")
        layout.operator("gemini.send_prompt")
        
        layout.separator()
        layout.label(text="Gemini Response:")
        
        box = layout.box()
        col = box.column()

        if props.response:
            wrap_width = max(10, int(context.region.width / 7))
            lines = props.response.split('\n')
            for line in lines:
                wrapped_lines = textwrap.wrap(line, width=wrap_width, replace_whitespace=False)
                if not wrapped_lines:
                    col.label(text="")
                else:
                    for wrapped_line in wrapped_lines:
                        col.label(text=wrapped_line)
        
        if "```python" in props.response:
            layout.operator("gemini.execute_code", icon='PLAY')
