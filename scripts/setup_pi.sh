#!/bin/bash
# Rally Timing - Raspberry Pi Initial Setup
# Run this script once on a fresh Raspberry Pi

set -e

echo "=== Rally Timing - Raspberry Pi Setup ==="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Setup project
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Creating virtual environment..."
cd "$PROJECT_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the system:"
echo "  cd $PROJECT_DIR"
echo "  bash scripts/start_server.sh"
echo ""
echo "Optional: Configure WiFi hotspot with hostapd + dnsmasq"
echo "  for offline access at the track."
