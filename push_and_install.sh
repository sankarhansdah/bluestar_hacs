#!/bin/bash

# Bluestar Smart AC - GitHub Push and HA Installation Script

echo "🚀 Bluestar Smart AC - GitHub Push and HA Installation"
echo "====================================================="

# Check if we're in the right directory
if [ ! -d "bluestar_ac" ]; then
    echo "❌ Error: bluestar_ac directory not found"
    echo "Please run this script from the bluestar_hacs_github directory"
    exit 1
fi

echo "✅ Found integration files"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not initialized"
    exit 1
fi

echo "✅ Git repository found"

# Check if remote is set
if ! git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "📋 GitHub Repository Setup Required"
    echo "=================================="
    echo "Please follow these steps:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: bluestar_hacs"
    echo "3. Description: Unofficial Home Assistant integration for Bluestar Smart AC units"
    echo "4. Make it Public"
    echo "5. Don't initialize with README"
    echo "6. Click 'Create repository'"
    echo ""
    echo "After creating the repository, run:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/bluestar_hacs.git"
    echo "git push -u origin main"
    echo ""
    read -p "Press Enter after you've created the GitHub repository..."
    
    # Try to add remote
    read -p "Enter your GitHub username: " username
    git remote add origin "https://github.com/$username/bluestar_hacs.git"
fi

echo ""
echo "📤 Pushing to GitHub..."
echo "======================"

# Push to GitHub
if git push -u origin main; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 Repository URL: $(git remote get-url origin)"
else
    echo "❌ Failed to push to GitHub"
    echo "Please check your GitHub credentials and try again"
    exit 1
fi

echo ""
echo "🏠 Home Assistant Installation"
echo "=============================="
echo "Now let's install the integration in Home Assistant..."

# Check if Home Assistant is accessible
if curl -s -o /dev/null -w "%{http_code}" http://192.168.1.15:8123/ | grep -q "200"; then
    echo "✅ Home Assistant is accessible at http://192.168.1.15:8123"
else
    echo "❌ Cannot reach Home Assistant at http://192.168.1.15:8123"
    echo "Please check if Home Assistant is running"
    exit 1
fi

echo ""
echo "📋 Installation Options:"
echo "1. Install via HACS (Recommended)"
echo "2. Manual installation (SSH to HA machine)"
echo "3. Show installation instructions"
echo "4. Test API connection"
echo "5. Exit"

read -p "Choose an option (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔧 HACS Installation Instructions"
        echo "================================="
        echo "1. Go to http://192.168.1.15:8123"
        echo "2. Navigate to HACS → Integrations"
        echo "3. Click the three dots menu → Custom repositories"
        echo "4. Add repository: $(git remote get-url origin | sed 's/\.git$//')"
        echo "5. Category: Integration"
        echo "6. Click 'Add'"
        echo "7. Find 'Bluestar Smart AC (Unofficial)' in the list"
        echo "8. Click 'Download'"
        echo "9. Restart Home Assistant"
        echo "10. Add Integration: Settings → Devices & Services → + Add Integration"
        echo "11. Search for 'Bluestar Smart AC'"
        echo "12. Enter credentials:"
        echo "    - Phone: 9439614598"
        echo "    - Password: Sonu@blue4"
        ;;
    2)
        echo ""
        echo "🔧 Manual Installation"
        echo "====================="
        echo "SSH to your Home Assistant machine and run:"
        echo ""
        echo "cd /config/custom_components"
        echo "git clone $(git remote get-url origin)"
        echo "chmod -R 755 bluestar_hacs/"
        echo ""
        echo "Then restart Home Assistant and add the integration."
        ;;
    3)
        echo ""
        echo "📖 Installation Instructions"
        echo "============================"
        echo "Repository URL: $(git remote get-url origin | sed 's/\.git$//')"
        echo ""
        echo "HACS Installation:"
        echo "1. Add custom repository in HACS"
        echo "2. Install the integration"
        echo "3. Restart Home Assistant"
        echo "4. Add integration via UI"
        echo ""
        echo "Manual Installation:"
        echo "1. Clone repository to /config/custom_components/"
        echo "2. Restart Home Assistant"
        echo "3. Add integration via UI"
        ;;
    4)
        echo ""
        echo "🧪 Testing API Connection"
        echo "========================"
        echo "Testing Bluestar API with fixed authentication..."
        
        response=$(curl -s -X POST "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod/auth/login" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -H "X-APP-VER: v4.11.4-133" \
          -H "X-OS-NAME: Android" \
          -H "X-OS-VER: v13-33" \
          -H "User-Agent: com.bluestarindia.bluesmart" \
          -d '{"auth_id":"9439614598","auth_type":1,"password":"Sonu@blue4"}')
        
        if echo "$response" | grep -q "session"; then
            echo "✅ API connection successful!"
            echo "Response: $response"
        else
            echo "❌ API connection failed"
            echo "Response: $response"
        fi
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo "Repository: $(git remote get-url origin | sed 's/\.git$//')"
echo "Home Assistant: http://192.168.1.15:8123"
echo ""
echo "✅ The integration now includes:"
echo "   - Fixed authentication (auth_type=1)"
echo "   - Better error handling"
echo "   - Multiple phone format support"
echo "   - API endpoint fallback"
echo "   - Proper timeout handling"
echo ""
echo "🔧 Next steps:"
echo "1. Restart Home Assistant"
echo "2. Add the integration"
echo "3. Enter your credentials"
echo "4. Test the connection"
