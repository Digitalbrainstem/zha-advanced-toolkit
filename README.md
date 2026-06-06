# ZHA Advanced Toolkit

Home Assistant custom integration that complements ZHA by exposing friendly entities for advanced Zigbee device settings.

## Current support

- Inovelli VZM32-SN Blue Series mmWave Presence Dimmer/Switch
- Requires ZHA and the relevant ZHA quirk to expose manufacturer clusters

## Install

1. Copy `custom_components/zha_advanced_toolkit` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & services** -> **Add integration**.
4. Add **ZHA Advanced Toolkit**.

The integration discovers supported ZHA devices and adds native Home Assistant entities to the existing ZHA device.

Only one **ZHA Advanced Toolkit** integration entry is needed. The Inovelli/Zigbee devices are discovered from ZHA and exposed as entities under their existing ZHA devices; you do not add each switch with **Add entry**.

## Exposed settings

The first profile focuses on the VZM32-SN wiring/setup settings:

- Switch mode
- Wiring type
- Smart bulb mode
- Aux switch unique scenes
- Local and remote protection
- Invert switch
- Min/max dim levels
- Auto-off timer
- Basic LED color/intensity settings
- Selected mmWave settings and commands

Unknown or firmware-specific select values are shown as **Custom / Unknown** so newer firmware is not hidden from the user.

## Notes

This integration uses ZHA as the Zigbee backend. It does not replace ZHA, pair devices, or manage the Zigbee network.
