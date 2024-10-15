# Deactivate the current virtual environment if active

deactivate
rm -rf .venv

python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip

pip install --upgrade pip

# Reinstall necessary packages

pip install numpy==1.23.5 pandas_ta yfinance flask flask_socketio
