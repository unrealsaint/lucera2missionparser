# XML Reward Editor

A modern, user-friendly tool for managing mission/reward XML files (such as `onedayreward.xml`) for games or similar systems.

## Features
- **Load, view, and edit** mission/reward XML files with a modern UI
- **Add, modify, and delete** rewards, requirements, and reward items
- **Edit advanced conditions** (minLevel, maxLevel, mobId) for each mission
- **Dark/black theme** with yellow highlights for easy viewing
- **Custom icon and branding**
- **Export as standalone Windows executable** (no Python required for end users)

## How to Use
1. **Install dependencies** (if running from source):
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app**:
   ```bash
   python xml_editor.py
   ```
3. **Load your XML file** (e.g., `onedayreward.xml`).
4. **Edit entries** using the right-side panel:
   - Change ID, name, description, reset time
   - Add/remove reward items and requirements
   - Edit advanced conditions (minLevel, maxLevel, mobId)
5. **Save your changes** back to XML.

## Build as EXE
1. Make sure you have Python 3.8+ and pip installed.
2. Place your icon at `img/Ologo.ico` (already included).
3. Run `build.bat`.
4. The compiled `xml_editor.exe` will appear in the `dist` folder (which opens automatically).

## Notes
- The app preserves the XML structure and formatting.
- All changes are made visually—no manual XML editing required.
- "Made by Saint" is shown in the UI for credit.

## Credits
- UI and logic: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- XML parsing: Python standard library
- Icon: Provided in `img/Ologo.ico`

---
**Made by Saint** 