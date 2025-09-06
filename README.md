# Bluestar Smart AC (Unofficial) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/sankarhansdah/bluestar_hacs.svg)](https://github.com/sankarhansdah/bluestar_hacs/releases)
[![GitHub stars](https://img.shields.io/github/stars/sankarhansdah/bluestar_hacs.svg?style=social&label=Stars)](https://github.com/sankarhansdah/bluestar_hacs)

An **unofficial** Home Assistant integration for Bluestar Smart AC units. This integration provides **standalone** control over your Bluestar Smart AC devices through Home Assistant, including temperature control, fan speed, swing modes, and more.

## ✨ Features

- 🌡️ **Climate Control**: Full HVAC mode control (Off, Fan Only, Cool, Dry, Auto)
- 🌪️ **Fan Control**: Multiple fan speeds (Low, Medium, High, Auto)
- 🔄 **Swing Control**: Independent vertical and horizontal swing control
- 📱 **Display Control**: Turn AC display on/off
- 📊 **Sensors**: RSSI signal strength and error code monitoring
- 🔄 **Force Sync**: Manual device state synchronization
- 🚀 **Standalone Operation**: Works directly with Bluestar cloud API
- ⚡ **Optional Gateway**: Enhanced performance with MQTT gateway
- ☁️ **Cloud Integration**: Direct API access with automatic fallback

## 🚀 Installation

### Via HACS (Recommended)

1. **Add Custom Repository**:
   - Open HACS → Integrations
   - Click the three dots menu → Custom repositories
   - Add repository: `sankarhansdah/bluestar_hacs`
   - Category: Integration

2. **Install Integration**:
   - Find "Bluestar Smart AC (Unofficial)" in HACS
   - Click Install
   - Restart Home Assistant

3. **Configure Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Bluestar Smart AC"
   - Enter your credentials (gateway URL is optional)

### Manual Installation

1. **Download Integration**:
   ```bash
   cd /config/custom_components
   git clone https://github.com/sankarhansdah/bluestar_hacs.git
   ```

2. **Restart Home Assistant**

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Bluestar Smart AC"

## 🔧 Configuration

### Required Information

- **Phone Number**: Your Bluestar account phone number
- **Password**: Your Bluestar account password
- **API Base URL**: `https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod` (default)

### Optional Configuration

- **MQTT Gateway URL**: For enhanced performance (optional)

## 📱 Screenshots

*[Add screenshots of your integration in Home Assistant here]*

## 🛠️ Troubleshooting

### Common Issues

1. **"Unable to connect to Bluestar API"**
   - ✅ **FIXED**: This was caused by incorrect `auth_type` format
   - The integration now uses the correct numeric format

2. **"Invalid credentials"**
   - Verify your phone number and password
   - Try different phone number formats (with/without +91)

3. **"No devices found"**
   - Ensure your Bluestar account has devices registered
   - Check if devices are online in the official Bluestar app

### Debug Mode

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.bluestar_ac: debug
```

## 🔧 Technical Details

### API Integration

- **Base URL**: `https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod`
- **Authentication**: Phone number + password
- **Protocol**: REST API + AWS IoT MQTT
- **Headers**: Exact match with official Bluestar app

### Supported Commands

- **Power**: `{"pow": 1, "ts": <timestamp>, "src": "anmq"}`
- **Temperature**: `{"stemp": "24.0", "ts": <timestamp>, "src": "anmq"}`
- **Mode**: `{"mode": 1, "ts": <timestamp>, "src": "anmq"}`
- **Fan Speed**: `{"fspd": 2, "ts": <timestamp>, "src": "anmq"}`
- **Swing**: `{"hswing": 1, "vswing": 1, "ts": <timestamp>, "src": "anmq"}`

## 📊 Changelog

### Version 2.0.0 (Latest)
- ✅ **FIXED**: Authentication issue (`auth_type` now uses numeric format)
- ✅ **IMPROVED**: Better error handling and user messages
- ✅ **ADDED**: Multiple phone number format support
- ✅ **ADDED**: API endpoint fallback logic
- ✅ **ADDED**: Proper timeout handling
- ✅ **ADDED**: Enhanced logging and debugging

### Version 1.0.0
- Initial release
- Basic climate control
- Fan control
- Switch controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an **unofficial** integration. It is not affiliated with or endorsed by Bluestar India. Use at your own risk.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/sankarhansdah/bluestar_hacs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sankarhansdah/bluestar_hacs/discussions)

## 🙏 Acknowledgments

- Bluestar India for the Smart AC platform
- Home Assistant community for integration framework
- Contributors and testers

---

**Made with ❤️ for the Home Assistant community**
