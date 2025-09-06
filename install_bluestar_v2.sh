#!/bin/bash

echo "🚀 Bluestar Smart AC Integration v2.0.0 Installer"
echo "================================================"
echo ""

# Check if running in Home Assistant environment
if [ ! -d "/config" ]; then
    echo "❌ Error: This script must be run in Home Assistant environment"
    echo "   Please run this from your Proxmox Home Assistant console"
    exit 1
fi

echo "📦 Downloading Bluestar Integration v2.0.0..."
cd /config/custom_components

# Remove old version if exists
if [ -d "bluestar_ac" ]; then
    echo "🗑️ Removing old integration..."
    rm -rf bluestar_ac
fi

# Download latest version
wget -O bluestar_hacs_v2.zip https://github.com/sankarhansdah/bluestar_hacs/archive/main.zip

if [ $? -ne 0 ]; then
    echo "❌ Failed to download integration"
    exit 1
fi

echo "📂 Extracting integration..."
unzip -o bluestar_hacs_v2.zip

if [ $? -ne 0 ]; then
    echo "❌ Failed to extract integration"
    exit 1
fi

echo "📋 Installing integration files..."
cp -r bluestar_hacs-main/custom_components/bluestar_ac .

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy integration files"
    exit 1
fi

echo "🔐 Setting permissions..."
chmod -R 755 bluestar_ac

echo "🧹 Cleaning up..."
rm -rf bluestar_hacs-main bluestar_hacs_v2.zip

echo ""
echo "✅ Bluestar Smart AC Integration v2.0.0 installed successfully!"
echo ""
echo "🔄 Restarting Home Assistant..."
ha core restart

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for Home Assistant to restart"
echo "2. Go to Settings > Devices & Services"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your phone number and password"
echo ""
echo "✨ Features in v2.0.0:"
echo "   • Built-in MQTT client (no external server needed)"
echo "   • Exact control algorithm from working Node.js server"
echo "   • Enhanced reliability with retry logic"
echo "   • Multiple phone number format support"
echo "   • Standalone operation"
echo ""
echo "🚀 Ready to control your AC!"
