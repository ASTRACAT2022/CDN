#!/bin/bash

# This script installs the CDN node agent and its dependencies.
# It should be run with root privileges.

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# --- Configuration ---
# The URL of the admin panel must be provided as the first argument.
if [ -z "$1" ]; then
    echo "Usage: $0 <admin_panel_url>"
    exit 1
fi

ADMIN_PANEL_URL=$1
AGENT_SOURCE_PATH="agent.py"
AGENT_DEST_PATH="/usr/local/bin/cdn-agent.py"
SERVICE_NAME="cdn-agent"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Starting CDN node installation..."

# 1. Update package lists and install dependencies
echo "Updating package lists and installing dependencies (nginx, python3, python3-pip)..."
apt-get update
apt-get install -y nginx python3 python3-pip

# 2. Install Python dependencies
echo "Installing Python requests library..."
pip3 install requests

# 3. Copy the agent script
echo "Installing the agent script to ${AGENT_DEST_PATH}..."
if [ ! -f "$AGENT_SOURCE_PATH" ]; then
    echo "Error: agent.py not found in the current directory."
    exit 1
fi
cp "$AGENT_SOURCE_PATH" "$AGENT_DEST_PATH"
chmod +x "$AGENT_DEST_PATH"

# 4. Create systemd service file
echo "Creating systemd service file at ${SERVICE_FILE}..."
cat > ${SERVICE_FILE} << EOL
[Unit]
Description=CDN Node Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 ${AGENT_DEST_PATH} ${ADMIN_PANEL_URL}
Restart=always
User=root
Group=root
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOL

# 5. Reload systemd, enable and start the service
echo "Reloading systemd and starting the agent service..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

# 6. Create cache directory for Nginx
mkdir -p /var/cache/nginx

echo "Installation complete."
echo "The CDN agent is now running and will automatically start on boot."
echo "You can check its status with: systemctl status ${SERVICE_NAME}"
echo "Logs can be viewed with: journalctl -u ${SERVICE_NAME}"