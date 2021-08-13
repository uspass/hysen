"""
Hysen Heating Thermostat Controller Interface
Hysen HY03-x-Wifi device and derivative
"""

from .hysendevice import HysenDevice as hysen
from datetime import datetime

HYSENHEAT_KEY_LOCK_OFF         = 0
HYSENHEAT_KEY_LOCK_ON          = 1

HYSENHEAT_POWER_OFF            = 0
HYSENHEAT_POWER_ON             = 1

HYSENHEAT_VALVE_OFF            = 0
HYSENHEAT_VALVE_ON             = 1

HYSENHEAT_MANUAL_IN_AUTO_OFF   = 0
HYSENHEAT_MANUAL_IN_AUTO_ON    = 1

HYSENHEAT_MODE_MANUAL          = 0
HYSENHEAT_MODE_AUTO            = 1

HYSENHEAT_SCHEDULE_12345_67    = 1
HYSENHEAT_SCHEDULE_123456_7    = 2
HYSENHEAT_SCHEDULE_1234567     = 3

HYSENHEAT_SENSOR_INTERNAL      = 0
HYSENHEAT_SENSOR_EXTERNAL      = 1
HYSENHEAT_SENSOR_INT_EXT       = 2

HYSENHEAT_HYSTERESIS_MIN       = 1
HYSENHEAT_HYSTERESIS_MAX       = 9

HYSENHEAT_CALIBRATION_MIN      = -5.0
HYSENHEAT_CALIBRATION_MAX      = 5.0

HYSENHEAT_FROST_PROTECTION_OFF = 0
HYSENHEAT_FROST_PROTECTION_ON  = 1

HYSENHEAT_POWERON_OFF          = 0
HYSENHEAT_POWERON_ON           = 1

HYSENHEAT_MAX_TEMP             = 99
HYSENHEAT_MIN_TEMP             = 5

HYSENHEAT_WEEKDAY_MONDAY       = 1
HYSENHEAT_WEEKDAY_SUNDAY       = 7


HYSENHEAT_DEFAULT_TARGET_TEMP        = 22
HYSENHEAT_DEFAULT_CALIBRATION        = 0.0
HYSENHEAT_DEFAULT_MAX_TEMP           = 35
HYSENHEAT_DEFAULT_MIN_TEMP           = 5
HYSENHEAT_DEFAULT_EXTERNAL_MAX_TEMP  = 42
HYSENHEAT_DEFAULT_HYSTERESIS         = 2


HYSENHEAT_DEV_TYPE             = 0x4EAD

class HysenHeatingDevice(hysen):
    
    def __init__ (self, host, mac, timeout, sync_clock, sync_hour):
        hysen.__init__(self, host, mac, HYSENHEAT_DEV_TYPE, timeout)

#        self.name = "Hysen Heating Thermostat Controller"
        self.unique_id = ''.join(format(x, '02x') for x in bytearray(mac)) 
        self._host = host[0]
        self._sync_clock = sync_clock
        self._sync_hour = sync_hour
        
        self.key_lock = HYSENHEAT_KEY_LOCK_OFF
        self.valve_state = HYSENHEAT_VALVE_OFF
        self.power_state = HYSENHEAT_POWER_ON
        self.manual_in_auto  = HYSENHEAT_MANUAL_IN_AUTO_OFF
        self.room_temp = 0        
        self.target_temp = HYSENHEAT_DEFAULT_TARGET_TEMP
        self.operation_mode = HYSENHEAT_MODE_MANUAL
        self.schedule = HYSENHEAT_SCHEDULE_1234567
        self.sensor = HYSENHEAT_SENSOR_INTERNAL
        self.external_max_temp = HYSENHEAT_DEFAULT_EXTERNAL_MAX_TEMP
        self.hysteresis = HYSENHEAT_DEFAULT_HYSTERESIS
        self.max_temp = HYSENHEAT_DEFAULT_MAX_TEMP
        self.min_temp = HYSENHEAT_DEFAULT_MIN_TEMP
        self.calibration = HYSENHEAT_DEFAULT_CALIBRATION
        self.frost_protection = HYSENHEAT_FROST_PROTECTION_OFF
        self.poweron = HYSENHEAT_POWERON_OFF
        self.unknown1 = 0
        self.external_temp = 0
        self.clock_hour = datetime.now().hour
        self.clock_minute = datetime.now().minute
        self.clock_second = datetime.now().second
        self.clock_weekday = datetime.now().isoweekday()
        self.period1_hour = 0
        self.period1_min = 0
        self.period2_hour = 0
        self.period2_min = 0
        self.period3_hour = 0
        self.period3_min = 0
        self.period4_hour = 0
        self.period4_min = 0
        self.period5_hour = 0
        self.period5_min = 0
        self.period6_hour = 0
        self.period6_min = 0
        self.we_period1_hour = 0
        self.we_period1_min = 0
        self.we_period2_hour = 0
        self.we_period2_min = 0
        self.period1_temp = 0
        self.period2_temp = 0
        self.period3_temp = 0
        self.period4_temp = 0
        self.period5_temp = 0
        self.period6_temp = 0
        self.we_period1_temp = 0
        self.we_period2_temp = 0
        self.unknown2 = 0
        self.unknown3 = 0
        self.fwversion = 0
        self._authenticated = False
        self._is_sync_clock_done = False

    # set lock and power
    # 0x01, 0x06, 0x00, 0x00, 0x0r, 0xap
    # r = Key lock, 0 = Off, 1 = On
    # a = Manual over Auto, 0 = Off, 1 = On
    # p = Power State, 0 = Power off, 1 = Power on
    # confirmation response:
    # response 0x01, 0x06, 0x00, 0x00, 0x0r, 0x0p
    def set_lock_power(self, key_lock, power_state):
        _request = bytearray([0x01, 0x06, 0x00, 0x00])
        _request.append(key_lock)
        _request.append(power_state)
        self._send_request(_request)

    def set_key_lock(self, key_lock):
        if key_lock not in [
            HYSENHEAT_KEY_LOCK_OFF, 
            HYSENHEAT_KEY_LOCK_ON]:
            raise ValueError(
                'Can\'t set remote lock (%s) outside device\'s admitted values (%s), (%s).' % ( \
                key_lock,
                HYSENHEAT_KEY_LOCK_OFF,
                HYSENHEAT_KEY_LOCK_ON))
        self.get_device_status()
        self.set_lock_power(
            key_lock, 
            self.power_state)

    def set_power(self, power_state):
        if power_state not in [
            HYSENHEAT_POWER_OFF, 
            HYSENHEAT_POWER_ON]:
            raise ValueError(
                'Can\'t set power state (%s) outside device\'s admitted values (%s), (%s).' % ( \
                power_state,
                HYSENHEAT_POWER_OFF,
                HYSENHEAT_POWER_ON))
        self.get_device_status()
        self.set_lock_power(
            self.key_lock, 
            power_state | (self.power_state & 0xFE))

    # set target temperature
    # 0x01,0x06,0x00,0x01,0x00, Tt
    # Tt = Target temperature in degrees Celsius * 2
    # confirmation response:
    # response 0x01,0x06,0x00,0x01,0x00,Tt
    # Note: If in automatic mode, setting target temperature changes to manual mode
    def set_target_temp(self, temp):
        self.get_device_status()
        if temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                temp,
                self.max_temp))
        if temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                temp,
                self.min_temp))
        _request = bytearray([0x01, 0x06, 0x00, 0x01])
        _request.append(0)
        _request.append(int(temp * 2))
        self._send_request(_request)

    # set mode, loop and sensor type
    # 0x01, 0x06, 0x00, 0x02, 0xlm, Sen
    # m = Operation mode, 0x00 = Manual, 0x01 = Auto
    # l = Loop mode, Weekly schedule, 0x01 = 12345,67, 0x02 = 123456,7, 0x03 = 1234567
    # Sen = sensor, 0x00 = internal, 0x01 = external, 0x02 = internal control with external target
    # confirmation response:
    # response 0x01, 0x06, 0x00, 0x02, 0xml, Sen
    # Note:  
    def set_mode_loop_sensor(self, operation_mode, schedule, sensor):
        _request = bytearray([0x01, 0x06, 0x00, 0x02])
        _request.append((schedule<<4) + operation_mode)
        _request.append(sensor)
        self._send_request(_request)

    def set_sensor(self, sensor):
        if sensor not in [
            HYSENHEAT_SENSOR_INTERNAL, 
            HYSENHEAT_SENSOR_EXTERNAL, 
            HYSENHEAT_SENSOR_INT_EXT]:
            raise ValueError(
                'Can\'t set sensor (%s) outside device\'s admitted values (%s), (%s), (%s).' % ( \
                sensor,
                HYSENHEAT_SENSOR_INTERNAL,
                HYSENHEAT_SENSOR_EXTERNAL, 
                HYSENHEAT_SENSOR_INT_EXT))
        self.get_device_status()
        self.set_mode_loop_sensor(
            self.operation_mode, 
            self.schedule, 
            sensor)
    
    def set_operation_mode(self, operation_mode):
        if operation_mode not in [
            HYSENHEAT_MODE_MANUAL, 
            HYSENHEAT_MODE_AUTO]:
            raise ValueError(
                'Can\'t set operation_mode (%s) outside device\'s admitted values (%s), (%s).' % ( \
                operation_mode,
                HYSENHEAT_MODE_MANUAL,
                HYSENHEAT_MODE_AUTO))
        self.get_device_status()
        self.set_mode_loop_sensor(
            operation_mode, 
            self.schedule, 
            self.sensor)
 
    def set_weekly_schedule(self, schedule):
        if schedule not in [
            HYSENHEAT_SCHEDULE_12345_67, 
            HYSENHEAT_SCHEDULE_123456_7, 
            HYSENHEAT_SCHEDULE_1234567]:
            raise ValueError(
                'Can\'t set schedule (%s) outside device\'s admitted values (%s), (%s), (%s).' % ( \
                schedule,
                HYSENHEAT_SCHEDULE_12345_67,
                HYSENHEAT_SCHEDULE_123456_7, 
                HYSENHEAT_SCHEDULE_1234567))
        self.get_device_status()
        self.set_mode_loop_sensor(
            self.operation_mode, 
            schedule, 
            self.sensor)
    
    # set options
    # 0x01, 0x10, 0x00, 0x03, 0x00, 0x04, 0x08, Osv, Dif, Svh, Svl, AdjMSB, AdjLSB, Fre, POn
    # Osv = Max. temperature of the external sensor
    # Dif = Hysteresis
    # Svh = Max. temperature internal sensor
    # Svl = Min. temperature internal sensor
    # Adj = Temperature calibration -5~+5, 0.5 degree Celsius step 
    #       (e.g. -1 = 0xFFFE, -1.5 = 0xFFFD, 0 = 0x0000, +1 = 0x0002, +1.5 = 0x0003, +2 = 0x0004, etc.)
    # Fre = Frost Protection, 0x00 = Off, 0x01 = On
    # POn = Power On, 0x00 = When powered, thermostat Off, 0x01 = When powered, thermostat On
    # confirmation response:
    # payload 0x01,0x10,0x00,0x03,0x00,0x08
    def set_options(self, external_max_temp, hysteresis, max_temp, min_temp, calibration, frost_protection, poweron):
        calibration = int(calibration * 2)
        # Convert to signed byte
        calibration = (0x10000 + calibration) & 0xFFFF
        calibration_MSB = (calibration >> 8) & 0xFF
        calibration_LSB = calibration & 0xFF
        _request = bytearray([0x01, 0x10, 0x00, 0x03, 0x00, 0x04, 0x08])
        _request.append(int(external_max_temp))
        _request.append(int(hysteresis))
        _request.append(max_temp)
        _request.append(min_temp)
        _request.append(calibration_MSB)
        _request.append(calibration_LSB)
        _request.append(frost_protection)
        _request.append(poweron)
        self._send_request(_request)

    def set_external_max_temp(self, external_max_temp):
        if external_max_temp < HYSENHEAT_MIN_TEMP:
            raise ValueError(
                'Can\'t set external limit temperature (%s°) lower than device\'s minimum (%s°).' % ( \
                external_max_temp,
                HYSENHEAT_MIN_TEMP))
        if external_max_temp > HYSENHEAT_MAX_TEMP:
            raise ValueError(
                'Can\'t set external limit temperature (%s°) higher than device\'s maximum (%s°).' % ( \
                external_max_temp,
                HYSENHEAT_MAX_TEMP))
        self.get_device_status()
        self.set_options(
            external_max_temp,
            self.hysteresis, 
            self.max_temp,
            self.min_temp, 
            self.calibration, 
            self.frost_protection,
            self.poweron)

    def set_hysteresis(self, hysteresis):
        if hysteresis < HYSENHEAT_HYSTERESIS_MIN:
            raise ValueError(
                'Can\'t set hysteresis (%s°) lower than device\'s minimum (%s°).' % ( \
                hysteresis,
                HYSENHEAT_HYSTERESIS_MIN))
        if hysteresis > HYSENHEAT_HYSTERESIS_MAX:
            raise ValueError(
                'Can\'t set hysteresis (%s°) higher than device\'s maximum (%s°).' % ( \
                hysteresis,
                HYSENHEAT_HYSTERESIS_MAX))
        self.get_device_status()
        self.set_options(
            self.external_max_temp,
            hysteresis, 
            self.max_temp,
            self.min_temp, 
            self.calibration, 
            self.frost_protection,
            self.poweron)

    def set_max_temp(self, temp):
        self.get_device_status()
        if temp > HYSENHEAT_MAX_TEMP:
            raise ValueError(
                'Can\'t set maximum temperature (%s°) higher than device\'s maximum (%s°).' % ( \
                temp,
                HYSENHEAT_MAX_TEMP))
        if temp < self.min_temp:
            raise ValueError(
                'Can\'t set maximum temperature (%s°) lower than minimum set (%s°).' % ( \
                temp,
                self.min_temp))
        if temp < self.target_temp:
            raise ValueError(
                'Can\'t set maximum temperature (%s°) lower than target temperature (%s°).' % ( \
                temp,
                self.target_temp))
        self.set_options(
            self.external_max_temp,
            self.hysteresis, 
            temp,
            self.min_temp, 
            self.calibration, 
            self.frost_protection,
            self.poweron)

    def set_min_temp(self, temp):
        self.get_device_status()
        if temp < HYSENHEAT_MIN_TEMP:
            raise ValueError(
                'Can\'t set minimum temperature (%s°) lower than device\'s minimum (%s°).' % ( \
                temp,
                HYSENHEAT_MIN_TEMP))
        if temp > self.max_temp:
            raise ValueError(
                'Can\'t set minimum temperature (%s°) higher than maximum set (%s°).' % ( \
                temp,
                self.max_temp))
        if temp > self.target_temp:
            raise ValueError(
                'Can\'t set minimum temperature (%s°) higher than target temperature (%s°).' % ( \
                temp,
                self.target_temp))
        self.set_options(
            self.external_max_temp,
            self.hysteresis, 
            self.max_temp,
            temp, 
            self.calibration, 
            self.frost_protection,
            self.poweron)

    def set_calibration(self, calibration):
        if calibration < HYSENHEAT_CALIBRATION_MIN:
            raise ValueError(
                'Can\'t set calibration (%s°) lower than device\'s minimum (%s°).' % ( \
                calibration,
                HYSENHEAT_CALIBRATION_MIN))
        if calibration > HYSENHEAT_CALIBRATION_MAX:
            raise ValueError(
                'Can\'t set calibration (%s°) higher than device\'s maximum (%s°).' % ( \
                calibration,
                HYSENHEAT_CALIBRATION_MAX))
        self.get_device_status()
        self.set_options(
            self.external_max_temp,
            self.hysteresis, 
            self.max_temp,
            self.min_temp, 
            calibration, 
            self.frost_protection,
            self.poweron)

    def set_frost_protection(self, frost_protection):
        if frost_protection not in [
            HYSENHEAT_FROST_PROTECTION_OFF, 
            HYSENHEAT_FROST_PROTECTION_ON]:
            raise ValueError(
                'Can\'t set frost protection (%s) outside device\'s admitted values (%s), (%s).' % ( \
                frost_protection,
                HYSENHEAT_FROST_PROTECTION_OFF,
                HYSENHEAT_FROST_PROTECTION_ON))
        self.get_device_status()
        self.set_options(
            self.external_max_temp,
            self.hysteresis, 
            self.max_temp,
            self.min_temp, 
            self.calibration, 
            frost_protection,
            self.poweron)

    def set_poweron(self, poweron):
        if poweron not in [
            HYSENHEAT_POWERON_OFF, 
            HYSENHEAT_POWERON_ON]:
            raise ValueError(
                'Can\'t set PowerOn (%s) outside device\'s admitted values (%s), (%s).' % ( \
                poweron,
                HYSENHEAT_POWERON_OFF,
                HYSENHEAT_POWERON_ON))
        self.get_device_status()
        self.set_options(
            self.external_max_temp,
            self.hysteresis, 
            self.max_temp,
            self.min_temp, 
            self.calibration, 
            self.frost_protection,
            poweron)

    # set time
    # 0x01,0x10,0x00,0x08,0x00,0x02,0x04, hh, mm, ss, wd
    # hh = Time hour past midnight
    # mm = Time minute past hour
    # ss = Time second past minute
    # wd = Weekday 0x01 = Monday, 0x02 = Tuesday, ..., 0x06 = Saturday, 0x07 = Sunday
    # confirmation response:
    # payload 0x01,0x10,0x00,0x08,0x00,0x02
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
        if (clock_weekday < HYSENHEAT_WEEKDAY_MONDAY) or (clock_weekday > HYSENHEAT_WEEKDAY_SUNDAY):
            raise ValueError(
                'Weekday (%s) has to be between 1 (Monday) and 7 (Saturday).' % ( \
                clock_weekday))
        _request = bytearray([0x01, 0x10, 0x00, 0x08, 0x00, 0x02, 0x04])
        _request.append(clock_hour)
        _request.append(clock_minute)
        _request.append(clock_second)
        _request.append(clock_weekday)
        self._send_request(_request)

    # set daily schedule
    # 0x01, 0x10, 0x00, 0x0A, 0x00, 0x0C, 0x18, P1h, P1m, P1t, P2h, P2m, P2t, P3h, P3m, P3t, 
    # P4h, P4m, P4t, P5h, P5m, P5t, P6h, P6m, P6t, weP1h, weP1m, weP1t, weP2h, weP2m, weP2t
    # P1h = Period1 hour
    # P1m = Period1 minute
    # P1t = Period1 temperature
    # P2h = Period2 hour
    # P2m = Period2 minute
    # P2t = Period2 temperature
    # P3h = Period3 hour
    # P3m = Period3 minute
    # P3t = Period3 temperature
    # P4h = Period4 hour
    # P4m = Period4 minute
    # P4t = Period4 temperature
    # P5h = Period5 hour
    # P5m = Period5 minute
    # P5t = Period5 temperature
    # P6h = Period6 hour
    # P6m = Period6 minute
    # P6t = Period6 temperature
    # weP1h = Period1 hour
    # weP1m = Period1 minute
    # weP1t = Period1 temperature
    # weP2h = Period2 hour
    # weP2m = Period2 minute
    # weP2t = Period2 temperature
    # confirmation response:
    # payload 0x01, 0x10, 0x00, 0x0A, 0x00, 0x0C
    def set_daily_schedule(self, period1_hour, period1_min, period2_hour, period2_min, period3_hour, period3_min, period4_hour, period4_min, period5_hour, period5_min, period6_hour, period6_min, we_period1_hour, we_period1_min, we_period2_hour, we_period2_min, period1_temp, period2_temp, period3_temp, period4_temp, period5_temp, period6_temp, we_period1_temp, we_period2_temp):
        _request = bytearray([0x01, 0x10, 0x00, 0x0A, 0x00, 0x0C, 0x18])
        _request.append(period1_hour)
        _request.append(period1_min)
        _request.append(period2_hour)
        _request.append(period2_min)
        _request.append(period3_hour)
        _request.append(period3_min)
        _request.append(period4_hour)
        _request.append(period4_min)
        _request.append(period5_hour)
        _request.append(period5_min)
        _request.append(period6_hour)
        _request.append(period6_min)
        _request.append(we_period1_hour)
        _request.append(we_period1_min)
        _request.append(we_period2_hour)
        _request.append(we_period2_min)
        _request.append(int(period1_temp * 2))
        _request.append(int(period2_temp * 2))
        _request.append(int(period3_temp * 2))
        _request.append(int(period4_temp * 2))
        _request.append(int(period5_temp * 2))
        _request.append(int(period6_temp * 2))
        _request.append(int(we_period1_temp * 2))
        _request.append(int(we_period2_temp * 2))
        self._send_request(_request)

    def set_period1(self, period1_hour = None, period1_min = None, period1_temp = None):
        self.get_device_status()
        if (period1_hour == None):
            period1_hour = self.period1_hour
        if (period1_min == None):
            period1_min = self.period1_min
        if (period1_temp == None):
            period1_temp = self.period1_temp
        if (period1_hour < 0) or (period1_hour > 23):
            raise ValueError(
                'period1_hour (%s) has to be between 0 and 23.' % ( \
                period1_hour))
        if (period1_min < 0) or (period1_min > 59):
            raise ValueError(
                'period1_min (%s) has to be between 0 and 59.' % ( \
                period1_min))
        if (period1_hour > self.period2_hour) or \
            ((period1_hour == self.period2_hour) and (period1_min > self.period2_min)):
            raise ValueError(
                'period1 (%s:%s) has to be before period2 (%s:%s).' % ( \
                period1_hour,
                period1_min,
                self.period2_hour,
                self.period2_min))
        if period1_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period1_temp,
                self.max_temp))
        if period1_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period1_temp,
                self.min_temp))
        self.set_daily_schedule(
            period1_hour,
            period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            period1_temp, 
            self.period2_temp,
            self.period3_temp,
            self.period4_temp,
            self.period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_period2(self, period2_hour, period2_min, period2_temp):
        self.get_device_status()
        if (period2_hour == None):
            period2_hour = self.period2_hour
        if (period2_min == None):
            period2_min = self.period2_min
        if (period2_temp == None):
            period2_temp = self.period2_temp
        if (period2_hour < 0) or (period2_hour > 23):
            raise ValueError(
                'period2_hour (%s) has to be between 0 and 23.' % ( \
                period2_hour))
        if (period2_min < 0) or (period2_min > 59):
            raise ValueError(
                'period2_min (%s) has to be between 0 and 59.' % ( \
                period2_min))
        if (period2_hour < self.period1_hour) or \
            ((period2_hour == self.period1_hour) and (period2_min < self.period1_min)):
            raise ValueError(
                'period2 (%s:%s) has to be after period1 (%s:%s).' % ( \
                period2_hour,
                period2_min,
                self.period1_hour,
                self.period1_min))
        if (period2_hour > self.period3_hour) or \
            ((period2_hour == self.period3_hour) and (period2_min > self.period3_min)):
            raise ValueError(
                'period2 (%s:%s) has to be before period3 (%s:%s).' % ( \
                period2_hour,
                period2_min,
                self.period3_hour,
                self.period3_min))
        if period2_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period2_temp,
                self.max_temp))
        if period2_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period2_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            period2_hour,
            period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            period2_temp,
            self.period3_temp,
            self.period4_temp,
            self.period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_period3(self, period3_hour, period3_min, period3_temp):
        self.get_device_status()
        if (period3_hour == None):
            period3_hour = self.period3_hour
        if (period3_min == None):
            period3_min = self.period3_min
        if (period3_temp == None):
            period3_temp = self.period3_temp
        if (period3_hour < 0) or (period3_hour > 23):
            raise ValueError(
                'period3_hour (%s) has to be between 0 and 23.' % ( \
                period3_hour))
        if (period3_min < 0) or (period3_min > 59):
            raise ValueError(
                'period3_min (%s) has to be between 0 and 59.' % ( \
                period3_min))
        if (period3_hour < self.period2_hour) or \
            ((period3_hour == self.period2_hour) and (period3_min < self.period2_min)):
            raise ValueError(
                'period3 (%s:%s) has to be after period2 (%s:%s).' % ( \
                period3_hour,
                period3_min,
                self.period2_hour,
                self.period2_min))
        if (period3_hour > self.period4_hour) or \
            ((period3_hour == self.period4_hour) and (period3_min > self.period4_min)):
            raise ValueError(
                'period3 (%s:%s) has to be before period4 (%s:%s).' % ( \
                period3_hour,
                period3_min,
                self.period4_hour,
                self.period4_min))
        if period3_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period3_temp,
                self.max_temp))
        if period3_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period3_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            period3_hour,
            period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            period3_temp,
            self.period4_temp,
            self.period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_period4(self, period4_hour, period4_min, period4_temp):
        self.get_device_status()
        if (period4_hour == None):
            period4_hour = self.period4_hour
        if (period4_min == None):
            period4_min = self.period4_min
        if (period4_temp == None):
            period4_temp = self.period4_temp
        if (period4_hour < 0) or (period4_hour > 23):
            raise ValueError(
                'period4_hour (%s) has to be between 0 and 23.' % ( \
                period4_hour))
        if (period4_min < 0) or (period4_min > 59):
            raise ValueError(
                'period4_min (%s) has to be between 0 and 59.' % ( \
                period4_min))
        if (period4_hour < self.period3_hour) or \
            ((period4_hour == self.period3_hour) and (period4_min < self.period3_min)):
            raise ValueError(
                'period4 (%s:%s) has to be after period3 (%s:%s).' % ( \
                period4_hour,
                period4_min,
                self.period3_hour,
                self.period3_min))
        if (period4_hour > self.period5_hour) or \
            ((period4_hour == self.period5_hour) and (period4_min > self.period5_min)):
            raise ValueError(
                'period4 (%s:%s) has to be before period5 (%s:%s).' % ( \
                period4_hour,
                period4_min,
                self.period5_hour,
                self.period5_min))
        if period4_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period4_temp,
                self.max_temp))
        if period4_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period4_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            period4_hour,
            period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            self.period3_temp,
            period4_temp,
            self.period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_period5(self, period5_hour, period5_min, period5_temp):
        self.get_device_status()
        if (period5_hour == None):
            period5_hour = self.period5_hour
        if (period5_min == None):
            period5_min = self.period5_min
        if (period5_temp == None):
            period5_temp = self.period5_temp
        if (period5_hour < 0) or (period5_hour > 23):
            raise ValueError(
                'period5_hour (%s) has to be between 0 and 23.' % ( \
                period5_hour))
        if (period5_min < 0) or (period5_min > 59):
            raise ValueError(
                'period5_min (%s) has to be between 0 and 59.' % ( \
                period5_min))
        if (period5_hour < self.period4_hour) or \
            ((period5_hour == self.period4_hour) and (period5_min < self.period4_min)):
            raise ValueError(
                'period5 (%s:%s) has to be after period4 (%s:%s).' % ( \
                period5_hour,
                period5_min,
                self.period4_hour,
                self.period4_min))
        if (period5_hour > self.period6_hour) or \
            ((period5_hour == self.period6_hour) and (period5_min > self.period6_min)):
            raise ValueError(
                'period5 (%s:%s) has to be before period6 (%s:%s).' % ( \
                period5_hour,
                period5_min,
                self.period6_hour,
                self.period6_min))
        if period5_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period5_temp,
                self.max_temp))
        if period5_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period5_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            period5_hour,
            period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            self.period3_temp,
            self.period4_temp,
            period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_period6(self, period6_hour, period6_min, period6_temp):
        self.get_device_status()
        if (period6_hour == None):
            period6_hour = self.period6_hour
        if (period6_min == None):
            period6_min = self.period6_min
        if (period6_temp == None):
            period6_temp = self.period6_temp
        if (period6_hour < 0) or (period6_hour > 23):
            raise ValueError(
                'period6_hour (%s) has to be between 0 and 23.' % ( \
                period6_hour))
        if (period6_min < 0) or (period6_min > 59):
            raise ValueError(
                'period6_min (%s) has to be between 0 and 59.' % ( \
                period6_min))
        if (period6_hour < self.period5_hour) or \
            ((period6_hour == self.period5_hour) and (period6_min < self.period5_min)):
            raise ValueError(
                'period6 (%s:%s) has to be after period5 (%s:%s).' % ( \
                period6_hour,
                period6_min,
                self.period5_hour,
                self.period5_min))
        if period6_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                period6_temp,
                self.max_temp))
        if period6_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                period6_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            period6_hour,
            period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            self.period3_temp,
            self.period4_temp,
            self.period5_temp,
            period6_temp,
            self.we_period1_temp,
            self.we_period2_temp)

    def set_we_period1(self, we_period1_hour, we_period1_min, we_period1_temp):
        self.get_device_status()
        if (we_period1_hour == None):
            we_period1_hour = self.we_period1_hour
        if (we_period1_min == None):
            we_period1_min = self.we_period1_min
        if (we_period1_temp == None):
            we_period1_temp = self.we_period1_temp
        if (we_period1_hour < 0) or (we_period1_hour > 23):
            raise ValueError(
                'we_period1_hour (%s) has to be between 0 and 23.' % ( \
                we_period1_hour))
        if (we_period1_min < 0) or (we_period1_min > 59):
            raise ValueError(
                'we_period1_min (%s) has to be between 0 and 59.' % ( \
                we_period1_min))
        if (we_period1_hour > self.we_period2_hour) or \
            ((we_period1_hour == self.we_period2_hour) and (we_period1_min > self.we_period2_min)):
            raise ValueError(
                'we_period1 (%s:%s) has to be before we_period2 (%s:%s).' % ( \
                we_period1_hour,
                we_period1_min,
                self.we_period2_hour,
                self.we_period2_min))
        if we_period1_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                we_period1_temp,
                self.max_temp))
        if we_period1_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                we_period1_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            we_period1_hour,
            we_period1_min, 
            self.we_period2_hour,
            self.we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            self.period3_temp,
            self.period4_temp,
            self.period5_temp,
            self.period6_temp,
            we_period1_temp,
            self.we_period2_temp)

    def set_we_period2(self, we_period2_hour, we_period2_min, we_period2_temp):
        self.get_device_status()
        if (we_period2_hour == None):
            we_period2_hour = self.we_period2_hour
        if (we_period2_min == None):
            we_period2_min = self.we_period2_min
        if (we_period2_temp == None):
            we_period2_temp = self.we_period2_temp
        if (we_period2_hour < 0) or (we_period2_hour > 23):
            raise ValueError(
                'we_period2_hour (%s) has to be between 0 and 23.' % ( \
                we_period2_hour))
        if (we_period2_min < 0) or (we_period2_min > 59):
            raise ValueError(
                'we_period2_min (%s) has to be between 0 and 59.' % ( \
                we_period2_min))
        if (we_period2_hour < self.we_period1_hour) or \
            ((we_period2_hour == self.we_period1_hour) and (we_period2_min < self.we_period1_min)):
            raise ValueError(
                'we_period2 (%s:%s) has to be after we_period1 (%s:%s).' % ( \
                we_period2_hour,
                we_period2_min,
                self.we_period1_hour,
                self.we_period1_min))
        if we_period2_temp > self.max_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) higher than maximum set (%s°).' % ( \
                we_period2_temp,
                self.max_temp))
        if we_period2_temp < self.min_temp:
            raise ValueError(
                'Can\'t set a target temperature (%s°) lower than minimum set (%s°).' % ( \
                we_period2_temp,
                self.min_temp))
        self.set_daily_schedule(
            self.period1_hour,
            self.period1_min, 
            self.period2_hour,
            self.period2_min, 
            self.period3_hour,
            self.period3_min, 
            self.period4_hour,
            self.period4_min, 
            self.period5_hour,
            self.period5_min, 
            self.period6_hour,
            self.period6_min, 
            self.we_period1_hour,
            self.we_period1_min, 
            we_period2_hour,
            we_period2_min, 
            self.period1_temp, 
            self.period2_temp,
            self.period3_temp,
            self.period4_temp,
            self.period5_temp,
            self.period6_temp,
            self.we_period1_temp,
            we_period2_temp)

    # get device status
    # 0x01, 0x03, 0x00, 0x00, 0x00, 0x17
    # response:
    # 0x01, 0x03, 0x2E, 0x0r, 0xavp, Rt, Tt, 0xlm, Sen, Osv, Dif, Svh, Svl, AdjMSB, AdjLSB, Fre, POn, 
    # Unk1, Ext, hh, mm, ss, wd, P1h, P1m, P1t, P2h, P2m, P2t, P3h, P3m, P3t, P4h, P4m, P4t, 
    # P5h, P5m, P5t, P6h, P6m, P6t, weP1h, weP1m, weP1t, weP6h, weP6m, weP6t, Unk2, Unk3
    # r = Remote lock, 0 = Off, 1 = On
    # v = Valve, 0 = Valve off, 1 = Valve on
    # a = Manual over Auto, 0 = Off, 1 = On
    # p = Power State, 0 = Power off, 1 = Power on
    # Rt = Room temperature in degrees Celsius * 2
    # Tt = Target temperature in degrees Celsius * 2
    # l = Weekly schedule, 0x01 = 12345_67, 0x02 = 123456_7, 0x03 = 1234567
    # m = Operation mode, 0x00 = Manual, 0x03 = Auto
    # Sen = sensor, 0x00 = internal, 0x01 = external, 0x02 = internal control with external target
    # Osv = Limit temperature external sensor
    # Dif = Hysteresis
    # Svh = Heating max. temperature
    # Svl = Heating min. temperature
    # Adj = Temperature calibration -5~+5, 0.1 degree Celsius step 
    #       (e.g. -1 = 0xFFF6, -1.4 = 0xFFF2, 0 = 0x0000, +1 = 0x000A, +1.2 = 0x000C, +2 = 0x0014, etc.)
    # Fre = Frost Protection, 0 = On, 1 = Off
    # POn = PowerOn, 0 = Off, 1 = On
    # Unk1 = Unknown, 0x00
    # Ext = External temperature
    # hh = Time hour past midnight
    # mm = Time minute past hour
    # ss = Time second past minute
    # wd = Weekday 0x01 = Monday, 0x01 = Tuesday, ..., 0x06 = Saturday, 0x07 = Sunday
    # P1h = Period1 hour
    # P1m = Period1 minute
    # P1t = Period1 temperature
    # P2h = Period1 hour
    # P2m = Period1 minute
    # P2t = Period1 temperature
    # P3h = Period1 hour
    # P3m = Period1 minute
    # P3t = Period1 temperature
    # P4h = Period1 hour
    # P4m = Period1 minute
    # P4t = Period1 temperature
    # P5h = Period1 hour
    # P5m = Period1 minute
    # P5t = Period1 temperature
    # P6h = Period1 hour
    # P6m = Period1 minute
    # P6t = Period1 temperature
    # weP1h = Weekend Period1 hour
    # weP1m = Weekend Period1 minute
    # weP1t = Weekend Period1 temperature
    # weP6h = Weekend Period6 hour
    # weP6m = Weekend Period6 minute
    # weP6t = Weekend Period6 temperature
    # Unk2 = Unknown, 0x01
    # Unk3 = Unknown, 0x02
    def get_device_status(self):
        if self._authenticated is False:
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
            _request = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x17])
            _response = self._send_request(_request)
            self.key_lock = _response[3] & 0x01
            self.manual_in_auto = (_response[4] >> 6) & 0x01
            self.valve_state =  (_response[4] >> 4) & 0x01
            self.power_state =  _response[4] & 0x01
            self.room_temp = float((_response[5] & 0xFF) / 2.0)
            self.target_temp = float((_response[6] & 0xFF) / 2.0)
            self.operation_mode = _response[7] & 0x01
            self.schedule = (_response[7] >> 4) & 0x0F
            self.sensor = _response[8]
            self.external_max_temp = float(_response[9])
            self.hysteresis = _response[10]
            self.max_temp = _response[11]
            self.min_temp = _response[12]
            self.calibration = (_response[13] << 8) + _response[14]
            if self.calibration > 0x7FFF:
                self.calibration = self.calibration - 0x10000
            self.calibration = float(self.calibration / 2.0)
            self.frost_protection = _response[15]
            self.poweron = _response[16]
            self.unknown1 = _response[17]
            self.external_temp = float((_response[18] & 0xFF) / 2.0)
            self.clock_hour = _response[19]
            self.clock_minute = _response[20]
            self.clock_second = _response[21]
            self.clock_weekday = _response[22]
            self.period1_hour = _response[23]
            self.period1_min = _response[24]
            self.period2_hour = _response[25]
            self.period2_min = _response[26]
            self.period3_hour = _response[27]
            self.period3_min = _response[28]
            self.period4_hour = _response[29]
            self.period4_min = _response[30]
            self.period5_hour = _response[31]
            self.period5_min = _response[32]
            self.period6_hour = _response[33]
            self.period6_min = _response[34]
            self.we_period1_hour = _response[35]
            self.we_period1_min = _response[36]
            self.we_period2_hour = _response[37]
            self.we_period2_min = _response[38]
            self.period1_temp = float(_response[39] / 2.0)
            self.period2_temp = float(_response[40] / 2.0)
            self.period3_temp = float(_response[41] / 2.0)
            self.period4_temp = float(_response[42] / 2.0)
            self.period5_temp = float(_response[43] / 2.0)
            self.period6_temp = float(_response[44] / 2.0)
            self.we_period1_temp = float(_response[45] / 2.0)
            self.we_period2_temp = float(_response[46] / 2.0)
            self.unknown2 = _response[47]
            self.unknown3 = _response[48]
            self.fwversion = self.get_fwversion()

