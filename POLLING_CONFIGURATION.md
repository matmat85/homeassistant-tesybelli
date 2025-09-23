# Tesy Integration - Configurable Polling Interval

## New Features

### Configurable Polling Interval
The Tesy integration now supports configurable polling intervals that can be adjusted through Home Assistant's UI.

#### Default Settings
- **Default polling interval**: 30 seconds
- **Minimum interval**: 10 seconds  
- **Maximum interval**: 300 seconds (5 minutes)

#### How to Configure
1. Go to **Settings** > **Devices & Services**
2. Find your **Tesy** integration
3. Click the **Configure** button (gear icon)
4. Adjust the **Update Interval** setting
5. Click **Submit**

The integration will automatically restart with the new polling interval.

### New Sensors

#### Polling Interval Sensor
- **Entity ID**: `sensor.tesy_polling_interval`
- **Purpose**: Shows the current polling interval in seconds
- **Attributes**:
  - `interval_seconds`: Current interval in seconds
  - `interval_minutes`: Current interval in minutes (rounded)
  - `description`: Explanation of what this setting controls
  - `configurable`: Information about how to change it

#### Last Successful Update Sensor  
- **Entity ID**: `sensor.tesy_last_successful_update`
- **Purpose**: Shows when the last successful data retrieval occurred
- **Device Class**: `timestamp` - displays as date/time in HA
- **Attributes**:
  - `last_update_datetime`: Human-readable timestamp
  - `seconds_since_update`: Time elapsed since last update (seconds)
  - `minutes_since_update`: Time elapsed since last update (minutes)
  - `update_interval_seconds`: Current polling interval for reference
  - `status`: "Connected" or "Delayed" based on expected update timing

### Technical Implementation

#### Configuration Storage
The polling interval is stored in the integration's options and persists across Home Assistant restarts.

#### Automatic Reload
When you change the polling interval through the options flow, the integration automatically reloads with the new settings - no manual restart required.

#### Connection Monitoring
The "Last Successful Update" sensor helps monitor connection health:
- Status shows "Connected" if updates are received within expected timeframe
- Status shows "Delayed" if updates are overdue (more than 2x the polling interval)

### Use Cases

#### Fast Updates (10-15 seconds)
- Real-time monitoring during heating cycles
- Quick response to temperature changes
- Higher network/device load

#### Standard Updates (30-60 seconds) 
- Balanced monitoring for general use
- Default recommended setting
- Good compromise between responsiveness and efficiency

#### Slow Updates (120-300 seconds)
- Monitoring when away from home
- Reducing network/device load
- Long-term trend tracking

### Benefits
1. **Customizable**: Adjust polling frequency based on your needs
2. **Transparent**: See exactly when data was last retrieved
3. **Efficient**: Avoid unnecessary polling when real-time data isn't needed
4. **Reliable**: Monitor connection health with status indicators
5. **User-friendly**: Configure through standard HA settings interface

### Troubleshooting
If you experience connection issues:
1. Check the "Last Successful Update" sensor
2. Try increasing the polling interval to reduce device load
3. Monitor the "status" attribute for connection health
