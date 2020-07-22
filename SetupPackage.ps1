# Install and setup up virtual environment
pip install virtualenv
virtualenv venv

# Activate virtual environment
& ./venv/Scripts/activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Python module
python setup.py develop

deactivate