# ESP32 Discovery Guide for Tesy Integration

This guide explains how to discover additional information from your Tesy water heater's ESP32 WiFi module.

## Overview

The Tesy water heaters use an ESP32 WiFi module (black PCB) that may expose additional endpoints and information beyond what the standard API provides. This integration now includes comprehensive discovery tools to help you find and utilize this additional information.

## Discovery Methods

### 1. Automatic Discovery Sensor

The integration automatically creates an "ESP32 Discovery" sensor that:
- Probes common ESP32 endpoints
- Reports the number of endpoints found
- Provides detailed information in the sensor attributes

### 2. Manual Discovery Services

You can manually trigger discovery using Home Assistant services:

#### `tesy.discover_esp32`
Comprehensive endpoint discovery that tests common ESP32 paths:

```yaml
service: tesy.discover_esp32
data:
  entity_id: water_heater.your_tesy_device
```

#### `tesy.get_esp32_system_info`
Get detailed system information:

```yaml
service: tesy.get_esp32_system_info
data:
  entity_id: water_heater.your_tesy_device
```

#### `tesy.get_esp32_wifi_info`
Get WiFi-specific information:

```yaml
service: tesy.get_esp32_wifi_info
data:
  entity_id: water_heater.your_tesy_device
```

#### `tesy.get_esp32_filesystem_info`
Get filesystem information:

```yaml
service: tesy.get_esp32_filesystem_info
data:
  entity_id: water_heater.your_tesy_device
```

## Common ESP32 Endpoints Tested

The discovery tool tests these common ESP32 endpoints:

### System Information
- `/` - Root page
- `/info` - System info
- `/status` - Status page
- `/system` - System details
- `/version` - Firmware version
- `/api/info`, `/api/status`, `/api/system`, `/api/version`

### WiFi Information
- `/wifi` - WiFi status
- `/scan` - WiFi scan results
- `/api/wifi`, `/api/scan`

### Debug Information
- `/debug` - Debug information
- `/heap` - Memory usage
- `/api/debug`, `/api/heap`

### Configuration
- `/config` - Configuration data
- `/api/config`

### Filesystem
- `/files` - File listing
- `/fs` - Filesystem info
- `/spiffs` - SPIFFS filesystem
- `/littlefs` - LittleFS filesystem
- `/api/files`

### Firmware/Update
- `/firmware` - Firmware info
- `/update` - Update interface
- `/restart` - Restart endpoint
- `/reset` - Reset endpoint

### Data Formats
- `/json` - JSON data
- `/data.json` - Data in JSON format
- `/status.json` - Status as JSON
- `/info.json` - Info as JSON
- `/manifest.json` - Manifest file

## Using Discovery Results

### In Automations

You can create automations that respond to discovery events:

```yaml
automation:
  - alias: "ESP32 Discovery Complete"
    trigger:
      - platform: event
        event_type: tesy_esp32_discovery
    action:
      - service: persistent_notification.create
        data:
          title: "ESP32 Discovery Results"
          message: "Found {{ trigger.event.data.discovery_info.endpoints_discovered | length }} endpoints"
```

### In Templates

Access discovery information in templates:

```yaml
sensor:
  - platform: template
    sensors:
      tesy_esp32_endpoints:
        friendly_name: "Tesy ESP32 Endpoints"
        value_template: "{{ state_attr('sensor.your_tesy_esp32_discovery', 'total_endpoints_found') }}"
```

## Manual Endpoint Testing

If you want to manually test specific endpoints, you can use tools like:

### Using curl
```bash
curl http://192.168.1.124/info
curl http://192.168.1.124/api/system
curl http://192.168.1.124/debug
```

### Using Python
```python
import requests

ip = "192.168.1.124"  # Your Tesy device IP
endpoints = ["/info", "/debug", "/wifi", "/system"]

for endpoint in endpoints:
    try:
        response = requests.get(f"http://{ip}{endpoint}", timeout=5)
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"Content: {response.text[:200]}...")
    except Exception as e:
        print(f"{endpoint}: Failed - {e}")
```

## Common ESP32 Information You Might Find

Based on typical ESP32 implementations, you might discover:

### System Information
- Chip ID and model
- Flash size and speed
- Free heap memory
- Uptime
- Reset reason
- CPU frequency

### WiFi Information
- Signal strength details
- Available networks
- Connection history
- MAC addresses
- Network configuration

### Firmware Information
- Build date and time
- Compiler version
- ESP-IDF version
- Custom firmware version

### Configuration
- Device settings
- Network settings
- Sensor calibration data
- Custom parameters

## Troubleshooting

### No Endpoints Found
- Verify the device IP address is correct
- Check that the device is accessible on the network
- Some endpoints may be disabled in the firmware

### Discovery Fails
- Check Home Assistant logs for detailed error messages
- Verify network connectivity
- Try manual endpoint testing with curl

### Limited Information
- Some ESP32 implementations may have minimal web interfaces
- The amount of available information depends on the firmware

## Security Considerations

- Discovery probes only use GET requests
- No authentication credentials are sent
- Only standard HTTP endpoints are tested
- Discovery does not attempt to modify device settings

## Example Discovery Output

A typical discovery might find endpoints like:

```json
{
  "endpoints_discovered": [
    {
      "endpoint": "/",
      "status_code": 200,
      "content_type": "text/html",
      "response_preview": "<!DOCTYPE html><html>..."
    },
    {
      "endpoint": "/info",
      "status_code": 200,
      "content_type": "application/json",
      "response_preview": "{\"chip_id\":\"12345\",\"free_heap\":45000...}"
    }
  ],
  "system_info": {
    "chip_id": "12345",
    "free_heap": 45000,
    "flash_size": 4194304
  }
}
```

## Contributing

If you discover useful endpoints or information, please consider:
- Documenting your findings
- Sharing with the community
- Contributing improvements to the integration

This discovery system helps unlock the full potential of your Tesy ESP32 module!
