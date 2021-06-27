"""Support for Hysen thermostats."""

from broadlink.device import device as broadlink_device
from broadlink.exceptions import check_error
from broadlink.helpers import calculate_crc16

class HysenDevice(broadlink_device):
    def __init__ (self, host, mac, devtype, timeout):
        broadlink_device.__init__(self, host, mac, devtype, timeout)
        
    # Send a request to the device
    # Returns decrypted payload
    # Device's memory data is structured in an array of bytes, word (2 bytes) aligned
    # input_payload should be a bytearray
    # There are three known different request types (commands)
    # 1. write a word (2 bytes) at a given position (position counted in words)
    #    Command example
    #      0x01, 0x06, 0x00, 0x04, 0x28, 0x0A
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x06 - write word at a given position 
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte which is memory data word's index
    #        0x04 - the fifth word in memory data 
    #      the bytes to be written
    #        0x28, 0x0A - cooling max_temp (sh1) = 40, cooling min_temp (sl1) = 10
    #    No error confirmation response 
    #      0x01, 0x06, 0x00, 0x04, 0x28, 0x0A
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x06 - write word at a given position 
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte which is memory data word's index
    #        0x04 - the fifth word in memory data 
    #      the bytes written
    #        0x28, 0x0A - cooling max_temp (sh1) = 40, cooling min_temp (sl1) = 10
    # 2. write several words (multiple of 2 bytes) at a given position (position counted in words)
    #    Command example
    #      0x01, 0x10, 0x00, 0x07, 0x00, 0x02, 0x04, 0x08, 0x14, 0x10, 0x02
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x10 - write several words at a given position 
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte representing memory data word's index
    #        0x07 - the eighth word in memory data
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte representing the number of words (2 bytes) to be written
    #        0x02 - 2 words
    #      a byte representing the number of bytes to be written (previous word multiplied by 2)
    #        0x04 - 4 bytes
    #      the bytes to be written
    #        0x08, 0x14, 0x10, 0x02 - hour = 8, min = 20, sec = 10, weekday = 2 = Tuesday
    #    No error confirmation response
    #      0x01, 0x10, 0x00, 0x08, 0x00, 0x02
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x10 - write several words at a given position 
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte representing memory data word's index
    #        0x07 - the eighth word in memory data
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte representing the number of words (2 bytes) written
    #        0x02 - 2 words
    # 3. read memory data from a given position (position counted in words)
    #    Command example
    #      0x01, 0x03, 0x00, 0x07, 0x00, 0x02
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x03 - read several words at a given position 
    #      an unknown byte (always 0x00)
    #        0x00
    #      a byte representing memory data word's index
    #        0x07 - the eighth word in memory data
    #      a byte representing the number of words to be read
    #        0x02 - 2 words
    #    No error confirmation response
    #      0x01, 0x03, 0x04, 0x08, 0x14, 0x10, 0x02
    #      first byte 
    #        0x01 - header
    #      a byte representing command type
    #        0x03 - read command 
    #      a byte representing the number of bytes read
    #        0x04 - 4 bytes 
    #      the memory data bytes
    #        0x08, 0x14, 0x10, 0x02 - hour = 8, min = 20, sec = 10, weekday = 2 = Tuesday
    # Error responses for any command type
    #      0x01, 0xXX, 0xYY where
    #      first byte 
    #        0x01 - header
    #      second byte - Most significant bit 1 (error), last significant bits is the command type
    #        e.g. 0x90 - error in command type 0x10
    #      third byte
    #        0xYY - error type
    #        0x01 - Unknown command
    #        0x02 - Length missing or too big
    #        0x03 - Wrong length
    # New behavior: raises a ValueError if the device response indicates an error or CRC check fails
    # The function prepends length (2 bytes) and appends CRC
    # This function is adapted from the original broadlink.climate.py code by mjg59
    def _send_request(self, input_payload):
        crc = calculate_crc16(bytes(input_payload))
                
        # first byte is length, +2 for CRC16
        request_payload = bytearray([len(input_payload) + 2,0x00])
        request_payload.extend(input_payload)

        # append CRC
        request_payload.append(crc & 0xFF)
        request_payload.append((crc >> 8) & 0xFF)

        # send to device
        response = self.send_packet(0x6a, request_payload)
        check_error(response[0x22:0x24])
        response_payload = self.decrypt(response[0x38:])
        
        # experimental check on CRC in response (first 2 bytes are len, and trailing bytes are crc)
        response_payload_len = response_payload[0]
        if response_payload_len + 2 > len(response_payload):
            raise ValueError('hysen_response_error','first byte of response is not length')
        crc = calculate_crc16(response_payload[2:response_payload_len])
        if (response_payload[response_payload_len] == crc & 0xFF) and \
           (response_payload[response_payload_len+1] == (crc >> 8) & 0xFF):
            return_payload = response_payload[2:response_payload_len]
        else:
            raise ValueError('hysen_response_error','CRC check on response failed')
            
        # check if return response is right
        if (input_payload[0:2] == bytearray([0x01, 0x06])) and \
           (input_payload != return_payload):
            self.auth()
            raise ValueError(
                'Hysen_response_error: request %s response %s',
                ' '.join(format(x, '02x') for x in bytearray(input_payload)),
                ' '.join(format(x, '02x') for x in bytearray(return_payload))
            )
        elif (input_payload[0:2] == bytearray([0x01, 0x10])) and \
             (input_payload[0:6] != return_payload):
            self.auth()
            raise ValueError(
                'Hysen_response_error: request %s response %s',
                ' '.join(format(x, '02x') for x in bytearray(input_payload)),
                ' '.join(format(x, '02x') for x in bytearray(return_payload))
            )
        elif (input_payload[0:2] == bytearray([0x01, 0x03])) and \
             ((input_payload[0:2] != return_payload[0:2]) or \
             ((2 * input_payload[5]) != return_payload[2]) or \
             ((2 * input_payload[5]) != len(return_payload[3:]))):
            self.auth()
            raise ValueError(
                'Hysen_response_error: request %s response %s',
                ' '.join(format(x, '02x') for x in bytearray(input_payload)),
                ' '.join(format(x, '02x') for x in bytearray(return_payload))
            )
        else:
            return return_payload

