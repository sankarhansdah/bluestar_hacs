#!/bin/bash

# Bluestar Smart AC HACS Integration - Installation Script
# This script helps users install the integration manually

echo "🌡️  Bluestar Smart AC HACS Integration Installer"
echo "=================================================="
echo ""

# Check if Home Assistant is running
if [ ! -d "/config" ]; then
    echo "❌ Error: Home Assistant config directory not found."
    echo "   Please run this script from your Home Assistant environment."
    exit 1
fi

# Check if custom_components directory exists
if [ ! -d "/config/custom_components" ]; then
    echo "📁 Creating custom_components directory..."
    mkdir -p /config/custom_components
fi

# Clone the integration
echo "📥 Downloading Bluestar Smart AC integration..."
cd /config/custom_components

if [ -d "bluestar_ac" ]; then
    echo "⚠️  Integration already exists. Updating..."
    cd bluestar_ac
    git pull origin main
else
    echo "📥 Cloning integration repository..."
    git clone https://github.com/bluestar-integration/bluestar_hacs.git bluestar_ac
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your phone number and password"
echo ""
echo "🎉 Enjoy controlling your Bluestar Smart AC through Home Assistant!"



