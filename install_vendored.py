import os
import subprocess
from pathlib import Path

def install_vendored():
    vendor_dir = Path(__file__).parent / "vendor"
    for item in vendor_dir.glob("*"):
        if item.is_dir() and (item / "setup.py").exists():
            subprocess.check_call(["pip", "install", "--no-deps", str(item)])
        elif item.suffix in ('.whl', '.tar.gz'):
            subprocess.check_call(["pip", "install", "--no-deps", str(item)])

if __name__ == "__main__":
    install_vendored()
