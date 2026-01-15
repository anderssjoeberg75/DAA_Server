## 1. System Prerequisites
First, update your system and install Python 3.10+ (required for modern async features) and pip.

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip git -y
```
## 2. Setup Project Directory
Create a directory for the project and navigate into it.

```
mkdir -p ~/DAA_Server
cd ~/DAA_Server
```

## 3. Create a Virtual Environment
It is best practice to run Python applications in an isolated environment to avoid conflicts.

# Create the virtual environment named 'venv'
```
python3 -m venv venv
```
# Activate the environment
```
source venv/bin/activate
```

## 4. Install Dependencies
Install the required libraries listed in your requirements.txt.

```
pip install -r requirements.txt
```

## 5. Configuration Open the settings file and enter your API keys directly.

```
nano config/settings.py
```
Find GOOGLE_API_KEY and paste your key.

Find MQTT_BROKER_IP and set your broker IP.

Ensure service_account.json is in the ~/DAA_Server folder.

Save and exit (Ctrl+O, Enter, Ctrl+X).
