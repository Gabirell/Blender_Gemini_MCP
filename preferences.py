# preferences.py

import bpy
from . import Blender_Gemini_MCP_utils as utils

_model_list_cache = [("gemini-1.5-flash-latest", "Gemini 1.5 Flash", "Default model")]

def get_models_for_enum(self, context):
    global _model_list_cache
    return _model_list_cache

def refresh_models_background(api_key):
    print("Refreshing Gemini models...")
    global _model_list_cache
    models = utils.get_available_models(api_key)
    if models:
        _model_list_cache = models
        print(f"Models found: {[m[0] for m in models]}")
    else:
        _model_list_cache = [("gemini-1.5-flash-latest", "No models found (check API Key)", "")]
        print("No models found or API key is invalid.")
    
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'PREFERENCES':
                area.tag_redraw()

def update_model_list_on_apikey_change(self, context):
    prefs = context.preferences.addons[__package__].preferences
    if prefs.api_key:
        bpy.app.timers.register(lambda: refresh_models_background(prefs.api_key))
    return None

class GeminiAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    api_key: bpy.props.StringProperty(
        name="Gemini API Key",
        description="Paste your Google Gemini API key here",
        subtype='PASSWORD',
        update=update_model_list_on_apikey_change,
    )

    model_list: bpy.props.EnumProperty(
        name="Model",
        description="Select the Gemini model to use",
        items=get_models_for_enum,
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "api_key")
        
        row = layout.row()
        row.prop(self, "model_list")
        row.operator("gemini.refresh_models", text="", icon='FILE_REFRESH')

class GEMINI_OT_refresh_models(bpy.types.Operator):
    bl_idname = "gemini.refresh_models"
    bl_label = "Refresh Model List"
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        if prefs.api_key:
            refresh_models_background(prefs.api_key)
            self.report({'INFO'}, "Model list refreshed.")
        else:
            self.report({'WARNING'}, "Please enter an API key first.")
        return {'FINISHED'}
