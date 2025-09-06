#!/bin/bash

# Bluestar Smart AC Integration - Automated Installation Script
# Run this script in your Home Assistant Proxmox console

echo "🌡️  Bluestar Smart AC Integration Installer"
echo "=============================================="
echo ""

# Check if we're in Home Assistant environment
if [ ! -f "/usr/bin/ha" ]; then
    echo "❌ Error: This script must be run in Home Assistant environment"
    echo "   Please run this from your Proxmox Home Assistant console"
    exit 1
fi

echo "✅ Home Assistant environment detected"
echo ""

# Step 1: Create custom_components directory
echo "📁 Creating custom_components directory..."
mkdir -p /config/custom_components
echo "✅ Directory created"

# Step 2: Download integration files
echo "📥 Downloading Bluestar Smart AC integration..."
cd /config/custom_components

# Download the integration
wget -O bluestar_ac.zip https://github.com/sankarhansdah/bluestar_hacs/archive/refs/heads/main.zip
if [ $? -eq 0 ]; then
    echo "✅ Download completed"
else
    echo "❌ Download failed. Please check your internet connection"
    exit 1
fi

# Step 3: Extract files
echo "📦 Extracting integration files..."
unzip bluestar_ac.zip
if [ $? -eq 0 ]; then
    echo "✅ Extraction completed"
else
    echo "❌ Extraction failed"
    exit 1
fi

# Step 4: Move integration to correct location
echo "📂 Moving integration files..."
mv bluestar_hacs-main/custom_components/bluestar_ac .
if [ $? -eq 0 ]; then
    echo "✅ Files moved successfully"
else
    echo "❌ Failed to move files"
    exit 1
fi

# Step 5: Clean up
echo "🧹 Cleaning up temporary files..."
rm -rf bluestar_hacs-main bluestar_ac.zip
echo "✅ Cleanup completed"

# Step 6: Verify installation
echo "🔍 Verifying installation..."
if [ -d "/config/custom_components/bluestar_ac" ]; then
    echo "✅ Integration files verified"
    echo "📋 Installed files:"
    ls -la /config/custom_components/bluestar_ac/
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "🔄 Restarting Home Assistant..."
ha core restart

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for Home Assistant to restart (2-3 minutes)"
echo "2. Go to: http://192.168.1.15:8123"
echo "3. Navigate to: Settings → Devices & Services"
echo "4. Click: 'Add Integration'"
echo "5. Search for: 'Bluestar Smart AC'"
echo "6. Enter your phone number and password"
echo ""
echo "🌡️  Enjoy controlling your Bluestar Smart AC through Home Assistant!"



