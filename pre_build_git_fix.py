import os
from pathlib import Path

# Ensure the directories expected by ESP-IDF / CMake during PlatformIO pre-build
dirs = [
    Path(".pio/build/esp32dev/CMakeFiles/git-data"),
    Path(".pio/build/esp32dev/bootloader/CMakeFiles/git-data")
]

for build_dir in dirs:
    build_dir.mkdir(parents=True, exist_ok=True)
    head_ref = build_dir / "head-ref"
    head_ref.write_text("0123456789abcdef0123456789abcdef01234567\n", encoding="utf-8")
