# Gemini MCP Assistant for Blender

Ask **Google Gemini** anything about Blender — right inside the 3D View — and run the Python it writes with one click.
**Free:** you use **your own free Gemini API key**. No extra installs, no account with us.

> Version **2.1** · Blender **3.0 → 4.x** (4.2+ as an Extension) · GPL-3.0-or-later · by [Gabriel Netto](https://gabrielnetto.com)

## What it does
- **Sidebar panel** (`N` → *Gemini*) and a quick **popup** (`Alt + G`) to ask questions in any language.
- **Runs the Python Gemini writes** with a *Run code* button — an **undo step** is created first (`Ctrl + Z` to go back).
- **Your own free key:** paste it once in Preferences; it stays on your computer.
- **Always on current models:** when Blender starts (once a day) it checks which Gemini models your key can use.
  Retired models disappear from the list; if yours is retired it **switches to the recommended one and tells you** —
  you can change the model anytime (or turn the automatic switch off).
- **Never stuck:** if a model is busy or out of free quota, the next one answers (and the answer says which).
- **No dependencies:** talks to Gemini with Python's standard library — nothing to `pip install`.

## Install
**Blender 4.2 or newer**
1. Download `gemini_mcp_assistant-2.1.0.zip` from **Releases**.
2. *Edit → Preferences → Get Extensions → ⌄ (top right) → Install from Disk…* → choose the zip.

**Blender 3.0 – 4.1**
1. Download `gemini_mcp_assistant-2.1.0-blender3-4.1.zip` from **Releases**.
2. *Edit → Preferences → Add-ons → Install…* → choose the zip → enable **Gemini MCP Assistant**.

## Get your free key (1 minute)
1. Open **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)** and sign in with Google.
2. **Create API key** — use a project **without billing** to stay on the free tier.
3. In Blender: *Preferences → Add-ons → Gemini MCP Assistant* → paste it in **Gemini API Key**.
   The model list loads by itself; the ★ one is recommended.

## Use it
- `N` → **Gemini** tab → type → **Send to Gemini**. Or press **`Alt + G`** in the 3D View.
- When the answer arrives, **Run code in Blender** appears right under *Send*; the code itself is folded (▸ Code) — open it to read it, or use **Copy code**.
- Example: *"Add 20 cubes in a spiral, each with a random emissive color"* → **Run code**.
- Always read the code before running it. `Ctrl + Z` undoes it.

## Privacy
Your prompts go **directly from your computer to Google's Gemini API** with your key (Google's terms apply).
Nothing goes through any other server. The key is saved in Blender's preferences on your machine.

## Support this project
If it saves you time, you can help keep it going:
**[☕ Buy me a coffee](https://buymeacoffee.com/js4qwvqfkgr)** · [More tools, games and art: gabrielnetto.com](https://gabrielnetto.com) · ⭐ Star the repo

## Changelog
- **2.1.0** — after the answer: big **Run code in Blender** button right under *Send*, **Copy answer / Copy code** buttons, explanation shown separately and the **code collapsed** (click to open); long prompts are shown in full under the field.
- **2.0.0** — no `google-generativeai` dependency; automatic daily model check (retired models removed, auto-switch with notice,
  choice remembered); busy/quota fallback; undo step before running code; Blender 4.2+ Extension manifest; GPL-3.0-or-later.
- 1.4.0 — model selector, popup (Alt+G), threaded requests.

## License
GPL-3.0-or-later © 2025-2026 Gabriel Netto. See [LICENSE](LICENSE).
