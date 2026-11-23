# SPDX-License-Identifier: GPL-3.0-or-later
# Preferences: the user's own API key, the chosen model (saved), and the automatic model check.

import json
import threading
import time

import bpy

from . import gemini_api as api

DAY = 24 * 3600
_items_cache = []          # Blender needs Python to keep EnumProperty item strings alive
_refreshing = False


def addon_prefs(context=None):
    ctx = context or bpy.context
    return ctx.preferences.addons[__package__].preferences


def cached_models(prefs):
    try:
        return [tuple(x) for x in json.loads(prefs.models_json or "[]")]
    except Exception:
        return []


def _redraw():
    wm = bpy.context.window_manager
    for win in wm.windows:
        for area in win.screen.areas:
            area.tag_redraw()


def apply_models(models, error=None, reason="check"):
    """Main thread: store the fresh list and repair the chosen model if it was retired."""
    global _refreshing
    _refreshing = False
    prefs = addon_prefs()
    prefs.last_check = time.time()
    if error is not None:
        prefs.notice = f"Model check failed: {error}"
        _redraw()
        return None
    prefs.models_json = json.dumps(models)
    names = [m[0] for m in models]
    best = api.recommended(models)
    if not prefs.model:
        prefs.model = best
        prefs.notice = f"Using {best} (recommended)."
    elif prefs.model not in names:
        old = prefs.model
        if prefs.auto_switch and best:
            prefs.model = best
            prefs.notice = f"'{old}' is no longer available → switched to '{best}'. You can choose another one anytime."
        else:
            prefs.notice = f"'{old}' is no longer available. Choose another model."
    elif reason == "manual":
        prefs.notice = f"{len(names)} models available. Recommended: {best}."
    bpy.context.preferences.is_dirty = True       # Blender auto-saves preferences
    _redraw()
    return None


def refresh_models(reason="check"):
    """Background thread: ask Google which models this key can use today (Blender never freezes)."""
    global _refreshing
    prefs = addon_prefs()
    if _refreshing or not prefs.api_key:
        return
    _refreshing = True
    key = prefs.api_key

    def work():
        try:
            models, err = api.list_chat_models(key), None
        except api.GeminiError as e:
            models, err = [], str(e)
        bpy.app.timers.register(lambda: apply_models(models, err, reason), first_interval=0.01)

    threading.Thread(target=work, daemon=True).start()


def startup_check():
    """Runs a few seconds after Blender starts: daily model check (cheap, one request)."""
    try:
        prefs = addon_prefs()
    except KeyError:
        return None
    if prefs.api_key and (time.time() - prefs.last_check > DAY or not cached_models(prefs)):
        refresh_models("startup")
    return None


def _on_key_change(self, context):
    self.models_json = "[]"
    if self.api_key:
        refresh_models("manual")


def _enum_items(self, context):
    global _items_cache
    models = cached_models(self)
    best = api.recommended(models)
    items = [(n, (label + "  ★ recommended") if n == best else label, n) for n, label in models]
    if self.model and self.model not in [m[0] for m in models]:
        items.insert(0, (self.model, f"{self.model} (not available now)", "Run a check or choose another model"))
    _items_cache = items or [("NONE", "Press ⟳ to load models", "")]
    return _items_cache


def _enum_get(self):
    for i, it in enumerate(_enum_items(self, None)):
        if it[0] == self.model:
            return i
    return 0


def _enum_set(self, value):
    items = _enum_items(self, None)
    if 0 <= value < len(items) and items[value][0] != "NONE":
        self.model = items[value][0]
        self.notice = f"Model set to {self.model}."


class GeminiAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    api_key: bpy.props.StringProperty(
        name="Gemini API Key", subtype='PASSWORD', update=_on_key_change,
        description="Your own free key from aistudio.google.com/apikey — it stays on this computer")
    model: bpy.props.StringProperty(name="Model", description="Gemini model used for answers")
    model_picker: bpy.props.EnumProperty(
        name="Model", items=_enum_items, get=_enum_get, set=_enum_set,
        description="Models your key can use today (retired ones disappear automatically)")
    auto_switch: bpy.props.BoolProperty(
        name="Switch automatically when my model is retired", default=True,
        description="If Google retires the chosen model, use the recommended one and tell me")
    models_json: bpy.props.StringProperty(default="[]", options={'HIDDEN'})
    last_check: bpy.props.FloatProperty(default=0.0, options={'HIDDEN'})
    notice: bpy.props.StringProperty(default="", options={'HIDDEN'})

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "api_key")
        row = col.row()
        row.operator("wm.url_open", text="Get a free key", icon='URL').url = "https://aistudio.google.com/apikey"
        col.separator()
        row = col.row(align=True)
        row.prop(self, "model_picker")
        row.operator("gemini.refresh_models", text="", icon='FILE_REFRESH')
        col.prop(self, "auto_switch")
        if self.notice:
            col.label(text=self.notice, icon='INFO')
        if self.last_check:
            col.label(text="Last model check: " + time.strftime("%Y-%m-%d %H:%M", time.localtime(self.last_check)))
        col.separator()
        col.label(text="Your prompts are sent to Google Gemini with your key. Review AI code before running it.", icon='LOCKED')


class GEMINI_OT_refresh_models(bpy.types.Operator):
    bl_idname = "gemini.refresh_models"
    bl_label = "Check models now"
    bl_description = "Ask Google which Gemini models your key can use today"

    def execute(self, context):
        if not addon_prefs(context).api_key:
            self.report({'WARNING'}, "Enter your Gemini API key first.")
            return {'CANCELLED'}
        refresh_models("manual")
        self.report({'INFO'}, "Checking available models…")
        return {'FINISHED'}
