# ZHA Advanced Toolkit

Home Assistant custom integration that complements ZHA with device-page advanced configuration and native entities for common Zigbee device settings.

## Current support

- Inovelli VZM32-SN Blue Series mmWave Presence Dimmer/Switch
- Requires ZHA and the relevant ZHA quirk to expose manufacturer clusters

## Install

1. Copy `custom_components/zha_advanced_toolkit` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & services** -> **Add integration**.
4. Add **ZHA Advanced Toolkit**.

The integration discovers supported ZHA devices and adds an **Open configuration** action to each supported ZHA device page.

Only one **ZHA Advanced Toolkit** integration entry is needed. The Inovelli/Zigbee devices are discovered from ZHA; you do not add each switch with **Add entry**.

## Device-page configuration

Open the supported ZHA device in Home Assistant and use **Open configuration** to view grouped advanced configuration settings, read current Zigbee values, write changes, and run supported device commands for that device.

The panel also includes **Raw cluster access** for attributes that do not have friendly controls yet. This lets you load exposed ZHA clusters and read/write endpoint, cluster, and attribute IDs directly from the same UI.

Home Assistant does not expose a supported API for custom integrations to add a new tab inside ZHA's built-in **Manage Zigbee Device** dialog. The toolkit therefore uses Home Assistant's supported device `configuration_url` action, which lives on the device page without patching ZHA's frontend.

## Configuration entities

Common setup controls are still exposed as Home Assistant **configuration entities** on the existing ZHA device page for quick access. The full advanced configuration surface is opened from the device page so the entity list does not become overloaded with rarely changed settings.

## Exposed settings

The first profile exposes VZM32-SN settings including:

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
