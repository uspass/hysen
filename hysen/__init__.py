#!/usr/bin/env python3

from .hysenheating import (
    HysenHeatingDevice,
    HYSENHEAT_KEY_LOCK_OFF,
    HYSENHEAT_KEY_LOCK_ON,
    HYSENHEAT_POWER_OFF,
    HYSENHEAT_POWER_ON,
    HYSENHEAT_VALVE_OFF,
    HYSENHEAT_VALVE_ON,
    HYSENHEAT_MANUAL_IN_AUTO_OFF,
    HYSENHEAT_MANUAL_IN_AUTO_ON,
    HYSENHEAT_MODE_MANUAL,
    HYSENHEAT_MODE_AUTO,
    HYSENHEAT_SCHEDULE_12345_67,
    HYSENHEAT_SCHEDULE_123456_7,
    HYSENHEAT_SCHEDULE_1234567,
    HYSENHEAT_SENSOR_INTERNAL,
    HYSENHEAT_SENSOR_EXTERNAL,
    HYSENHEAT_SENSOR_INT_EXT,
    HYSENHEAT_HYSTERESIS_MIN,
    HYSENHEAT_HYSTERESIS_MAX,
    HYSENHEAT_CALIBRATION_MIN,
    HYSENHEAT_CALIBRATION_MAX,
    HYSENHEAT_FROST_PROTECTION_OFF,
    HYSENHEAT_FROST_PROTECTION_ON,
    HYSENHEAT_POWERON_OFF,
    HYSENHEAT_POWERON_ON,
    HYSENHEAT_MAX_TEMP,
    HYSENHEAT_MIN_TEMP,
    HYSENHEAT_WEEKDAY_MONDAY,
    HYSENHEAT_WEEKDAY_SUNDAY
)
from .hysen2pfc import (
    Hysen2PipeFanCoilDevice,
    HYSEN2PFC_KEY_LOCK_OFF,
    HYSEN2PFC_KEY_LOCK_ON,
    HYSEN2PFC_KEY_ALL_UNLOCKED,
    HYSEN2PFC_KEY_POWER_UNLOCKED,
    HYSEN2PFC_KEY_ALL_LOCKED,
    HYSEN2PFC_POWER_OFF,
    HYSEN2PFC_POWER_ON,
    HYSEN2PFC_VALVE_OFF,
    HYSEN2PFC_VALVE_ON,
    HYSEN2PFC_HYSTERESIS_HALVE,
    HYSEN2PFC_HYSTERESIS_WHOLE,
    HYSEN2PFC_CALIBRATION_MIN,
    HYSEN2PFC_CALIBRATION_MAX,
    HYSEN2PFC_FAN_LOW,
    HYSEN2PFC_FAN_MEDIUM,
    HYSEN2PFC_FAN_HIGH,
    HYSEN2PFC_FAN_AUTO,
    HYSEN2PFC_MODE_FAN,
    HYSEN2PFC_MODE_COOL,
    HYSEN2PFC_MODE_HEAT,
    HYSEN2PFC_FAN_CONTROL_ON,
    HYSEN2PFC_FAN_CONTROL_OFF,
    HYSEN2PFC_FROST_PROTECTION_OFF,
    HYSEN2PFC_FROST_PROTECTION_ON,
    HYSEN2PFC_SCHEDULE_TODAY,
    HYSEN2PFC_SCHEDULE_12345,
    HYSEN2PFC_SCHEDULE_123456,
    HYSEN2PFC_SCHEDULE_1234567,
    HYSEN2PFC_PERIOD_DISABLED,
    HYSEN2PFC_PERIOD_ENABLED,
    HYSEN2PFC_COOLING_MAX_TEMP,
    HYSEN2PFC_COOLING_MIN_TEMP,
    HYSEN2PFC_HEATING_MAX_TEMP,
    HYSEN2PFC_HEATING_MIN_TEMP,
    HYSEN2PFC_MAX_TEMP,
    HYSEN2PFC_MIN_TEMP,
    HYSEN2PFC_WEEKDAY_MONDAY,
    HYSEN2PFC_WEEKDAY_SUNDAY
)