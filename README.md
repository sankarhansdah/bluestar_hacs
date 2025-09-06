# Bluestar Smart AC (Unofficial) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/bluestar-integration/bluestar_hacs.svg)](https://github.com/bluestar-integration/bluestar_hacs/releases)
[![GitHub stars](https://img.shields.io/github/stars/bluestar-integration/bluestar_hacs.svg?style=social&label=Stars)](https://github.com/bluestar-integration/bluestar_hacs)

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
   git clone https://github.com/sankarhansdah/bluestar_hacs.git bluestar_ac
   ```

2. **Restart Home Assistant**

3. **Configure Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Bluestar Smart AC"

## ⚙️ Configuration

### Required Fields

- **Phone Number**: Your Bluestar account phone number (include country code)
- **Password**: Your Bluestar account password

### Optional Fields

- **MQTT Gateway URL**: URL of your Node.js gateway (for enhanced performance)
  - Example: `http://localhost:3000`
  - Example: `http://192.168.1.100:3000`
  - **Note**: Integration works standalone without this
- **Base URL**: Bluestar API base URL (usually not needed)

### Configuration Examples

```yaml
# Standalone Mode (Default)
phone: "+919876543210"
password: "your_password"

# With MQTT Gateway (Enhanced Performance)
phone: "+919876543210"
password: "your_password"
mqtt_gateway_url: "http://localhost:3000"
```

## 🔧 How It Works

### Standalone Mode (Default)
The integration works **completely standalone** by connecting directly to the Bluestar cloud API:
- **Direct API**: Communicates directly with Bluestar's cloud servers
- **No Dependencies**: No additional software or services required
- **Automatic Fallback**: Built-in retry mechanisms and error handling
- **Full Control**: All AC features available through Home Assistant

### Enhanced Mode (Optional)
For users who want **maximum performance** and **reliability**:
- **MQTT Gateway**: Use your existing Node.js MQTT gateway
- **Faster Response**: Direct MQTT communication with AWS IoT
- **Better Reliability**: Proven control algorithm from original app
- **Automatic Fallback**: Falls back to direct API if gateway unavailable

## 📱 Entities

For each Bluestar Smart AC device, the integration creates:

### Climate Entity
- **Main AC Control**: Temperature, HVAC mode, fan speed, swing
- **Modes**: Off, Fan Only, Cool, Dry, Auto
- **Temperature Range**: 16.0°C - 30.0°C (0.5°C steps)

### Select Entities
- **Vertical Swing**: Off, 15°, 30°, 45°, 60°, Auto
- **Horizontal Swing**: Off, 15°, 30°, 45°, 60°, Auto

### Switch Entity
- **Display**: Turn AC display on/off

### Button Entity
- **Force Sync**: Manually sync device state

### Sensor Entities
- **RSSI**: Signal strength in dBm
- **Error Code**: Current error status

## Usage

### Basic Control

```yaml
# Turn on AC and set to cool mode
service: climate.set_hvac_mode
target:
  entity_id: climate.ac_climate
data:
  hvac_mode: cool

# Set temperature
service: climate.set_temperature
target:
  entity_id: climate.ac_climate
data:
  temperature: 24.0

# Set fan speed
service: climate.set_fan_mode
target:
  entity_id: climate.ac_climate
data:
  fan_mode: medium
```

### Advanced Control

```yaml
# Set vertical swing
service: select.select_option
target:
  entity_id: select.ac_vertical_swing
data:
  option: "30°"

# Turn off display
service: switch.turn_off
target:
  entity_id: switch.ac_display

# Force sync device
service: button.press
target:
  entity_id: button.ac_force_sync
```

### Automation Examples

```yaml
# Turn on AC when temperature is high
automation:
  - alias: "Turn on AC when hot"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 30
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.ac_climate
        data:
          hvac_mode: cool
      - service: climate.set_temperature
        target:
          entity_id: climate.ac_climate
        data:
          temperature: 24.0

# Turn off AC when leaving home
automation:
  - alias: "Turn off AC when leaving"
    trigger:
      - platform: state
        entity_id: person.you
        to: "not_home"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.ac_climate
        data:
          hvac_mode: off
```

## Troubleshooting

### Common Issues

1. **"Cannot connect" error**:
   - Check your phone number and password
   - Ensure your internet connection is working
   - Verify the MQTT gateway URL is correct (if using gateway)

2. **"Invalid credentials" error**:
   - Double-check your phone number format (include country code)
   - Verify your password is correct
   - Try logging into the official Bluestar app first

3. **Devices not appearing**:
   - Check if devices are connected in the official app
   - Try the Force Sync button
   - Check the integration logs for errors

4. **Control commands not working**:
   - Ensure the device is online and connected
   - Try the Force Sync button
   - Check if using MQTT gateway (recommended)

### Debugging

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.bluestar_ac: debug
```

### Gateway Issues

If using the MQTT gateway:

1. **Check Gateway Status**:
   ```bash
   curl http://localhost:3000/api/devices
   ```

2. **Check Gateway Logs**:
   ```bash
   # In your gateway directory
   npm start
   ```

3. **Test Gateway Login**:
   ```bash
   curl -X POST http://localhost:3000/api/login \
     -H "Content-Type: application/json" \
     -d '{"auth_id":"+919876543210","auth_type":"phone","password":"your_password"}'
   ```

## Technical Details

### Protocol Implementation

This integration uses the exact same control protocol as the official Bluestar Android app:

- **MQTT Primary**: Uses AWS IoT shadow updates with exact payload structure
- **HTTP Fallback**: Direct API calls with mode-specific preferences
- **Force Sync**: Manual state synchronization when needed

### Control Algorithm

The integration follows the "EXACT BLUESTAR CONTROL ALGORITHM":

1. **MQTT Gateway** (if configured): Send control via tested Node.js gateway
2. **Mode Preferences**: Use Bluestar's mode-specific preferences API
3. **Direct Shadow**: Fallback to direct AWS IoT shadow updates
4. **Force Sync**: Final fallback for state synchronization

### Data Flow

```
Home Assistant → Integration → MQTT Gateway → AWS IoT → Bluestar Device
                     ↓
                Direct API (fallback)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/bluestar-integration/bluestar_hacs.git
   cd bluestar_hacs
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**:
   ```bash
   python -m pytest
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with Bluestar India. Use at your own risk. The authors are not responsible for any damage to your devices or account.

## Support

- **Issues**: [GitHub Issues](https://github.com/bluestar-integration/bluestar_hacs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bluestar-integration/bluestar_hacs/discussions)

## Acknowledgments

- Based on reverse engineering of the official Bluestar Smart AC Android app
- Uses the exact MQTT protocol implementation from the original app
- Built on top of the existing Node.js MQTT gateway implementation
