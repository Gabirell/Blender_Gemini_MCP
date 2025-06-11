# __init__.py

bl_info = {
    "name": "Gemini MCP Assistant",
    "author": "Gabriel Netto & Gemini",
    "version": (1, 4, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Gemini MCP, or press Alt+G",
    "description": "Control Blender with Gemini, execute code, and select models.",
    "warning": "",
    "doc_url": "https://github.com/Gabirell/Blender_Gemini_MCP",
    "category": "3D View",
}

import bpy
from bpy.props import PointerProperty
from . import Blender_Gemini_MCP
from . import Blender_Gemini_MCP_utils
from . import preferences

import importlib
importlib.reload(Blender_Gemini_MCP)
importlib.reload(Blender_Gemini_MCP_utils)
importlib.reload(preferences)

addon_keymaps = []

classes = (
    Blender_Gemini_MCP.GeminiProperties,
    Blender_Gemini_MCP.GEMINI_OT_send_prompt,
    Blender_Gemini_MCP.GEMINI_OT_execute_code,
    Blender_Gemini_MCP.GEMINI_OT_popup_window,
    Blender_Gemini_MCP.GEMINI_PT_panel,
    preferences.GeminiAddonPreferences,
    preferences.GEMINI_OT_refresh_models,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.gemini_properties = PointerProperty(type=Blender_Gemini_MCP.GeminiProperties)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(Blender_Gemini_MCP.GEMINI_OT_popup_window.bl_idname, 'G', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.gemini_properties