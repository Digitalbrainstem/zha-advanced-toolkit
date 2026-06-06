"""Device profiles for ZHA Advanced Toolkit."""

from __future__ import annotations

from dataclasses import replace

from .const import (
    CATEGORY_DIMMING,
    CATEGORY_LED,
    CATEGORY_MMWAVE,
    CATEGORY_PROTECTION,
    CATEGORY_REPORTING,
    CATEGORY_SWITCH,
    INOVELLI_MANUFACTURER_CODE,
)
from .models import (
    CommandEntityDescription,
    NumberEntityDescription,
    Profile,
    SelectEntityDescription,
    SwitchEntityDescription,
    option,
)

EP1 = 1
INOVELLI_CONFIG_CLUSTER = 0xFC31
INOVELLI_MMWAVE_CLUSTER = 0xFC32


def inovelli_select(
    *,
    key: str,
    name: str,
    category: str,
    attribute_id: int,
    attribute_name: str,
    options: tuple,
    cluster_id: int = INOVELLI_CONFIG_CLUSTER,
    enabled_by_default: bool = False,
) -> SelectEntityDescription:
    """Create an Inovelli select entity description."""
    return SelectEntityDescription(
        key=key,
        name=name,
        category=category,
        endpoint_id=EP1,
        cluster_id=cluster_id,
        attribute_id=attribute_id,
        attribute_name=attribute_name,
        manufacturer=INOVELLI_MANUFACTURER_CODE,
        options=options,
        enabled_by_default=enabled_by_default,
    )


def inovelli_switch(
    *,
    key: str,
    name: str,
    category: str,
    attribute_id: int,
    attribute_name: str,
    cluster_id: int = INOVELLI_CONFIG_CLUSTER,
    enabled_by_default: bool = False,
) -> SwitchEntityDescription:
    """Create an Inovelli switch entity description."""
    return SwitchEntityDescription(
        key=key,
        name=name,
        category=category,
        endpoint_id=EP1,
        cluster_id=cluster_id,
        attribute_id=attribute_id,
        attribute_name=attribute_name,
        manufacturer=INOVELLI_MANUFACTURER_CODE,
        enabled_by_default=enabled_by_default,
    )


def inovelli_number(
    *,
    key: str,
    name: str,
    category: str,
    attribute_id: int,
    attribute_name: str,
    minimum: float,
    maximum: float,
    cluster_id: int = INOVELLI_CONFIG_CLUSTER,
    unit: str | None = None,
    enabled_by_default: bool = False,
) -> NumberEntityDescription:
    """Create an Inovelli number entity description."""
    return NumberEntityDescription(
        key=key,
        name=name,
        category=category,
        endpoint_id=EP1,
        cluster_id=cluster_id,
        attribute_id=attribute_id,
        attribute_name=attribute_name,
        manufacturer=INOVELLI_MANUFACTURER_CODE,
        native_min_value=minimum,
        native_max_value=maximum,
        native_unit_of_measurement=unit,
        enabled_by_default=enabled_by_default,
    )


def inovelli_command(
    *,
    key: str,
    name: str,
    category: str,
    cluster_id: int,
    command_id: int,
    params: dict | None = None,
    enabled_by_default: bool = False,
) -> CommandEntityDescription:
    """Create an Inovelli command button entity description."""
    return CommandEntityDescription(
        key=key,
        name=name,
        category=category,
        endpoint_id=EP1,
        cluster_id=cluster_id,
        command_id=command_id,
        manufacturer=INOVELLI_MANUFACTURER_CODE,
        params=params or {},
        enabled_by_default=enabled_by_default,
    )


DIMMING_SETTINGS = (
    inovelli_number(
        key="dimming_speed_up_remote",
        name="Dimming speed up - remote",
        category=CATEGORY_DIMMING,
        attribute_id=0x0001,
        attribute_name="dimming_speed_up_remote",
        minimum=0,
        maximum=126,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="dimming_speed_up_local",
        name="Dimming speed up - local",
        category=CATEGORY_DIMMING,
        attribute_id=0x0002,
        attribute_name="dimming_speed_up_local",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="ramp_rate_off_to_on_remote",
        name="Ramp rate off to on - remote",
        category=CATEGORY_DIMMING,
        attribute_id=0x0003,
        attribute_name="ramp_rate_off_to_on_remote",
        minimum=0,
        maximum=127,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="ramp_rate_off_to_on_local",
        name="Ramp rate off to on - local",
        category=CATEGORY_DIMMING,
        attribute_id=0x0004,
        attribute_name="ramp_rate_off_to_on_local",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="dimming_speed_down_remote",
        name="Dimming speed down - remote",
        category=CATEGORY_DIMMING,
        attribute_id=0x0005,
        attribute_name="dimming_speed_down_remote",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="dimming_speed_down_local",
        name="Dimming speed down - local",
        category=CATEGORY_DIMMING,
        attribute_id=0x0006,
        attribute_name="dimming_speed_down_local",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="ramp_rate_on_to_off_remote",
        name="Ramp rate on to off - remote",
        category=CATEGORY_DIMMING,
        attribute_id=0x0007,
        attribute_name="ramp_rate_on_to_off_remote",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="ramp_rate_on_to_off_local",
        name="Ramp rate on to off - local",
        category=CATEGORY_DIMMING,
        attribute_id=0x0008,
        attribute_name="ramp_rate_on_to_off_local",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="minimum_level",
        name="Minimum dim level",
        category=CATEGORY_DIMMING,
        attribute_id=0x0009,
        attribute_name="minimum_level",
        minimum=1,
        maximum=254,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="maximum_level",
        name="Maximum dim level",
        category=CATEGORY_DIMMING,
        attribute_id=0x000A,
        attribute_name="maximum_level",
        minimum=2,
        maximum=255,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="default_level_local",
        name="Default level - local",
        category=CATEGORY_DIMMING,
        attribute_id=0x000D,
        attribute_name="default_level_local",
        minimum=0,
        maximum=255,
    ),
    inovelli_number(
        key="default_level_remote",
        name="Default level - remote",
        category=CATEGORY_DIMMING,
        attribute_id=0x000E,
        attribute_name="default_level_remote",
        minimum=0,
        maximum=255,
    ),
    inovelli_number(
        key="level_after_power_restored",
        name="Level after power restored",
        category=CATEGORY_DIMMING,
        attribute_id=0x000F,
        attribute_name="state_after_power_restored",
        minimum=0,
        maximum=255,
    ),
)


SWITCH_SETTINGS = (
    inovelli_select(
        key="switch_mode",
        name="Switch mode",
        category=CATEGORY_SWITCH,
        attribute_id=0x0102,
        attribute_name="output_mode",
        options=(
            option(0, "Dimmer", "Allows dimming and level control."),
            option(1, "On / Off", "Acts like a relay switch with no dimming output."),
        ),
        enabled_by_default=True,
    ),
    inovelli_select(
        key="switch_type",
        name="Wiring type",
        category=CATEGORY_SWITCH,
        attribute_id=0x0016,
        attribute_name="switch_type",
        options=(
            option(0, "Single pole", "The switch directly controls one load with no traveler or aux switch."),
            option(1, "Multi-way mode 1 / aux or firmware default", "Use for supported multi-way wiring with an aux/add-on switch on firmwares that expose mode 1."),
            option(2, "Multi-way mode 2 / dumb or alternate aux", "Use for supported multi-way wiring with a dumb switch or alternate aux wiring on firmwares that expose mode 2."),
            option(3, "Multi-way full sine / firmware-specific", "Firmware-specific multi-way mode. Use only when recommended for your wiring."),
        ),
        enabled_by_default=True,
    ),
    inovelli_switch(
        key="smart_bulb_mode",
        name="Smart bulb mode",
        category=CATEGORY_SWITCH,
        attribute_id=0x0034,
        attribute_name="smart_bulb_mode",
        enabled_by_default=True,
    ),
    inovelli_switch(
        key="invert_switch",
        name="Invert switch",
        category=CATEGORY_SWITCH,
        attribute_id=0x000B,
        attribute_name="invert_switch",
        enabled_by_default=True,
    ),
    inovelli_number(
        key="auto_off_timer",
        name="Auto-off timer",
        category=CATEGORY_SWITCH,
        attribute_id=0x000C,
        attribute_name="auto_off_timer",
        minimum=0,
        maximum=32767,
        unit="s",
        enabled_by_default=True,
    ),
    inovelli_number(
        key="quick_start_time",
        name="Quick start time",
        category=CATEGORY_SWITCH,
        attribute_id=0x0017,
        attribute_name="quick_start_time",
        minimum=0,
        maximum=127,
    ),
    inovelli_number(
        key="quick_start_level",
        name="Quick start level",
        category=CATEGORY_SWITCH,
        attribute_id=0x0018,
        attribute_name="quick_start_level",
        minimum=0,
        maximum=254,
    ),
    inovelli_switch(
        key="increased_non_neutral_output",
        name="Increased non-neutral output",
        category=CATEGORY_SWITCH,
        attribute_id=0x0019,
        attribute_name="increased_non_neutral_output",
    ),
    inovelli_select(
        key="leading_or_trailing_edge",
        name="Leading / trailing edge",
        category=CATEGORY_SWITCH,
        attribute_id=0x001A,
        attribute_name="leading_or_trailing_edge",
        options=(
            option(0, "Leading edge", "Forward phase dimming, often used for magnetic/MLV loads."),
            option(1, "Trailing edge", "Reverse phase dimming, often smoother for many LED loads."),
        ),
    ),
    inovelli_number(
        key="button_delay",
        name="Button press delay",
        category=CATEGORY_SWITCH,
        attribute_id=0x0032,
        attribute_name="button_delay",
        minimum=0,
        maximum=9,
    ),
    inovelli_switch(
        key="double_tap_up_enabled",
        name="Enable 2x tap up level",
        category=CATEGORY_SWITCH,
        attribute_id=0x0035,
        attribute_name="double_tap_up_enabled",
    ),
    inovelli_switch(
        key="double_tap_down_enabled",
        name="Enable 2x tap down level",
        category=CATEGORY_SWITCH,
        attribute_id=0x0036,
        attribute_name="double_tap_down_enabled",
    ),
    inovelli_number(
        key="double_tap_up_level",
        name="2x tap up level",
        category=CATEGORY_SWITCH,
        attribute_id=0x0037,
        attribute_name="double_tap_up_level",
        minimum=2,
        maximum=254,
    ),
    inovelli_number(
        key="double_tap_down_level",
        name="2x tap down level",
        category=CATEGORY_SWITCH,
        attribute_id=0x0038,
        attribute_name="double_tap_down_level",
        minimum=0,
        maximum=254,
    ),
    inovelli_switch(
        key="aux_switch_unique_scenes",
        name="Aux switch unique scenes",
        category=CATEGORY_SWITCH,
        attribute_id=0x007B,
        attribute_name="aux_switch_scenes",
        enabled_by_default=True,
    ),
)


LED_SETTINGS = (
    inovelli_number(
        key="load_level_indicator_timeout",
        name="LED indicator timeout",
        category=CATEGORY_LED,
        attribute_id=0x0011,
        attribute_name="load_level_indicator_timeout",
        minimum=0,
        maximum=11,
        unit="s",
    ),
    inovelli_number(
        key="led_color_when_on",
        name="LED color when on",
        category=CATEGORY_LED,
        attribute_id=0x005F,
        attribute_name="led_color_when_on",
        minimum=0,
        maximum=255,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="led_color_when_off",
        name="LED color when off",
        category=CATEGORY_LED,
        attribute_id=0x0060,
        attribute_name="led_color_when_off",
        minimum=0,
        maximum=255,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="led_intensity_when_on",
        name="LED intensity when on",
        category=CATEGORY_LED,
        attribute_id=0x0061,
        attribute_name="led_intensity_when_on",
        minimum=0,
        maximum=100,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="led_intensity_when_off",
        name="LED intensity when off",
        category=CATEGORY_LED,
        attribute_id=0x0062,
        attribute_name="led_intensity_when_off",
        minimum=0,
        maximum=100,
        enabled_by_default=True,
    ),
    inovelli_switch(
        key="led_scaling_mode",
        name="LED bar scaling",
        category=CATEGORY_LED,
        attribute_id=0x0064,
        attribute_name="led_scaling_mode",
    ),
    inovelli_switch(
        key="one_led_mode",
        name="One LED mode",
        category=CATEGORY_LED,
        attribute_id=0x0103,
        attribute_name="on_off_led_mode",
    ),
    inovelli_switch(
        key="firmware_progress_led",
        name="Firmware progress LED",
        category=CATEGORY_LED,
        attribute_id=0x0104,
        attribute_name="firmware_progress_led",
    ),
    inovelli_switch(
        key="disable_clear_notifications_double_tap",
        name="Disable clear notifications by 2x config tap",
        category=CATEGORY_LED,
        attribute_id=0x0106,
        attribute_name="disable_clear_notifications_double_tap",
    ),
) + tuple(
    item
    for led in range(1, 8)
    for item in (
        inovelli_number(
            key=f"default_led{led}_strip_color_when_on",
            name=f"LED {led} color when on",
            category=CATEGORY_LED,
            attribute_id={1: 0x003C, 2: 0x0041, 3: 0x0046, 4: 0x004B, 5: 0x0050, 6: 0x0055, 7: 0x005A}[led],
            attribute_name=f"default_led{led}_strip_color_when_on",
            minimum=0,
            maximum=255,
        ),
        inovelli_number(
            key=f"default_led{led}_strip_color_when_off",
            name=f"LED {led} color when off",
            category=CATEGORY_LED,
            attribute_id={1: 0x003D, 2: 0x0042, 3: 0x0047, 4: 0x004C, 5: 0x0051, 6: 0x0056, 7: 0x005B}[led],
            attribute_name=f"default_led{led}_strip_color_when_off",
            minimum=0,
            maximum=255,
        ),
        inovelli_number(
            key=f"default_led{led}_strip_intensity_when_on",
            name=f"LED {led} intensity when on",
            category=CATEGORY_LED,
            attribute_id={1: 0x003E, 2: 0x0043, 3: 0x0048, 4: 0x004D, 5: 0x0052, 6: 0x0057, 7: 0x005C}[led],
            attribute_name=f"default_led{led}_strip_intensity_when_on",
            minimum=0,
            maximum=101,
        ),
        inovelli_number(
            key=f"default_led{led}_strip_intensity_when_off",
            name=f"LED {led} intensity when off",
            category=CATEGORY_LED,
            attribute_id={1: 0x003F, 2: 0x0044, 3: 0x0049, 4: 0x004E, 5: 0x0053, 6: 0x0058, 7: 0x005D}[led],
            attribute_name=f"default_led{led}_strip_intensity_when_off",
            minimum=0,
            maximum=101,
        ),
    )
)


PROTECTION_SETTINGS = (
    inovelli_switch(
        key="local_protection",
        name="Local protection",
        category=CATEGORY_PROTECTION,
        attribute_id=0x0100,
        attribute_name="local_protection",
        enabled_by_default=True,
    ),
    inovelli_switch(
        key="remote_protection",
        name="Remote protection",
        category=CATEGORY_PROTECTION,
        attribute_id=0x0101,
        attribute_name="remote_protection",
        enabled_by_default=True,
    ),
)


REPORTING_SETTINGS = (
    inovelli_number(
        key="active_power_reports",
        name="Active power report threshold",
        category=CATEGORY_REPORTING,
        attribute_id=0x0012,
        attribute_name="active_power_reports",
        minimum=0,
        maximum=255,
    ),
    inovelli_number(
        key="periodic_power_and_energy_reports",
        name="Periodic power and energy reports",
        category=CATEGORY_REPORTING,
        attribute_id=0x0013,
        attribute_name="periodic_power_and_energy_reports",
        minimum=0,
        maximum=32767,
        unit="s",
    ),
    inovelli_number(
        key="active_energy_reports",
        name="Active energy report threshold",
        category=CATEGORY_REPORTING,
        attribute_id=0x0014,
        attribute_name="active_energy_reports",
        minimum=0,
        maximum=32767,
    ),
)


MMWAVE_SETTINGS = (
    inovelli_select(
        key="light_on_presence_behavior",
        name="Light-on presence behavior",
        category=CATEGORY_MMWAVE,
        attribute_id=0x006E,
        attribute_name="light_on_presence_behavior",
        options=(
            option(0, "Disabled", "Presence does not automatically control the load."),
            option(1, "Auto on/off when occupied", "Turn on when occupied and turn off after vacancy timeout."),
            option(2, "Auto off when vacant", "Only turn off automatically when the room becomes vacant."),
            option(3, "Auto on when occupied", "Only turn on automatically when presence is detected."),
            option(4, "Auto on/off when vacant", "Firmware-specific behavior for vacancy-triggered automation."),
            option(5, "Auto on when vacant", "Firmware-specific behavior. Use only if documented for your firmware."),
            option(6, "Auto off when occupied", "Firmware-specific behavior. Use only if documented for your firmware."),
        ),
        enabled_by_default=True,
    ),
    inovelli_select(
        key="mmwave_room_size_preset",
        name="mmWave room size",
        category=CATEGORY_MMWAVE,
        attribute_id=0x0075,
        attribute_name="mmwave_room_size_preset",
        options=(
            option(0, "Custom", "Use the manual width/depth/height boundary values."),
            option(1, "X-Small", "Small enclosed space or very close detection area."),
            option(2, "Small", "Small room or tight detection area."),
            option(3, "Medium", "Typical room-sized detection area."),
            option(4, "Large", "Larger room-sized detection area."),
            option(5, "X-Large", "Largest preset detection area."),
        ),
        enabled_by_default=True,
    ),
    inovelli_number(
        key="mmwave_height_minimum_floor",
        name="mmWave height minimum floor",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0065,
        attribute_name="mmwave_height_minimum_floor",
        minimum=-600,
        maximum=600,
    ),
    inovelli_number(
        key="mmwave_height_maximum_ceiling",
        name="mmWave height maximum ceiling",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0066,
        attribute_name="mmwave_height_maximum_ceiling",
        minimum=-600,
        maximum=600,
    ),
    inovelli_number(
        key="mmwave_width_minimum_left",
        name="mmWave width minimum left",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0067,
        attribute_name="mmwave_width_minimum_left",
        minimum=-600,
        maximum=600,
    ),
    inovelli_number(
        key="mmwave_width_maximum_right",
        name="mmWave width maximum right",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0068,
        attribute_name="mmwave_width_maximum_right",
        minimum=-600,
        maximum=600,
    ),
    inovelli_number(
        key="mmwave_depth_minimum_near",
        name="mmWave depth minimum near",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0069,
        attribute_name="mmwave_depth_minimum_near",
        minimum=0,
        maximum=600,
    ),
    inovelli_number(
        key="mmwave_depth_maximum_far",
        name="mmWave depth maximum far",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x006A,
        attribute_name="mmwave_depth_maximum_far",
        minimum=0,
        maximum=600,
    ),
    inovelli_switch(
        key="mmwave_target_info_report",
        name="mmWave target info report",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x006B,
        attribute_name="mmwave_target_info_report",
    ),
    inovelli_number(
        key="mmwave_stay_life",
        name="mmWave stay life",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x006C,
        attribute_name="mmwave_stay_life",
        minimum=0,
        maximum=3600,
        unit="s",
        enabled_by_default=True,
    ),
    inovelli_number(
        key="mmwave_sensitivity",
        name="mmWave sensitivity",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0070,
        attribute_name="mmwave_detect_sensitivity",
        minimum=0,
        maximum=2,
        enabled_by_default=True,
    ),
    inovelli_number(
        key="mmwave_trigger_speed",
        name="mmWave trigger speed",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0071,
        attribute_name="mmwave_detect_trigger",
        minimum=0,
        maximum=2,
    ),
    inovelli_number(
        key="mmwave_detection_timeout",
        name="mmWave detection timeout",
        category=CATEGORY_MMWAVE,
        cluster_id=INOVELLI_MMWAVE_CLUSTER,
        attribute_id=0x0072,
        attribute_name="mmwave_hold_time",
        minimum=0,
        maximum=4294967295,
        unit="s",
        enabled_by_default=True,
    ),
)


FAN_BINDING_SETTINGS = (
    inovelli_select(
        key="fan_single_tap_behavior",
        name="Fan single-tap behavior",
        category=CATEGORY_SWITCH,
        attribute_id=0x0078,
        attribute_name="fan_single_tap_behavior",
        options=(
            option(0, "Disabled", "Single tap does not change fan speed behavior."),
            option(1, "Cycle", "Single tap cycles through fan speed levels."),
            option(2, "Favorite", "Single tap jumps to the configured favorite fan level."),
        ),
    ),
    inovelli_switch(
        key="fan_timer_display",
        name="Fan timer display",
        category=CATEGORY_SWITCH,
        attribute_id=0x0079,
        attribute_name="fan_timer_display",
    ),
    inovelli_switch(
        key="binding_off_to_on_sync_level",
        name="Binding default level sync",
        category=CATEGORY_SWITCH,
        attribute_id=0x007D,
        attribute_name="binding_off_to_on_sync_level",
    ),
    inovelli_number(
        key="fan_module_binding_control",
        name="Fan module binding control",
        category=CATEGORY_SWITCH,
        attribute_id=0x0082,
        attribute_name="fan_module_binding_control",
        minimum=0,
        maximum=2,
    ),
    inovelli_number(
        key="low_for_bound_control",
        name="Low level for bound fan control",
        category=CATEGORY_SWITCH,
        attribute_id=0x0083,
        attribute_name="low_for_bound_control",
        minimum=2,
        maximum=254,
    ),
    inovelli_number(
        key="medium_for_bound_control",
        name="Medium level for bound fan control",
        category=CATEGORY_SWITCH,
        attribute_id=0x0084,
        attribute_name="medium_for_bound_control",
        minimum=2,
        maximum=254,
    ),
    inovelli_number(
        key="high_for_bound_control",
        name="High level for bound fan control",
        category=CATEGORY_SWITCH,
        attribute_id=0x0085,
        attribute_name="high_for_bound_control",
        minimum=2,
        maximum=254,
    ),
    inovelli_number(
        key="led_color_for_bound_control",
        name="LED color for bound fan control",
        category=CATEGORY_LED,
        attribute_id=0x0086,
        attribute_name="led_color_for_bound_control",
        minimum=0,
        maximum=255,
    ),
)


SETTING_DESCRIPTIONS = {
    "switch_mode": "Choose whether the device controls the load as a dimmer or as a simple on/off relay.",
    "switch_type": "Match this to the wiring at the wall. Incorrect wiring mode can make multi-way or aux switches behave incorrectly.",
    "smart_bulb_mode": "Keeps power available to smart bulbs while still sending switch events to Home Assistant.",
    "invert_switch": "Reverses the local paddle direction when the physical orientation or wiring makes up/down feel backwards.",
    "auto_off_timer": "Automatically turns the load off after this many seconds. Set to 0 to disable.",
    "quick_start_time": "Briefly boosts output at turn-on to help some bulbs start reliably.",
    "quick_start_level": "Brightness level used during the quick-start boost.",
    "increased_non_neutral_output": "Raises non-neutral output behavior for loads that need more power to operate reliably.",
    "leading_or_trailing_edge": "Selects the dimming phase style. Trailing edge is often smoother for LEDs; leading edge may be needed for some transformers.",
    "button_delay": "Delay used to distinguish single taps from multi-taps. Lower is faster; higher makes multi-taps easier.",
    "double_tap_up_enabled": "Enables a dedicated level when the up paddle is double-tapped.",
    "double_tap_down_enabled": "Enables a dedicated level when the down paddle is double-tapped.",
    "double_tap_up_level": "Target level used when double-tapping up.",
    "double_tap_down_level": "Target level used when double-tapping down.",
    "aux_switch_unique_scenes": "Makes aux/add-on switch actions generate separate scene events from the main paddle.",
    "dimming_speed_up_remote": "How quickly brightness increases from Zigbee/Home Assistant commands.",
    "dimming_speed_up_local": "How quickly brightness increases from the physical paddle.",
    "dimming_speed_down_remote": "How quickly brightness decreases from Zigbee/Home Assistant commands.",
    "dimming_speed_down_local": "How quickly brightness decreases from the physical paddle.",
    "ramp_rate_off_to_on_remote": "Transition time from off to on for Zigbee/Home Assistant commands.",
    "ramp_rate_off_to_on_local": "Transition time from off to on from the physical paddle.",
    "ramp_rate_on_to_off_remote": "Transition time from on to off for Zigbee/Home Assistant commands.",
    "ramp_rate_on_to_off_local": "Transition time from on to off from the physical paddle.",
    "minimum_level": "Lowest output level the dimmer will use. Raise this if bulbs flicker or turn off at low levels.",
    "maximum_level": "Highest output level the dimmer will use. Lower this if bulbs flicker or overdrive at full output.",
    "default_level_local": "Default brightness used from the physical paddle. 0 typically means use the previous level.",
    "default_level_remote": "Default brightness used from Zigbee/Home Assistant commands. 0 typically means use the previous level.",
    "level_after_power_restored": "Brightness/load state restored after power is lost and returns.",
    "load_level_indicator_timeout": "How long the LED bar shows the current load level after a change.",
    "led_color_when_on": "LED bar color while the load is on.",
    "led_color_when_off": "LED bar color while the load is off.",
    "led_intensity_when_on": "LED bar brightness while the load is on.",
    "led_intensity_when_off": "LED bar brightness while the load is off.",
    "led_scaling_mode": "Changes how the LED bar represents load level.",
    "one_led_mode": "Uses a single LED indicator instead of the full bar when supported.",
    "firmware_progress_led": "Allows firmware update progress to display on the LED bar.",
    "disable_clear_notifications_double_tap": "Prevents clearing LED notifications by double-tapping the config button.",
    "local_protection": "Disables local paddle control while still allowing remote control.",
    "remote_protection": "Disables remote/Zigbee control while preserving local control.",
    "active_power_reports": "How much active power must change before the device sends a report.",
    "periodic_power_and_energy_reports": "How often the device sends periodic power/energy reports.",
    "active_energy_reports": "How much energy must change before the device sends a report.",
    "light_on_presence_behavior": "Controls how the mmWave presence sensor automatically affects the load.",
    "mmwave_room_size_preset": "Preset detection boundary size for the mmWave sensor.",
    "mmwave_height_minimum_floor": "Lower vertical boundary for mmWave detection.",
    "mmwave_height_maximum_ceiling": "Upper vertical boundary for mmWave detection.",
    "mmwave_width_minimum_left": "Left boundary for mmWave detection.",
    "mmwave_width_maximum_right": "Right boundary for mmWave detection.",
    "mmwave_depth_minimum_near": "Nearest depth boundary for mmWave detection.",
    "mmwave_depth_maximum_far": "Farthest depth boundary for mmWave detection.",
    "mmwave_target_info_report": "Enables extra target information reporting from the mmWave module.",
    "mmwave_stay_life": "How long occupancy remains active after motion/presence stops.",
    "mmwave_sensitivity": "How sensitive the mmWave sensor is to presence.",
    "mmwave_trigger_speed": "How quickly the mmWave sensor triggers presence.",
    "mmwave_detection_timeout": "How long detection is held before clearing.",
    "fan_single_tap_behavior": "Controls how a fan switch handles single-tap fan commands.",
    "fan_timer_display": "Shows fan timer/countdown information on the LED bar when supported.",
    "binding_off_to_on_sync_level": "Syncs bound devices to the default level when turning on.",
    "fan_module_binding_control": "Controls fan module binding behavior.",
    "low_for_bound_control": "Level sent for low speed to a bound fan module.",
    "medium_for_bound_control": "Level sent for medium speed to a bound fan module.",
    "high_for_bound_control": "Level sent for high speed to a bound fan module.",
    "led_color_for_bound_control": "LED color used for bound fan control feedback.",
}


def _description_for(setting) -> str | None:
    """Return a description for a setting."""
    if setting.key in SETTING_DESCRIPTIONS:
        return SETTING_DESCRIPTIONS[setting.key]
    if "color" in setting.key:
        return "LED color. The toolkit shows a color picker and converts it to the raw Inovelli hue value."
    if "intensity" in setting.key:
        return "LED brightness percentage for this indicator."
    return None


def _presentation_for(setting) -> str | None:
    """Return the preferred UI presentation for a setting."""
    if "color" in setting.key:
        return "color_hue"
    return None


def with_metadata(settings):
    """Attach descriptions and presentation hints to profile settings."""
    return tuple(
        replace(
            setting,
            description=_description_for(setting),
            presentation=_presentation_for(setting),
        )
        for setting in settings
    )


COMMON_SWITCH_DIMMER_SETTINGS = with_metadata(
    SWITCH_SETTINGS
    + DIMMING_SETTINGS
    + LED_SETTINGS
    + PROTECTION_SETTINGS
    + REPORTING_SETTINGS
)

COMMON_SWITCH_SETTINGS = with_metadata(
    SWITCH_SETTINGS + LED_SETTINGS + PROTECTION_SETTINGS + REPORTING_SETTINGS
)

COMMON_FAN_SWITCH_SETTINGS = with_metadata(
    SWITCH_SETTINGS
    + LED_SETTINGS
    + PROTECTION_SETTINGS
    + REPORTING_SETTINGS
    + FAN_BINDING_SETTINGS
)


VZM32_SN = Profile(
    name="Inovelli VZM32-SN",
    manufacturer="Inovelli",
    model="VZM32-SN",
    settings=(
        COMMON_SWITCH_DIMMER_SETTINGS
        + with_metadata(MMWAVE_SETTINGS + FAN_BINDING_SETTINGS)
    ),
    commands=(
        inovelli_command(
            key="reset_energy_meter",
            name="Reset energy meter",
            category=CATEGORY_REPORTING,
            cluster_id=INOVELLI_CONFIG_CLUSTER,
            command_id=0x02,
        ),
        inovelli_command(
            key="mmwave_reset_module",
            name="Reset mmWave module",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 0},
        ),
        inovelli_command(
            key="mmwave_generate_interference_area",
            name="Generate mmWave interference area",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 1},
            enabled_by_default=True,
        ),
        inovelli_command(
            key="mmwave_obtain_areas",
            name="Obtain mmWave areas",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 2},
        ),
        inovelli_command(
            key="mmwave_clear_interference_area",
            name="Clear mmWave interference area",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 3},
        ),
        inovelli_command(
            key="mmwave_reset_detection_area",
            name="Reset mmWave detection area",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 4},
        ),
        inovelli_command(
            key="mmwave_clear_stay_area",
            name="Clear mmWave stay area",
            category=CATEGORY_MMWAVE,
            cluster_id=INOVELLI_MMWAVE_CLUSTER,
            command_id=0x00,
            params={"control_id": 5},
        ),
    ),
)

VZM31_SN = Profile(
    name="Inovelli VZM31-SN",
    manufacturer="Inovelli",
    model="VZM31-SN",
    settings=COMMON_SWITCH_DIMMER_SETTINGS,
    commands=VZM32_SN.commands[:1],
)

VZM30_SN = Profile(
    name="Inovelli VZM30-SN",
    manufacturer="Inovelli",
    model="VZM30-SN",
    settings=COMMON_SWITCH_SETTINGS,
    commands=VZM32_SN.commands[:1],
)

VZM35_SN = Profile(
    name="Inovelli VZM35-SN",
    manufacturer="Inovelli",
    model="VZM35-SN",
    settings=COMMON_FAN_SWITCH_SETTINGS,
    commands=VZM32_SN.commands[:1],
)

PROFILES = (VZM32_SN, VZM31_SN, VZM30_SN, VZM35_SN)


def get_matching_profile(manufacturer: str | None, model: str | None) -> Profile | None:
    """Return a matching device profile."""
    for profile in PROFILES:
        if profile.matches(manufacturer, model):
            return profile
    return None
