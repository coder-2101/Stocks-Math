# Deactivate the current virtual environment if active

deactivate

# Remove the existing virtual environment

rm -rf .venv

# Create a new virtual environment using Homebrew's Python

python3 -m venv .venv

# Activate the new virtual environment

source .venv/bin/activate

# Upgrade pip

pip install --upgrade pip

# Reinstall necessary packages

pip install numpy==1.23.5 pandas_ta yfinance
