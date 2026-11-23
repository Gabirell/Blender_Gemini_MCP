# SPDX-License-Identifier: GPL-3.0-or-later
# Gemini MCP Assistant 2.0 — ask Google Gemini inside Blender, with YOUR OWN free API key.
# Blender 4.2+: installed as an extension (blender_manifest.toml). Older Blender (3.x–4.1): bl_info below.

bl_info = {
    "name": "Gemini MCP Assistant",
    "author": "Gabriel Netto",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar (N) > Gemini, or Alt+G",
    "description": "Ask Gemini about Blender and run the Python it writes. Uses your own free API key; models are checked automatically.",
    "doc_url": "https://github.com/Gabirell/Blender_Gemini_MCP",
    "tracker_url": "https://github.com/Gabirell/Blender_Gemini_MCP/issues",
    "category": "3D View",
}

import bpy

from . import gemini_api, preferences, operators

classes = (
    operators.GeminiProperties,
    operators.GEMINI_OT_send_prompt,
    operators.GEMINI_OT_execute_code,
    operators.GEMINI_OT_popup_window,
    operators.GEMINI_PT_panel,
    preferences.GeminiAddonPreferences,
    preferences.GEMINI_OT_refresh_models,
)
addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gemini_properties = bpy.props.PointerProperty(type=operators.GeminiProperties)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(operators.GEMINI_OT_popup_window.bl_idname, 'G', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi))
    # daily model check a few seconds after Blender starts (one small request, in the background)
    bpy.app.timers.register(preferences.startup_check, first_interval=3.0)


def unregister():
    if bpy.app.timers.is_registered(preferences.startup_check):
        bpy.app.timers.unregister(preferences.startup_check)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gemini_properties
