# SPDX-License-Identifier: GPL-3.0-or-later
# Prompt → Gemini (in a background thread) → answer in the sidebar → optional "Run code" with an undo point.

import json
import textwrap
import threading

import bpy

from . import gemini_api as api
from . import preferences as P


class GeminiProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(name="Prompt", default="")
    response: bpy.props.StringProperty(name="Response", default="")
    popup_prompt: bpy.props.StringProperty(name="Popup Prompt", default="")
    busy: bpy.props.BoolProperty(default=False)
    show_code: bpy.props.BoolProperty(name="Show code", default=False)


def _ask(key, model, prompt, auto_switch, out, fallbacks=()):
    """Background thread. Busy model → try the next models (answer says which one replied).
    Retired model → switch to the recommended one (remembered) and answer."""
    try:
        try:
            out["text"] = api.generate(key, model, prompt)
            out["model"] = model
            return
        except api.GeminiError as busy:
            if busy.kind not in ("busy", "quota"):          # free quotas are per model → another model may still answer
                raise
            for alt in [m for m in fallbacks if m != model][:3]:
                try:
                    out["text"] = api.generate(key, alt, prompt)
                    out["model"] = alt
                    out["busy_fallback"] = (model, alt)
                    return
                except api.GeminiError as e3:
                    if e3.kind not in ("busy", "quota"):
                        break
            raise busy
    except api.GeminiError as e:
        if e.kind == "gone" and auto_switch:
            try:
                models = api.list_chat_models(key)
                for best in [m[0] for m in models if m[0] != model][:4]:   # recommended first, next ones if busy
                    try:
                        out["text"] = api.generate(key, best, prompt)
                        out.update(model=best, models=models, switched=(model, best))
                        return
                    except api.GeminiError as e4:
                        if e4.kind not in ("busy", "quota"):
                            raise
            except api.GeminiError as e2:
                e = e2
        hints = {"key": "Check your API key in Preferences → Add-ons → Gemini MCP Assistant.",
                 "quota": "Free limit reached for now — wait a minute and try again.",
                 "billing": "This key's Google project has billing problems. Create a key in a project without billing (free tier).",
                 "busy": "Google is busy right now — try again in a moment.",
                 "gone": "This model is no longer available — choose another one in Preferences."}
        out["error"] = f"{e}\n\n{hints.get(e.kind, '')}".strip()


class GEMINI_OT_send_prompt(bpy.types.Operator):
    bl_idname = "gemini.send_prompt"
    bl_label = "Send to Gemini"
    bl_description = "Send the prompt to Gemini with your own API key"

    from_popup: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def execute(self, context):
        prefs = P.addon_prefs(context)
        props = context.scene.gemini_properties
        if not prefs.api_key:
            self.report({'ERROR'}, "Set your Gemini API key in Preferences → Add-ons → Gemini MCP Assistant.")
            return {'CANCELLED'}
        if not prefs.model:
            models = P.cached_models(prefs)
            prefs.model = api.recommended(models) or "gemini-flash-latest"
        prompt = props.popup_prompt if self.from_popup else props.prompt
        if not prompt.strip():
            self.report({'INFO'}, "The prompt is empty.")
            return {'CANCELLED'}
        props.response = f"Thinking… ({prefs.model})"
        props.busy = True
        if self.from_popup:
            props.popup_prompt = ""
        self._out = {}
        fallbacks = [m[0] for m in P.cached_models(prefs)]
        self._thread = threading.Thread(target=_ask, args=(prefs.api_key, prefs.model, prompt, prefs.auto_switch, self._out, fallbacks), daemon=True)
        self._thread.start()
        self._timer = context.window_manager.event_timer_add(0.2, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type != 'TIMER' or self._thread.is_alive():
            return {'PASS_THROUGH'}
        context.window_manager.event_timer_remove(self._timer)
        props = context.scene.gemini_properties
        props.busy = False
        out = self._out
        if "switched" in out:                                   # model was retired → remember the new one
            prefs = P.addon_prefs(context)
            old, new = out["switched"]
            prefs.model = new
            prefs.models_json = json.dumps(out.get("models", []))
            prefs.notice = f"'{old}' is no longer available → switched to '{new}'."
            context.preferences.is_dirty = True
            self.report({'INFO'}, prefs.notice)
        props.response = out.get("text") or out.get("error") or "No answer."
        props.show_code = False
        if "busy_fallback" in out:
            props.response = f"(Answered by {out['busy_fallback'][1]} — {out['busy_fallback'][0]} was busy or out of free quota.)\n\n" + props.response
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}


class GEMINI_OT_execute_code(bpy.types.Operator):
    bl_idname = "gemini.execute_code"
    bl_label = "Run code"
    bl_description = "Run the Python code from Gemini's answer (an undo step is created first)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        code = api.extract_python_code(context.scene.gemini_properties.response)
        if not code:
            self.report({'WARNING'}, "No Python code block in the answer.")
            return {'CANCELLED'}
        bpy.ops.ed.undo_push(message="Before Gemini code")
        try:
            exec(compile(code, "<gemini>", "exec"), {"bpy": bpy, "__name__": "__main__"})
        except Exception as e:
            context.scene.gemini_properties.response += f"\n\n--- ERROR WHILE RUNNING ---\n{type(e).__name__}: {e}\n(Ctrl+Z undoes the changes.)"
            self.report({'ERROR'}, f"Code error: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Code executed. Ctrl+Z to undo.")
        return {'FINISHED'}


class GEMINI_OT_copy(bpy.types.Operator):
    bl_idname = "gemini.copy"
    bl_label = "Copy"
    bl_description = "Copy Gemini's answer (or only its code) to the clipboard"

    what: bpy.props.EnumProperty(items=[('ANSWER', "Answer", ""), ('CODE', "Code", "")], default='ANSWER', options={'SKIP_SAVE'})

    def execute(self, context):
        resp = context.scene.gemini_properties.response
        text = api.extract_python_code(resp) if self.what == 'CODE' else resp
        if not text:
            self.report({'WARNING'}, "Nothing to copy.")
            return {'CANCELLED'}
        context.window_manager.clipboard = text
        self.report({'INFO'}, "Code copied." if self.what == 'CODE' else "Answer copied.")
        return {'FINISHED'}


def _wrapped(layout, text, width, icon=None):
    col = layout.column(align=True)
    first = True
    for line in (text or "").split("\n"):
        for w in (textwrap.wrap(line, width=width, replace_whitespace=False) or [""]):
            col.label(text=w, icon=icon if (icon and first) else 'NONE')
            first = False
    return col


class GEMINI_OT_popup_window(bpy.types.Operator):
    bl_idname = "gemini.popup_window"
    bl_label = "Ask Gemini"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        self.layout.prop(context.scene.gemini_properties, "popup_prompt", text="")

    def execute(self, context):
        bpy.ops.gemini.send_prompt('INVOKE_DEFAULT', from_popup=True)
        return {'FINISHED'}


class GEMINI_PT_panel(bpy.types.Panel):
    bl_idname = "GEMINI_PT_panel"
    bl_label = "Gemini MCP Assistant"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gemini_properties
        prefs = P.addon_prefs(context)
        if not prefs.api_key:
            col = layout.column()
            col.label(text="Add your free Gemini API key:", icon='ERROR')
            col.operator("wm.url_open", text="1. Get a free key", icon='URL').url = "https://aistudio.google.com/apikey"
            col.operator("preferences.addon_show", text="2. Paste it here", icon='PREFERENCES').module = __package__
            return
        row = layout.row(align=True)
        row.prop(prefs, "model_picker", text="")
        row.operator("gemini.refresh_models", text="", icon='FILE_REFRESH')
        if prefs.notice:
            box = layout.box()
            for line in textwrap.wrap(prefs.notice, max(20, int(context.region.width / 7))):
                box.label(text=line)
        width = max(10, int(context.region.width / 7))
        layout.prop(props, "prompt", text="")
        if len(props.prompt) > width - 4:                       # Blender fields are single-line → show the whole prompt
            box = layout.box()
            _wrapped(box, props.prompt, width - 2)
        sub = layout.row()
        sub.scale_y = 1.3
        sub.enabled = not props.busy
        sub.operator("gemini.send_prompt", text="Thinking…" if props.busy else "Send to Gemini", icon='TIME' if props.busy else 'PLAY')
        if not props.response or props.busy:
            return
        code = api.extract_python_code(props.response)
        if code:                                              # 1) the action first: Run code
            run = layout.row()
            run.scale_y = 1.6
            run.alert = True
            run.operator("gemini.execute_code", text="Run code in Blender", icon='SCRIPT')
        row = layout.row(align=True)                          # 2) copy buttons
        row.operator("gemini.copy", text="Copy answer", icon='COPYDOWN').what = 'ANSWER'
        if code:
            row.operator("gemini.copy", text="Copy code", icon='TEXT').what = 'CODE'
        explanation = api.explanation_text(props.response)    # 3) Gemini's explanation
        if explanation:
            _wrapped(layout.box(), explanation, width)
        if code:                                              # 4) the code, collapsed by default
            box = layout.box()
            n = code.count("\n") + 1
            box.prop(props, "show_code", text=f"Code ({n} lines)", emboss=False,
                     icon='TRIA_DOWN' if props.show_code else 'TRIA_RIGHT')
            if props.show_code:
                col = box.column(align=True)
                col.scale_y = 0.8
                for line in code.split("\n"):
                    for w in (textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) or [""]):
                        col.label(text=w)
            layout.label(text="Review the code before running it · Ctrl+Z undoes it", icon='INFO')
