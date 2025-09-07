# Bluestar Smart AC Integration - GitHub Installation Guide

## 🚀 Quick Installation via GitHub

### Method 1: HACS Installation (Recommended)

1. **Open HACS** in Home Assistant
2. **Go to Integrations**
3. **Click the three dots menu** → **Custom repositories**
4. **Add repository**:
   - Repository: `sankarhansdah/bluestar_hacs`
   - Category: **Integration**
5. **Click "Add"**
6. **Find "Bluestar Smart AC (Unofficial)"** in the list
7. **Click "Download"**
8. **Restart Home Assistant**
9. **Add Integration**:
   - Go to **Settings** → **Devices & Services**
   - Click **"+ Add Integration"**
   - Search for **"Bluestar Smart AC"**
   - Enter your credentials

### Method 2: Manual GitHub Installation

1. **SSH to your Home Assistant machine**:
   ```bash
   ssh user@192.168.1.15
   ```

2. **Navigate to custom_components directory**:
   ```bash
   cd /config/custom_components
   ```

3. **Clone the repository**:
   ```bash
   git clone https://github.com/sankarhansdah/bluestar_hacs.git
   ```

4. **Set permissions**:
   ```bash
   chmod -R 755 bluestar_hacs/
   ```

5. **Restart Home Assistant**

6. **Add Integration** via web UI

### Method 3: Direct Download

1. **Download the latest release**:
   ```bash
   wget https://github.com/sankarhansdah/bluestar_hacs/archive/main.zip
   ```

2. **Extract and install**:
   ```bash
   unzip main.zip
   cp -r bluestar_hacs-main/custom_components/bluestar_ac /config/custom_components/
   chmod -R 755 /config/custom_components/bluestar_ac/
   ```

3. **Restart Home Assistant**

## 🔧 Configuration

### Required Credentials
- **Phone Number**: `9439614598` (or your phone number)
- **Password**: `Sonu@blue4` (or your password)
- **API Base URL**: `https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod` (default)

### Optional Settings
- **MQTT Gateway URL**: For enhanced performance (optional)

## ✅ What's Fixed in This Version

- ✅ **Authentication Fixed**: `auth_type` now uses numeric format (1) instead of string ("phone")
- ✅ **API Working**: Confirmed API endpoint responds correctly
- ✅ **Better Error Handling**: More specific error messages
- ✅ **Multiple Phone Formats**: Supports various phone number formats
- ✅ **Endpoint Fallback**: Automatic fallback between API endpoints
- ✅ **Timeout Handling**: Proper request timeouts

## 🧪 Testing

### Test API Connection
```bash
curl -X POST "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod/auth/login" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-APP-VER: v4.11.4-133" \
  -H "X-OS-NAME: Android" \
  -H "X-OS-VER: v13-33" \
  -H "User-Agent: com.bluestarindia.bluesmart" \
  -d '{"auth_id":"9439614598","auth_type":1,"password":"Sonu@blue4"}'
```

Expected response: `{"session": "...", "user": {...}, "mi": "..."}`

## 🐛 Troubleshooting

### Issue: "Integration not found"
**Solution**: Make sure the files are in the correct location:
```bash
ls -la /config/custom_components/bluestar_ac/
# Should show: __init__.py, api.py, config_flow.py, etc.
```

### Issue: "Unable to connect to Bluestar API"
**Solution**: This should now be fixed! If it still occurs:
1. Check Home Assistant logs
2. Verify your credentials
3. Test API connection manually

### Issue: "Invalid credentials"
**Solution**: 
1. Double-check your phone number and password
2. Try different phone number formats
3. Make sure your Bluestar account is active

## 📊 Verification

### Check Integration Status
1. Go to **Settings** → **Devices & Services**
2. Find "Bluestar Smart AC" in the list
3. Verify it shows as "Connected"

### Check Entities
1. Go to **Settings** → **Devices & Services** → **Entities**
2. Search for "bluestar"
3. You should see entities like:
   - `climate.bluestar_ac_<device_name>`
   - `fan.bluestar_ac_<device_name>`
   - `switch.bluestar_ac_<device_name>`

## 🔗 Links

- **GitHub Repository**: https://github.com/sankarhansdah/bluestar_hacs
- **Home Assistant**: http://192.168.1.15:8123
- **HACS**: https://hacs.xyz/

## 📞 Support

- **GitHub Issues**: https://github.com/sankarhansdah/bluestar_hacs/issues
- **GitHub Discussions**: https://github.com/sankarhansdah/bluestar_hacs/discussions

---

**The integration should now work perfectly with the authentication fix!**
