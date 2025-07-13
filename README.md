# Weider WT16 Heat Pump Integration for Home Assistant

A custom Home Assistant integration for monitoring and controlling Weider WT16 heat pumps via Modbus TCP.

## Features

- **Temperature Monitoring**: Read various temperature sensors from the heat pump
- **Binary Sensors**: Monitor operational states, pumps, and fault conditions
- **Climate Control**: Control room temperature and hot water temperature setpoints
- **Real-time Data**: Continuous monitoring with configurable update intervals
- **Easy Setup**: Configuration flow with automatic device discovery

## Installation

### HACS (Recommended)
1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Install"
6. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/weider_wt16` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Weider WT16 Heat Pump"
3. Enter your heat pump's IP address (default port: 502, Modbus address: 1)
4. Click Submit

## Available Entities

### Sensors
- Room temperature (actual and setpoint)
- Hot water temperature (actual and setpoint)
- Various heat pump temperatures (flow, return, evaporator, etc.)
- Pressure readings
- Volume flow
- Runtime counters

### Binary Sensors
- Compressor status
- Pump states (heating, hot water, mixer)
- Flow monitor
- Fault conditions
- Lock states (heating, hot water, EVU)
- SGready signals

### Climate Entities
- Room temperature control
- Hot water temperature control

## Network Configuration

Ensure your Weider WT16 heat pump is connected to your network and accessible via Modbus TCP:
- Default IP: Configure on your heat pump's network settings
- Default Port: 502
- Default Modbus Address: 1

## Supported Models

- Weider WT16

## Troubleshooting

### Connection Issues
- Verify the heat pump is connected to your network
- Check firewall settings allow Modbus TCP traffic on port 502
- Ensure the IP address is correct
- Verify Modbus TCP is enabled on the heat pump

### Sensor Data Issues
- Some sensors may not be available on all heat pump configurations
- Check the heat pump's manual for supported registers
- Sensor values of 0 may indicate disconnected sensors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.