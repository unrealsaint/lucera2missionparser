# L2J Reward Editor

A modern, user-friendly tool for editing and synchronizing Lineage 2 One Day Reward data between server-side XML and client-side text formats.

## Features
- **Visual Editor:** Edit reward name, description, category, requirements, reward items, mob IDs, and more in a convenient UI.
- **XML & Text Sync:** Load the authoritative server-side XML and overlay client-side text fields (name, description, category, etc.) for easy updates.
- **Multi-Select & Batch Delete:** Select and delete multiple rewards at once.
- **Mob ID Editing:** Edit mob IDs (for monster kill conditions) with a simple text box.
- **Flexible Requirements:** Supports all requirement types found in your XML.
- **Safe Data Handling:** Only updates text fields from the text file, keeping server-side data authoritative.
- **Export:** Save your changes back to XML and text formats, ready for server and client use.
- **Build to EXE:** Easily build a standalone Windows executable with `build.bat`.

## Usage
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the editor:**
   ```bash
   python reward_editor.py
   ```
3. **Workflow:**
   - Click **Load XML** and select your server-side XML file.
   - (Optional) Click **Load Text** to overlay client-side fields (name, description, category, etc.).
   - Edit rewards as needed. Use the Mob IDs box for monster lists.
   - Save as XML or Text when done.
   - Use **build.bat** to create a standalone `.exe` (requires PyInstaller).

## Notes
- The XML file is the authoritative source for all data except for fields like name, description, and category, which can be overridden by the text file.
- The text file is used for client display and only updates specific fields.
- Mob IDs are handled as a semicolon-separated list in both the UI and text file.

## Credits
**Made by Saint**

---
For questions or improvements, open an issue or PR! 