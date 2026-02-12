#!/bin/bash
#
# This script installs the external tools required by CyberSentinel
# on a Debian-based Linux distribution (like Ubuntu or Debian).
#

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

echo "--- Updating package lists ---"
apt-get update

echo "--- Installing core dependencies ---"
apt-get install -y nmap sslscan nikto gobuster git python3-pip

echo "--- Installing Dirsearch ---"
# Clone the dirsearch repository
git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch
# Create a symbolic link to make it executable from anywhere
ln -s /opt/dirsearch/dirsearch.py /usr/local/bin/dirsearch

echo "--- Verifying installations ---"
tools=("nmap" "sslscan" "nikto" "gobuster" "dirsearch")
for tool in "${tools[@]}"; do
  if ! command -v $tool &> /dev/null; then
    echo "ERROR: $tool could not be found after installation."
  else
    echo "$tool installed successfully."
  fi
done

echo "--- Installation complete ---"
