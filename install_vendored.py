import os
import subprocess
from pathlib import Path
import shutil

def install_vendored():
    vendor_dir = Path(__file__).parent / "vendor"
    print(f"Checking vendor directory: {vendor_dir}")
    
    # Get the Python site-packages directory
    import site
    site_packages = Path(site.getsitepackages()[0])
    print(f"Site packages directory: {site_packages}")
    
    for package_dir in vendor_dir.iterdir():
        if package_dir.is_dir():
            package_name = package_dir.name
            print(f"Installing package: {package_name}")
            
            # Create target directory
            target_dir = site_packages / package_name
            target_dir.mkdir(exist_ok=True)
            
            # Copy all files, including .py and .so files
            for item in package_dir.glob('*'):
                if item.is_file():
                    print(f"Copying {item.name} to {target_dir}")
                    shutil.copy2(item, target_dir)
                    
            # If there's a setup.py, run pip install
            if (package_dir / "setup.py").exists():
                subprocess.check_call(["pip", "install", "--no-deps", str(package_dir)])

if __name__ == "__main__":
    install_vendored()
