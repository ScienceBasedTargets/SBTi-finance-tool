# Activate virtual environment
& ./venv/Scripts/activate.ps1

# Install all requirements
pip install -r requirements.txt

# Install and use pip-licenses to get list of dependencies
pip install --upgrade pip-licenses
pip-licenses --with-system --format=markdown > SBTi-tat-licenses.md
