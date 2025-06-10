@echo off
REM Build the L2J Reward Editor into an executable
pyinstaller --onefile --windowed --name "L2J_Reward_Editor" reward_editor.py
pause 