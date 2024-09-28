import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of packages to install
packages = ['bs4', 'selenium', 'requests', 'chromedriver']

# Install each package
for package in packages:
    install(package)

print("Packages installed successfully.")