"""
Hysen Controller for 2 Pipe Fan Coil Interface
Hysen HY03AC-x-Wifi device and derivative
"""

from .hysendevice import HysenDevice as hysen
from datetime import datetime

HYSEN2PFC_KEY_LOCK_OFF          = 0
HYSEN2PFC_KEY_LOCK_ON           = 1

HYSEN2PFC_KEY_ALL_UNLOCKED      = 0
HYSEN2PFC_KEY_POWER_UNLOCKED    = 1
HYSEN2PFC_KEY_ALL_LOCKED        = 2

HYSEN2PFC_POWER_OFF             = 0
HYSEN2PFC_POWER_ON              = 1

HYSEN2PFC_VALVE_OFF             = 0
HYSEN2PFC_VALVE_ON              = 1

HYSEN2PFC_HYSTERESIS_HALVE      = 0
HYSEN2PFC_HYSTERESIS_WHOLE      = 1

HYSEN2PFC_CALIBRATION_MIN       = -5.0
HYSEN2PFC_CALIBRATION_MAX       = 5.0

HYSEN2PFC_FAN_LOW               = 1
HYSEN2PFC_FAN_MEDIUM            = 2
HYSEN2PFC_FAN_HIGH              = 3
HYSEN2PFC_FAN_AUTO              = 4

HYSEN2PFC_MODE_FAN              = 1
HYSEN2PFC_MODE_COOL             = 2
HYSEN2PFC_MODE_HEAT             = 3

HYSEN2PFC_FAN_CONTROL_ON        = 0
HYSEN2PFC_FAN_CONTROL_OFF       = 1

HYSEN2PFC_FROST_PROTECTION_OFF  = 0
HYSEN2PFC_FROST_PROTECTION_ON   = 1

HYSEN2PFC_SCHEDULE_TODAY        = 0
HYSEN2PFC_SCHEDULE_12345        = 1
HYSEN2PFC_SCHEDULE_123456       = 2
HYSEN2PFC_SCHEDULE_1234567      = 3

HYSEN2PFC_PERIOD_DISABLED       = 0
HYSEN2PFC_PERIOD_ENABLED        = 1

HYSEN2PFC_MAX_TEMP              = 40
HYSEN2PFC_MIN_TEMP              = 10
HYSEN2PFC_COOLING_MAX_TEMP      = 40
HYSEN2PFC_COOLING_MIN_TEMP      = 10
HYSEN2PFC_HEATING_MAX_TEMP      = 40
HYSEN2PFC_HEATING_MIN_TEMP      = 10

HYSEN2PFC_WEEKDAY_MONDAY        = 1
HYSEN2PFC_WEEKDAY_SUNDAY        = 7

HYSEN2PFC_DEFAULT_TARGET_TEMP   = 22
HYSEN2PFC_DEFAULT_CALIBRATION   = 0.0

HYSEN2PFC_DEV_TYPE              = 0x4F5B

class Hysen2PipeFanCoilDevice(hysen):
    
    def __init__ (self, host, mac, timeout, sync_clock, sync_hour):
        hysen.__init__(self, host, mac, HYSEN2PFC_DEV_TYPE, timeout)

#        self.name = "Hysen 2 Pipe Fan Coil Controller"
        self.unique_id = ''.join(format(x, '02x') for x in bytearray(mac)) 
        self._host = host[0]
        self._sync_clock = sync_clock
        self._sync_hour = sync_hour

        self.key_lock = HYSEN2PFC_KEY_LOCK_OFF
        self.key_lock_type = HYSEN2PFC_KEY_ALL_UNLOCKED
        self.valve_state = HYSEN2PFC_VALVE_OFF
        self.power_state = HYSEN2PFC_POWER_ON
        self.operation_mode = HYSEN2PFC_MODE_FAN
        self.fan_mode = HYSEN2PFC_FAN_LOW
        self.room_temp = 0        
        self.target_temp = HYSEN2PFC_DEFAULT_TARGET_TEMP
        self.hysteresis = HYSEN2PFC_HYSTERESIS_WHOLE
        self.calibration = HYSEN2PFC_DEFAULT_CALIBRATION
        self.cooling_max_temp = HYSEN2PFC_COOLING_MAX_TEMP
        self.cooling_min_temp = HYSEN2PFC_COOLING_MIN_TEMP
        self.heating_max_temp = HYSEN2PFC_HEATING_MAX_TEMP
        self.heating_min_temp = HYSEN2PFC_HEATING_MIN_TEMP
        self.fan_control = HYSEN2PFC_FAN_CONTROL_ON
        self.frost_protection = HYSEN2PFC_FROST_PROTECTION_ON
        self.clock_hour = datetime.now().hour
        self.clock_minute = datetime.now().minute
        self.clock_second = datetime.now().second
        self.clock_weekday = datetime.now().isoweekday()
        self.unknown = 0
        self.schedule = HYSEN2PFC_SCHEDULE_TODAY
        self.period1_start_enabled = HYSEN2PFC_PERIOD_DISABLED
        self.period1_start_hour = 8
        self.period1_start_min = 0
        self.period1_end_enabled = HYSEN2PFC_PERIOD_DISABLED
        self.period1_end_hour = 11
        self.period1_end_min = 30
        self.period2_start_enabled = HYSEN2PFC_PERIOD_DISABLED
        self.period2_start_hour = 12
        self.period2_start_min = 30
        self.period2_end_enabled = HYSEN2PFC_PERIOD_DISABLED
        self.period2_end_hour = 17
        self.period2_end_min = 30
        self.time_valve_on = 0
        self.fwversion = 0
        self._authenticated = False
        self._is_sync_clock_done = False

    # set lock and power
    # 0x01, 0x06, 0x00, 0x00, 0xrk, 0x0p
    # r = Key lock, 0 = Off, 1 = On
    # k = Key lock type (Loc), 0 = Unlocked, 1 = All buttons locked except Power, 2 = All buttons locked
    # p = Power State, 0 = Power off, 1 = Power on
    # If key lock is Off then key lock type has to be unlocked otherwise after any subsequent command we will get remote lock on
    def set_lock_power(self, key_lock, key_lock_type, power_state):
        _request = bytearray([0x01, 0x06, 0x00, 0x00])
        _request.append((key_lock << 4) + key_lock_type)
        _request.append(power_state)
        self._send_request(_request)

    def set_key_lock(self, key_lock_type):
        if key_lock_type not in [
            HYSEN2PFC_KEY_ALL_UNLOCKED,
            HYSEN2PFC_KEY_POWER_UNLOCKED,
            HYSEN2PFC_KEY_ALL_LOCKED]:
            raise ValueError(
                'Can\'t set key lock type (%s) outside device\'s admitted values (%s), (%s), (%s).' % ( \
                key_lock_type,
                HYSEN2PFC_KEY_ALL_UNLOCKED,
                HYSEN2PFC_KEY_POWER_UNLOCKED,
                HYSEN2PFC_KEY_ALL_LOCKED))
        self.get_device_status()
        if key_lock_type == HYSEN2PFC_KEY_ALL_UNLOCKED:
            self.key_lock = HYSEN2PFC_KEY_LOCK_OFF;
        else:
            self.key_lock = HYSEN2PFC_KEY_LOCK_ON;
        self.set_lock_power(
            self.key_lock,
            key_lock_type,
            self.power_state)

    def set_power(self, power):
        if power not in [
            HYSEN2PFC_POWER_OFF,
            HYSEN2PFC_POWER_ON]:
            raise ValueError(
                'Can\'t set power (%s) outside device\'s admitted values (%s), (%s).' % ( \
                power,
                HYSEN2PFC_POWER_OFF,
                HYSEN2PFC_POWER_ON))
        self.get_device_status()
        self.set_lock_power(
            self.key_lock,
            self.key_lock_type,
            power)

    # set mode and fan
    # 0x01, 0x06, 0x00, 0x01, Mod, Fs
    # Mod = Operation mode, 0x01 = Ventilation, 0x02 = Cooling, 0x03 = Heating
    # Fs = Fan speed, 0x01 = Low, 0x02 = Medium, 0x03 = High, 0x04 = Auto
    # Note: Ventilation and fan auto are mutual exclusive (e.g. Mod = 0x01 and Fs = 0x04 is not allowed)
    #       The calling method should deal with that 
    def set_mode_fan(self, operation_mode, fan_mode):
        _request = bytearray([0x01, 0x06, 0x00, 0x01])
        _request.append(operation_mode)
        _request.append(fan_mode)
        self._send_request(_request)

    def set_fan_mode(self, fan_mode):
        if fan_mode not in [
            HYSEN2PFC_FAN_LOW,
            HYSEN2PFC_FAN_MEDIUM,
            HYSEN2PFC_FAN_HIGH,
            HYSEN2PFC_FAN_AUTO]:
            raise ValueError(
                'Can\'t set fan_mode (%s) outside device\'s admitted values (%s), (%s), (%s), (%s).' % ( \
                fan_mode,
                HYSEN2PFC_FAN_LOW,
                HYSEN2PFC_FAN_MEDIUM,
                HYSEN2PFC_FAN_HIGH,
                HYSEN2PFC_FAN_AUTO))
        self.get_device_status()
        if (fan_mode == HYSEN2PFC_FAN_AUTO) and \
           (self.operation_mode == HYSEN2PFC_MODE_FAN):
            raise ValueError(
                'Can\'t have fan_mode \'auto\' and operation_mode \'fan_only\'.')
        self.set_mode_fan(
            self.operation_mode,
            fan_mode)
    
    def set_operation_mode(self, operation_mode):
        if operation_mode not in [
            HYSEN2PFC_MODE_FAN,
            HYSEN2PFC_MODE_COOL,
            HYSEN2PFC_MODE_HEAT]:
            raise ValueError(
                'Can\'t set operation_mode (%s) outside device\'s admitted values (%s), (%s), (%s).' % ( \
                operation_mode,
                HYSEN2PFC_MODE_FAN,
                HYSEN2PFC_MODE_COOL,
                HYSEN2PFC_MODE_HEAT))
        self.get_device_status()
        if (operation_mode == HYSEN2PFC_MODE_FAN) and \
           (self.fan_mode == HYSEN2PFC_FAN_AUTO):
            raise ValueError(
                'Can\'t have operation_mode \'fan_only\' and fan_mode \'auto\'.')
        self.set_mode_fan(
            operation_mode,
            self.fan_mode)
 
    # set target temperature
    # 0x01,0x06,0x00,0x02,0x00, Tt
    # Tt = Target temperature in degrees Celsius
    # confirmation response:
    # response 0x01,0x06,0x00,0x02,0x00,Tt
    # Note: The calling method should not do anything if in ventilation mode
    #       Check temp against Sh1, Sl1 for cooling and against Sh2, Sl2 for heating
    def set_target_temp(self, temp):
        self.get_device_status()
        if self.operation_mode == HYSEN2PFC_MODE_FAN:
            raise ValueError(
                'Can\'t set a target temperature when operation_mode is \'fan_only\'.') 
        elif self.operation_mode == HYSEN2PFC_MODE_HEAT:
            if (temp > self.heating_max_temp):
                raise ValueError(
                    'Can\'t set a heating target temperature (%s°) higher than maximum set (%s°).' % ( \
                    temp,
                    self.heating_max_temp))
            if temp < self.heating_min_temp:
                raise ValueError(
                    'Can\'t set a heating target temperature (%s°) lower than minimum set (%s°).' % ( \
                    temp,
                    self.heating_min_temp))
        else:
            if temp > self.cooling_max_temp:
                raise ValueError(
                    'Can\'t set a cooling target temperature (%s°) higher than maximum set (%s°).' % ( \
                    temp,
                    self.cooling_max_temp))
            if temp < self.cooling_min_temp:
                raise ValueError(
                    'Can\'t set a cooling target temperature (%s°) lower than minimum set (%s°).' % ( \
                    temp,
                    self.cooling_min_temp))
        _request = bytearray([0x01, 0x06, 0x00, 0x02])
        _request.append(0)
        _request.append(temp)
        self._send_request(_request)

    # set options
    # 0x01, 0x10, 0x00, 0x03, 0x00, 0x04, 0x08, Dif, Adj, Sh1, Sl1, Sh2, Sl2, Fan, Fre
    # Dif = Hysteresis, 0x00 = 0.5 degree Celsius, 0x01 = 1 degree Celsius
    # Adj = Temperature calibration -5~+5, 0.1 degree Celsius step 
    #       (e.g. -1 = 0xF6, -1.4 = 0xF2, 0 = 0x00, +1 = 0x0A, +1.2 = 0x0C, +2 = 0x14, etc.)
    # Sh1 = Cooling max. temperature
    # Sl1 = Cooling min. temperature
    # Sh2 = Heating max. temperature
    # Sl2 = Heating min. temperature
    # Fan = Fan coil control mode, 0x00 = Fan coil in control, 0x01 = Fan coil out of control
    # Fre = Frost Protection, 0x00 = On, 0x01 = Off
    # confirmation response:
    # payload 0x01,0x10,0x00,0x03,0x00,0x04
    def set_options(self, hysteresis, calibration, cooling_max_temp, cooling_min_temp, heating_max_temp, heating_min_temp, fan_control, frost_protection):
        # Truncate the fractional part to 1 digit 
        calibration = int(calibration * 10 // 1)
        # Convert to signed byte
        calibration = (0x100 + calibration) & 0xFF
        _request = bytearray([0x01, 0x10, 0x00, 0x03, 0x00, 0x04, 0x08])
        _request.append(hysteresis)
        _request.append(calibration)
        _request.append(cooling_max_temp)
        _request.append(cooling_min_temp)
        _request.append(heating_max_temp)
        _request.append(heating_min_temp)
        _request.append(fan_control)
        _request.append(frost_protection)
        self._send_request(_request)

    def set_hysteresis(self, hysteresis):
        if hysteresis not in [
            HYSEN2PFC_HYSTERESIS_HALVE,
            HYSEN2PFC_HYSTERESIS_WHOLE]:
            raise ValueError(
                'Can\'t set hysteresis (%s) outside device\'s admitted values (%s), (%s).' % ( \
                hysteresis,
                HYSEN2PFC_HYSTERESIS_HALVE,
                HYSEN2PFC_HYSTERESIS_WHOLE))
        self.get_device_status()
        self.set_options(
            hysteresis,
            self.calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_calibration(self, calibration):
        if calibration < HYSEN2PFC_CALIBRATION_MIN:
            raise ValueError(
                'Can\'t set calibration (%s°) lower than device\'s minimum (%s°).' % ( \
                calibration,
                HYSEN2PFC_CALIBRATION_MIN))
        if calibration > HYSEN2PFC_CALIBRATION_MAX:
            raise ValueError(
                'Can\'t set calibration (%s°) higher than device\'s maximum (%s°).' % ( \
                calibration,
                HYSEN2PFC_CALIBRATION_MAX))
        self.get_device_status()
        self.set_options(
            self.hysteresis,
            calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_cooling_max_temp(self, cooling_max_temp):
        self.get_device_status()
        if cooling_max_temp > HYSEN2PFC_COOLING_MAX_TEMP:
            raise ValueError(
                'Can\'t set cooling maximum temperature (%s°) higher than device\'s maximum (%s°).' % ( \
                cooling_max_temp,
                HYSEN2PFC_COOLING_MAX_TEMP))
        if cooling_max_temp < self.cooling_min_temp:
            raise ValueError(
                'Can\'t set cooling maximum temperature (%s°) lower than minimum set (%s°).' % ( \
                cooling_max_temp,
                self.cooling_min_temp))
        if cooling_max_temp < self.target_temp:
            raise ValueError(
                'Can\'t set cooling maximum temperature (%s°) lower than target temperature (%s°).' % ( \
                cooling_max_temp,
                self.target_temp))
        self.set_options(
            self.hysteresis,
            self.calibration,
            cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_cooling_min_temp(self, cooling_min_temp):
        self.get_device_status()
        if cooling_min_temp < HYSEN2PFC_COOLING_MIN_TEMP:
            raise ValueError(
                'Can\'t set cooling minimum temperature (%s°) lower than device\'s minimum (%s°).' % ( \
                cooling_min_temp,
                HYSEN2PFC_COOLING_MIN_TEMP))
        if cooling_min_temp > self.cooling_max_temp:
            raise ValueError(
                'Can\'t set cooling minimum temperature (%s°) higher than maximum set (%s°).' % ( \
                cooling_min_temp,
                self.cooling_max_temp))
        if cooling_min_temp > self.target_temp:
            raise ValueError(
                'Can\'t set cooling minimum temperature (%s°) higher than target temperature (%s°).' % ( \
                cooling_min_temp,
                self.target_temp))
        self.set_options(
            self.hysteresis,
            self.calibration,
            self.cooling_max_temp,
            cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_heating_max_temp(self, heating_max_temp):
        self.get_device_status()
        if heating_max_temp > HYSEN2PFC_HEATING_MAX_TEMP:
            raise ValueError(
                'Can\'t set heating maximum temperature (%s°) higher than device\'s maximum (%s°).' % ( \
                 heating_max_temp,
                HYSEN2PFC_HEATING_MAX_TEMP))
        if  heating_max_temp < self. heating_min_temp:
            raise ValueError(
                'Can\'t set heating maximum temperature (%s°) lower than minimum set (%s°).' % ( \
                 heating_max_temp,
                self. heating_min_temp))
        if  heating_max_temp < self.target_temp:
            raise ValueError(
                'Can\'t set heating maximum temperature (%s°) lower than target temperature (%s°).' % ( \
                 heating_max_temp,
                self.target_temp))
        self.set_options(
            self.hysteresis,
            self.calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_heating_min_temp(self, heating_min_temp):
        self.get_device_status()
        if heating_min_temp < HYSEN2PFC_HEATING_MIN_TEMP:
            raise ValueError(
                'Can\'t set heating minimum temperature (%s°) lower than device\'s minimum (%s°).' % ( \
                heating_min_temp,
                HYSEN2PFC_HEATING_MIN_TEMP))
        if heating_min_temp > self.heating_max_temp:
            raise ValueError(
                'Can\'t set heating minimum temperature (%s°) higher than maximum set (%s°).' % ( \
                heating_min_temp,
                self.heating_max_temp))
        if heating_min_temp > self.target_temp:
            raise ValueError(
                'Can\'t set heating minimum temperature (%s°) higher than target temperature (%s°).' % ( \
                heating_min_temp,
                self.target_temp))
        self.set_options(
            self.hysteresis,
            self.calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            heating_min_temp,
            self.fan_control,
            self.frost_protection)

    def set_fan_control(self, fan_control):
        if fan_control not in [
            HYSEN2PFC_FAN_CONTROL_ON,
            HYSEN2PFC_FAN_CONTROL_OFF]:
            raise ValueError(
                'Can\'t set fan control (%s) outside device\'s admitted values (%s), (%s).' % ( \
                fan_control,
                HYSEN2PFC_FAN_CONTROL_ON,
                HYSEN2PFC_FAN_CONTROL_OFF))
        self.get_device_status()
        self.set_options(
            self.hysteresis,
            self.calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            fan_control,
            self.frost_protection)

    def set_frost_protection(self, frost_protection):
        if frost_protection not in [
            HYSEN2PFC_FROST_PROTECTION_OFF,
            HYSEN2PFC_FROST_PROTECTION_ON]:
            raise ValueError(
                'Can\'t set frost protection (%s) outside device\'s admitted values (%s), (%s).' % ( \
                frost_protection,
                HYSEN2PFC_FROST_PROTECTION_OFF,
                HYSEN2PFC_FROST_PROTECTION_ON))
        self.get_device_status()
        self.set_options(
            self.hysteresis,
            self.calibration,
            self.cooling_max_temp,
            self.cooling_min_temp,
            self.heating_max_temp,
            self.heating_min_temp,
            self.fan_control,
            frost_protection)

    # set time
    # 0x01, 0x10, 0x00, 0x07, 0x00, 0x02, 0x04, hh, mm, ss, wd
    # hh = Time hour past midnight
    # mm = Time minute past hour
    # ss = Time second past minute
    # wd = Weekday 0x01 = Monday, 0x02 = Tuesday, ..., 0x06 = Saturday, 0x07 = Sunday
    # confirmation response:
    # payload 0x01, 0x10, 0x00, 0x07, 0x00, 0x02
    def set_time(self, clock_hour, clock_minute, clock_second, clock_weekday):
        if clock_hour is None:
            clock_hour = self.clock_hour
        if clock_minute is None:
            clock_minute = self.clock_minute
        if clock_second is None:
            clock_second = self.clock_second
        if clock_weekday is None:
            clock_weekday = self.clock_weekday
        if (clock_hour < 0) or (clock_hour > 23):
            raise ValueError(
                'Hour (%s) has to be between 0 and 23.' % ( \
                clock_hour))
        if (clock_minute < 0) or (clock_minute > 59):
            raise ValueError(
                'Minute (%s) has to be between 0 and 59.' % ( \
                clock_minute))
        if (clock_second < 0) or (clock_second > 59):
            raise ValueError(
                'Second (%s) has to be between 0 and 59.' % ( \
                clock_second))
        if (clock_weekday < HYSEN2PFC_WEEKDAY_MONDAY) or (clock_weekday > HYSEN2PFC_WEEKDAY_SUNDAY):
            raise ValueError(
                'Weekday (%s) has to be between 1 (Monday) and 7 (Saturday).' % ( \
                clock_weekday))
        _request = bytearray([0x01, 0x10, 0x00, 0x07, 0x00, 0x02, 0x04])
        _request.append(clock_hour)
        _request.append(clock_minute)
        _request.append(clock_second)
        _request.append(clock_weekday)
        self._send_request(_request)

    # set weekly schedule
    # 0x01, 0x10, 0x00, 0x09, 0x00, 0x01, 0x02, 0x00, Lm
    # Unknown = 0x00
    # Lm = Weekly schedule, 0x00 = Today, 0x01 = 12345, 0x02 = 123456, 0x03 = 1234567
    # confirmation response:
    # payload 0x01, 0x10, 0x00, 0x09, 0x00, 0x01
    def set_weekly_schedule(self, schedule):
        if schedule not in [
            HYSEN2PFC_SCHEDULE_TODAY,
            HYSEN2PFC_SCHEDULE_12345,
            HYSEN2PFC_SCHEDULE_123456,
            HYSEN2PFC_SCHEDULE_1234567]:
            raise ValueError(
                'Can\'t set schedule (%s) outside device\'s admitted values (%s), (%s), (%s), (%s).' % ( \
                schedule,
                HYSEN2PFC_SCHEDULE_TODAY,
                HYSEN2PFC_SCHEDULE_12345,
                HYSEN2PFC_SCHEDULE_123456,
                HYSEN2PFC_SCHEDULE_1234567))
        _request = bytearray([0x01, 0x10, 0x00, 0x09, 0x00, 0x01, 0x02])
        _request.append(0)
        _request.append(schedule)
        self._send_request(_request)

    # set daily schedule
    # 0x01, 0x10, 0x00, 0x0A, 0x00, 0x04, 0x08, P1OnH, P1OnM, P1OffH, P1OffM, P2OnH, P2OnM, P2OffH, P2OffM
    # P1OnH = Period1 Start Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P1OnM = Period1 Start Minute past hour
    # P1OffH = Period1 End Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P1OffM = Period1 End Minute past hour
    # P2OnH = Period2 Start Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P2OnM = Period2 Start Minute past hour
    # P2OffH = Period2 End Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P2OffM = Period2 End Minute past hour
    # confirmation response:
    # payload 0x01, 0x10, 0x00, 0x0A, 0x00, 0x04
    def set_daily_schedule(self, period1_start_enabled, period1_start_hour, period1_start_min, period1_end_enabled, period1_end_hour, period1_end_min, period2_start_enabled, period2_start_hour, period2_start_min, period2_end_enabled, period2_end_hour, period2_end_min):
        self.get_device_status()
        # Check start period 1 
        if period1_start_enabled is None:
            period1_start_enabled = self.period1_start_enabled
        if period1_start_hour is None:
            period1_start_hour = self.period1_start_hour
        if period1_start_min is None:
            period1_start_min = self.period1_start_min
        if period1_start_enabled not in [
            HYSEN2PFC_PERIOD_DISABLED,
            HYSEN2PFC_PERIOD_ENABLED]:
            raise ValueError(
                'Can\'t set period1_start_enabled (%s) outside device\'s admitted values (%s), (%s).' % ( \
                period1_start_enabled,
                HYSEN2PFC_PERIOD_DISABLED,
                HYSEN2PFC_PERIOD_ENABLED))
        if (period1_start_hour < 0) or (period1_start_hour > 23):
            raise ValueError(
                'period1_start_hour (%s) has to be between 0 and 23.' % ( \
                period1_start_hour))
        if (period1_start_min < 0) or (period1_start_min > 59):
            raise ValueError(
                'period1_start_min (%s) has to be between 0 and 59.' % ( \
                period1_start_min))
        # Check end period 1 
        if period1_end_enabled is None:
            period1_end_enabled = self.period1_end_enabled
        if period1_end_hour is None:
            period1_end_hour = self.period1_end_hour
        if period1_end_min is None:
            period1_end_min = self.period1_end_min
        if period1_end_enabled not in [
            HYSEN2PFC_PERIOD_DISABLED,
            HYSEN2PFC_PERIOD_ENABLED]:
            raise ValueError(
                'Can\'t set period1_end_enabled (%s) outside device\'s admitted values (%s), (%s).' % ( \
                period1_end_enabled,
                HYSEN2PFC_PERIOD_DISABLED,
                HYSEN2PFC_PERIOD_ENABLED))
        if (period1_end_hour < 0) or (period1_end_hour > 23):
            raise ValueError(
                'period1_end_hour (%s) has to be between 0 and 23.' % ( \
                period1_end_hour))
        if (period1_end_min < 0) or (period1_end_min > 59):
            raise ValueError(
                'period1_end_min (%s) has to be between 0 and 59.' % ( \
                period1_end_min))
        # Check start period 2 
        if period2_start_enabled is None:
            period2_start_enabled = self.period2_start_enabled
        if period2_start_hour is None:
            period2_start_hour = self.period2_start_hour
        if period2_start_min is None:
            period2_start_min = self.period2_start_min
        if period2_start_enabled not in [
            HYSEN2PFC_PERIOD_DISABLED,
            HYSEN2PFC_PERIOD_ENABLED]:
            raise ValueError(
                'Can\'t set period2_start_enabled (%s) outside device\'s admitted values (%s), (%s).' % ( \
                period2_start_enabled,
                HYSEN2PFC_PERIOD_DISABLED,
                HYSEN2PFC_PERIOD_ENABLED))
        if (period2_start_hour < 0) or (period2_start_hour > 23):
            raise ValueError(
                'period2_start_hour (%s) has to be between 0 and 23.' % ( \
                period2_start_hour))
        if (period2_start_min < 0) or (period2_start_min > 59):
            raise ValueError(
                'period2_start_min (%s) has to be between 0 and 59.' % ( \
                period2_start_min))
        # Check end period 2 
        if period2_end_enabled is None:
            period2_end_enabled = self.period2_end_enabled
        if period2_end_hour is None:
            period2_end_hour = self.period2_end_hour
        if period2_end_min is None:
            period2_end_min = self.period2_end_min
        if period2_end_enabled not in [
            HYSEN2PFC_PERIOD_DISABLED,
            HYSEN2PFC_PERIOD_ENABLED]:
            raise ValueError(
                'Can\'t set period2_end_enabled (%s) outside device\'s admitted values (%s), (%s).' % ( \
                period2_end_enabled,
                HYSEN2PFC_PERIOD_DISABLED,
                HYSEN2PFC_PERIOD_ENABLED))
        if (period2_end_hour < 0) or (period2_end_hour > 23):
            raise ValueError(
                'period2_end_hour (%s) has to be between 0 and 23.' % ( \
                period2_end_hour))
        if (period2_end_min < 0) or (period2_end_min > 59):
            raise ValueError(
                'period2_end_min (%s) has to be between 0 and 59.' % ( \
                period2_end_min))
        #Check if start period 1 precedes end period 1
        if (period1_start_hour > period1_end_hour) or \
            ((period1_start_hour == period1_end_hour) and (period1_start_min >= period1_end_min)):
            raise ValueError(
                'period1 start (%s:%s) has to be before period1 end (%s:%s).' % ( \
                period1_start_hour,
                period1_start_min,
                period1_end_hour,
                period1_end_min))
        #Check if end period 1 precedes start period 2
        if (period1_end_hour > period2_start_hour) or \
            ((period1_end_hour == period2_start_hour) and (period1_end_min >= period2_start_min)):
            raise ValueError(
                'period1 end (%s:%s) has to be before period2 start (%s:%s).' % ( \
                period1_end_hour,
                period1_end_min,
                period2_start_hour,
                period2_start_min))
        #Check if start period 2 precedes end period 2
        if (period2_start_hour > period2_end_hour) or \
            ((period2_start_hour == self.period2_end_hour) and (period2_start_min >= period2_end_min)):
            raise ValueError(
                'period2 start (%s:%s) has to be before period2 end (%s:%s).' % ( \
                period2_start_hour,
                period2_start_min,
                period2_end_hour,
                period2_end_min))

        _request = bytearray([0x01, 0x10, 0x00, 0x0A, 0x00, 0x04, 0x08])
        _request.append((period1_start_enabled << 7) + period1_start_hour)
        _request.append(period1_start_min)
        _request.append((period1_end_enabled << 7) + period1_end_hour)
        _request.append(period1_end_min)
        _request.append((period2_start_enabled << 7) + period2_start_hour)
        _request.append(period2_start_min)
        _request.append((period2_end_enabled << 7) + period2_end_hour)
        _request.append(period2_end_min)
        self._send_request(_request)

    # get device status
    # 0x01, 0x03, 0x00, 0x00, 0x00, 0x10
    # response:
    # 0x01, 0x03, 0x20, 0xrk, 0xvp, Mod, Fs, Rt, Tt, Dif, Adj, Sh1, Sl1, Sh2, Sl2, Fan, Fre, hh, mm, ss, wd, Unk, Lm, P1OnH, P1OnMin, P1OffH, P1OffM, P2OnH, P2OnMin, P2OffH, P2OffM, Tv1, Tv2, Tv3, Tv4
    # r = Remote lock, 0 = Off, 1 = On
    # k = Key lock (Loc), 0 = Unlocked, 1 = All buttons locked except Power, 2 = All buttons locked
    # v = Valve, 0 = Valve off, 1 = Valve on
    # p = Power, 0 = Power off, 1 = Power on
    # Mod = Operation mode, 0x01 = Ventilation, 0x02 = Cooling, 0x03 = Heating
    # Fs = Fan speed, 0x01 = Low, 0x02 = Medium, 0x03 = High, 0x04 = Auto
    # Rt = Room temperature
    # Tt = Target temperature
    # Dif = Hysteresis, 0x00 = 0.5 degree Celsius, 0x01 = 1 degree Celsius
    # Adj = Temperature calibration -5~+5, 0.1 degree Celsius step
    #       (e.g. -1 = 0xF6, -1.4 = 0xF2, 0 = 0x00, +1 = 0x0A, +1.2 = 0x0C, +2 = 0x14)
    # Sh1 = Cooling max. temperature
    # Sl1 = Cooling min. temperature
    # Sh2 = Heating max. temperature
    # Sl2 = Heating min. temperature
    # Fan = Fan coil control mode, 0x00 = Fan coil in control, 0x01 = Fan coil out of control
    # Fre = Frost Protection, 0 = On, 1 = Off
    # hh = Time hour past midnight
    # mm = Time minute past hour
    # ss = Time second past minute
    # wd = Weekday 0x01 = Monday, 0x01 = Tuesday, ..., 0x06 = Saturday, 0x07 = Sunday
    # Unk = Unknown, 0x00
    # Lm = Weekly schedule, 0x00 = Today, 0x01 = 12345, 0x02 = 123456, 0x03 = 1234567
    # P1OnH = Period1 Start Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P1OnM = Period1 Start Minute past hour
    # P1OffH = Period1 End Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P1OffM = Period1 End Minute past hour
    # P2OnH = Period2 Start Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P2OnM = Period2 Start Minute past hour
    # P2OffH = Period2 End Hour, Note: The most significant bit, 0 = Disabled, 1 = Enabled
    # P2OffM = Period2 End Minute past hour
    # Tv1 = Total time valve on in seconds MSByte
    # Tv3 = Total time valve on in seconds
    # Tv3 = Total time valve on in seconds
    # Tv4 = Total time valve on in seconds LSByte
    def get_device_status(self):
        if not self._authenticated:
            self._authenticated = self.auth()
        if self._authenticated:        
            if (self._sync_clock):
                _dt = datetime.now()
                if self._is_sync_clock_done:
                    self._is_sync_clock_done = _dt.hour == self._sync_hour
                else:
                    if _dt.hour == self._sync_hour:
                        self.set_time(
                            _dt.hour,
                            _dt.minute,
                            _dt.second,
                            _dt.isoweekday())
                        self._is_sync_clock_done = True
            _request = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x10])
            _response = self._send_request(_request)
            self.key_lock = (_response[3]>>4) & 1
            self.key_lock_type = _response[3] & 3
            self.valve_state = (_response[4]>>4) & 1
            self.power_state = _response[4] & 1
            self.operation_mode = _response[5]
            self.fan_mode = _response[6]
            self.room_temp = _response[7]
            self.target_temp = _response[8]
            self.hysteresis = _response[9]
            self.calibration = _response[10]
            if self.calibration > 0x7F:
                self.calibration = self.calibration - 0x100
            self.calibration = float(self.calibration / 10.0)
            self.cooling_max_temp = _response[11]
            self.cooling_min_temp = _response[12]
            self.heating_max_temp = _response[13]
            self.heating_min_temp = _response[14]
            self.fan_control = _response[15]
            self.frost_protection = _response[16]
            self.clock_hour = _response[17]
            self.clock_minute = _response[18]
            self.clock_second = _response[19]
            self.clock_weekday = _response[20]
            self.unknown = _response[21]
            self.schedule = _response[22]
            self.period1_start_enabled = (_response[23]>>7) & 1
            self.period1_start_hour = _response[23] & 0x1F
            self.period1_start_min = _response[24] & 0x3F
            self.period1_end_enabled = (_response[25]>>7) & 1
            self.period1_end_hour = _response[25] & 0x1F
            self.period1_end_min = _response[26] & 0x3F
            self.period2_start_enabled = (_response[27]>>7) & 1
            self.period2_start_hour = _response[27] & 0x1F
            self.period2_start_min = _response[28] & 0x3F
            self.period2_end_enabled = (_response[29]>>7) & 1
            self.period2_end_hour = _response[29] & 0x1F
            self.period2_end_min = _response[30] & 0x3F
            self.time_valve_on = (_response[31] << 24) + (_response[32] << 16) + (_response[33] << 8) + _response[34]
            self.fwversion = self.get_fwversion()
            
