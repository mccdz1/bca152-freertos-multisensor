Import("env")
import shutil
import os

def copy_firmware(source, target, env):
    build_dir = env.subst("$BUILD_DIR")
    bin_path = os.path.join(build_dir, "firmware.bin")
    elf_path = os.path.join(build_dir, "firmware.elf")
    if os.path.exists(bin_path):
        shutil.copy(bin_path, "firmware.bin")
    if os.path.exists(elf_path):
        shutil.copy(elf_path, "firmware.elf")

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", copy_firmware)
