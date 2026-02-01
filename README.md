# --- Build updater
pyinstaller --onefile --icon=update.ico updater.py

# --- Build tool
# Tạo file spec
pyi-makespec src/main.py --name masood_meta --windowed --add-data "data:./.icons"

# Build
pyinstaller masood_meta.spec --noconfirm
