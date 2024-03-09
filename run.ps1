# Check if there is a virtual environment and activate it
if (!(Test-Path .\venv\Scripts\Activate.ps1)) {
    Write-Host "No virtual environment found"
    Write-Host "Creating virtual environment..."
    virtualenv venv
    Write-Host "Virtual environment created"
} else {
    Write-Host "Virtual environment found"
} 

Write-Host "Installing / Updating dependencies..."
# Install / Update dependencies
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt
Write-Host "Dependencies installed / updated"

# Run the script
Write-Host "Starting SimpleCTE..."
.\venv\Scripts\python.exe .\simplecte\main.py

