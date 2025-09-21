# Installation Guide: Tesy Test Enhanced Integration

## 🚀 Quick Installation

This enhanced version of the Tesy integration is installed as **"Tesy Test"** with domain **"tesytest"** to avoid conflicts with the original integration.

### 📁 Installation Path
```
/config/custom_components/tesytest/
```

### 🔧 Manual Installation Steps

1. **Download** this repository
2. **Copy** the `custom_components/tesy/` folder to `custom_components/tesytest/` in your Home Assistant config directory
3. **Restart** Home Assistant
4. **Add Integration**: Go to Settings → Devices & Services → Add Integration → Search for "Tesy Test"

## 🆚 Key Differences from Original

| Aspect | Original "tesy" | Enhanced "tesytest" |
|--------|----------------|---------------------|
| **Domain** | `tesy` | `tesytest` |
| **Integration Name** | "Tesy" | "Tesy Test" |
| **Installation Path** | `/custom_components/tesy/` | `/custom_components/tesytest/` |
| **Services** | `tesy.*` | `tesytest.*` |
| **Events** | `tesy_*` | `tesytest_*` |
| **Entity IDs** | `*.tesy_*` | `*.tesytest_*` |

## 📋 New Features Summary

### Additional Sensors
- **ESP32 Discovery Sensor**: Shows discovered endpoints
- **WiFi Signal Strength**: RSSI and quality percentage
- **Device Uptime**: Seconds, hours, and days since boot
- **Countdown Timer**: Minutes until target temperature (properly interpreted)
- **Error Code Sensor**: Shows specific error codes
- **Hardware Version**: Device hardware version
- **WiFi Network Info**: IP address and SSID
- **Installation Position**: Vertical or horizontal orientation
- **Device Name**: Custom name from device (decoded from extra field)

### Additional Binary Sensors
- **Child Lock Status**: Shows if controls are locked
- **Vacation Mode**: Shows if vacation mode is active
- **Heating Status**: Real-time heating indicator
- **Error Status**: Binary error indicator with error code details

### ESP32 Discovery Services
- `tesytest.discover_esp32` - Probe for additional endpoints
- `tesytest.get_esp32_system_info` - Get system information
- `tesytest.get_esp32_wifi_info` - Get WiFi details
- `tesytest.get_esp32_filesystem_info` - Get filesystem info

## 🔌 Service Usage Examples

### Basic Discovery
```yaml
service: tesytest.discover_esp32
data:
  entity_id: water_heater.tesytest_your_device
```

### System Information
```yaml
service: tesytest.get_esp32_system_info
data:
  entity_id: water_heater.tesytest_your_device
```

### WiFi Information
```yaml
service: tesytest.get_esp32_wifi_info
data:
  entity_id: water_heater.tesytest_your_device
```

## 📊 Enhanced Entity Information

### Water Heater Entity
The main water heater entity now includes these additional attributes:
- `current_target_temperature` - What the controller is actually targeting
- `child_lock` - Child lock status
- `vacation_mode` - Vacation mode status  
- `position` - Installation orientation
- `countdown_timer_minutes` - Time to reach target
- `error_code` - Current error code
- `uptime_days` - Device uptime
- `wifi_signal_quality` - WiFi signal as percentage

### Example Entity IDs
```
water_heater.tesytest_bellislimo
sensor.tesytest_temperature
sensor.tesytest_energy_consumed
sensor.tesytest_wifi_signal
sensor.tesytest_uptime
sensor.tesytest_countdown
sensor.tesytest_error_code
sensor.tesytest_hardware_version
sensor.tesytest_wifi_ip
sensor.tesytest_wifi_ssid
sensor.tesytest_device_name
sensor.tesytest_position
sensor.tesytest_esp32_discovery
binary_sensor.tesytest_child_lock
binary_sensor.tesytest_vacation_mode
binary_sensor.tesytest_heating
binary_sensor.tesytest_error
switch.tesytest_boost_mode
```

## 🔄 Event System

The integration fires events for ESP32 discovery:

### Events Available
- `tesytest_esp32_discovery` - Full discovery results
- `tesytest_esp32_system_info` - System information
- `tesytest_esp32_wifi_info` - WiFi information
- `tesytest_esp32_filesystem_info` - Filesystem information

### Example Automation
```yaml
automation:
  - alias: "Log ESP32 Discovery"
    trigger:
      - platform: event
        event_type: tesytest_esp32_discovery
    action:
      - service: system_log.write
        data:
          message: "ESP32 Discovery found {{ trigger.event.data.discovery_info.endpoints_discovered | length }} endpoints"
```

## ⚠️ Migration Notes

### From Original Tesy Integration
- This runs **alongside** the original integration
- You'll have **both** versions available
- Entity IDs will be **different** (tesytest vs tesy prefix)
- **Reconfigure** your device in the new integration
- **Update** automations to use new service names
- **Update** dashboard cards to use new entity IDs

### Automation Updates Needed
```yaml
# OLD
service: tesy.discover_esp32

# NEW  
service: tesytest.discover_esp32
```

### Dashboard Updates Needed
```yaml
# OLD
entity: water_heater.tesy_your_device

# NEW
entity: water_heater.tesytest_your_device
```

## 🛠️ Troubleshooting

### Integration Not Found
- Ensure files are in `/config/custom_components/tesytest/`
- Check that `manifest.json` has `"domain": "tesytest"`
- Restart Home Assistant completely

### No ESP32 Discovery
- Check device is accessible on network
- Try manual endpoint testing with curl
- Check Home Assistant logs for errors

### Missing Entities
- Verify device is online and responding
- Check coordinator logs for JSON parsing errors
- Ensure device firmware supports the fields

## 🔍 Advanced Discovery

### Manual Endpoint Testing
```bash
# Test your device directly
curl http://YOUR_DEVICE_IP/info
curl http://YOUR_DEVICE_IP/debug
curl http://YOUR_DEVICE_IP/api/system
```

### Custom Endpoint Discovery
Use the ESP32 discovery sensor to find additional endpoints your device might support that aren't in the standard list.

This enhanced integration unlocks the full potential of your ESP32-based Tesy water heater!
