#!/bin/bash

# Quick Home Assistant Installation Script

echo "🏠 Installing Bluestar Smart AC Integration in Home Assistant"
echo "============================================================"

# Check if Home Assistant is accessible
if curl -s -o /dev/null -w "%{http_code}" http://192.168.1.15:8123/ | grep -q "200"; then
    echo "✅ Home Assistant is accessible at http://192.168.1.15:8123"
else
    echo "❌ Cannot reach Home Assistant at http://192.168.1.15:8123"
    echo "Please check if Home Assistant is running"
    exit 1
fi

echo ""
echo "📋 Installation Methods:"
echo "1. HACS Installation (Recommended)"
echo "2. Manual Installation (SSH)"
echo "3. Direct Download"
echo "4. Test API Connection"
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
        echo "4. Add repository: https://github.com/sankarhansdah/bluestar_hacs"
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
        echo "    - API URL: https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod"
        echo ""
        echo "🔗 Repository URL: https://github.com/sankarhansdah/bluestar_hacs"
        ;;
    2)
        echo ""
        echo "🔧 Manual Installation (SSH)"
        echo "============================"
        echo "SSH to your Home Assistant machine and run:"
        echo ""
        echo "cd /config/custom_components"
        echo "git clone https://github.com/sankarhansdah/bluestar_hacs.git"
        echo "chmod -R 755 bluestar_hacs/"
        echo ""
        echo "Then restart Home Assistant and add the integration."
        echo ""
        echo "🔗 Repository URL: https://github.com/sankarhansdah/bluestar_hacs"
        ;;
    3)
        echo ""
        echo "🔧 Direct Download"
        echo "=================="
        echo "Download and extract the integration:"
        echo ""
        echo "wget https://github.com/sankarhansdah/bluestar_hacs/archive/main.zip"
        echo "unzip main.zip"
        echo "cp -r bluestar_hacs-main/custom_components/bluestar_ac /config/custom_components/"
        echo "chmod -R 755 /config/custom_components/bluestar_ac/"
        echo ""
        echo "Then restart Home Assistant and add the integration."
        echo ""
        echo "🔗 Repository URL: https://github.com/sankarhansdah/bluestar_hacs"
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
echo "Repository: https://github.com/sankarhansdah/bluestar_hacs"
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
