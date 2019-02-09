"""
    REST API for Pi GPIO Controls.
        - arush15june 2018/02/07
"""
from flask import Flask, request, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_cors import CORS

from helpers import *

"""
    Flask Config
"""

app = Flask(__name__)
app.config['DEBUG'] = False
app.secret_key = 'd4abb98d-5864-4e3b-a845-2c4969f3b9be'

""" Enable CORS """
cors = CORS(app, 
            resources={r"/api/*": {"origins": "*"}}
        )
api = Api(app) # API Singleton

"""
    Resources
"""
class PiResource(Resource):
    """
        Abstract Resource for POST actions.
    """
    parser = reqparse.RequestParser()

    ERROR_MESSAGE = 'Failure'
    ERROR_STATUS_CODE = 503

    def post(self):
        args = self.parser.parse_args()

        return self.post_action(args)

    def post_action(self, args):
        raise NotImplementedError()

    def error_response(self, *args, **kwargs):
        response = {
            'message': self.ERROR_MESSAGE
        }

        data = kwargs.get('data')
        if data is not None:
            response.update(data)
        
        return response, self.ERROR_STATUS_CODE

class PinResource(PiResource):
    """
        Abstract class to accept pin in args.
    """

    DEFAULT_PIN = 17

    def __init__(self, *args, **kwargs):
        super(PinResource, self).__init__(*args, **kwargs)
        self.parser.add_argument('pin', type=int, default=self.DEFAULT_PIN)

class BlinkResource(PinResource):
    """
        /blink
        Blink an led on a pin for required seconds.
        POST Arguments:
            `pin`: pin to blink on. Default = 17
            `time`: seconds to blink for. Default = 2s

        Example:
            /blink?pin=17&time=2
    """    
    DEFAULT_PIN = 17 # GPIO17
    DEFAULT_BLINK_TIME = 2 # seconds

    SUCCESS_MESSAGE = 'Blink successful on GPIO{} for {} seconds'
    ERROR_MESSAGE = 'Blink Failed'

    def __init__(self, *args, **kwargs):
        super(BlinkResource, self).__init__(*args, **kwargs)
        self.parser.add_argument('time', type=int, default=self.DEFAULT_BLINK_TIME)

    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args['pin']
        time = parser_args['time']
        try:
            """
                blink function from helpers.py.
            """
            blink(pin, time)
            
            response = {'message': self.SUCCESS_MESSAGE.format(pin, time)}

            return response
        except:
            return self.error_response()
        
class TemperatureResource(PinResource):
    """
        /temperature
        Return the current temperature from the temperature sensor
        
        POST Arguments:
            `pin`: pin to read temp from. Default=24
            `units`: Celius/Farheneit (C/F)
        Example:
            /temperature?pin=24&units=C
    """
    
    DEFAULT_PIN = 24 # GPIO24
    DEFAULT_UNITS = 'C'

    ERROR_MESSAGE = 'Error retrieving temperature'

    VALID_UNITS = set(['C', 'F'])

    def __init__(self, *args, **kwargs):
        super(TemperatureResource, self).__init__(*args, **kwargs)
        self.parser.add_argument('units', type=str, )

    def set_units(self, recvd_units, *args, **kwargs):
        return self.DEFAULT_UNITS if recvd_units not in self.VALID_UNITS else recvd_units
    
    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args['pin']
        units = self.set_units(parser_args['units'])
        try:
            """
                read_temperature function from helpers.py
            """
            temperature = read_temperature(pin, units)
            response = {
                'temperature': temperature,
                'units': units
            }

            return response
        except:
            return self.error_response()


class InvalidServoLocationError(Exception):
    pass

class ServoResource(PinResource):
    """
    /servo
    Control a servo on `pin` to location `location`.

    POST Arguments:
        location: min/mid/max
        pin: default = 14
    Example:
        /servo?location=min&pin=14

    """

    DEFAULT_PIN = 14

    SUCCESS_MESSAGE = 'Successfully moved Servo on GPIO{} to {} position'
    ERROR_MESSAGE = 'Error Handling Servo'

    VALID_LOCATIONS = set(['min', 'mid', 'max'])

    def __init__(self, *args, **kwargs):
        super(ServoResource, self).__init__(*args, **kwargs)
        self.parser.add_argument('location', type=str, required=True)
        
    def verify_location(self, location):
        if location not in self.VALID_LOCATIONS:
            raise InvalidServoLocationError()
        else:
            return True
        
    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args.get('pin')
        location = parser_args.get('location')
        try:
            self.verify_location(location)
            """
                move_servo function from helpers.py
            """
            move_servo(pin, location)

            response = {'message': self.SUCCESS_MESSAGE.format(pin, location )}

            return response
        except:
            return self.error_response()

class InvalidStreamError(Exception):
    pass

class BuzzerResource(PinResource):
    """
    /buzzer
    Play a bitstream on buzzer connected to `pin`.

    POST Arguments:
        stream: bitstream to play.
        high_time: time to keep the buzzer high for. milliseconds, Default = 500
        pin: default = 3
    Example:
        /servo?bitstream=110101001&pin=14&high_time=500

    """

    DEFAULT_PIN = 27

    DEFAULT_HIGH_TIME = 500 # ms

    SUCCESS_MESSAGE = 'Played bitstream on buzzer at GPIO{}'
    ERROR_MESSAGE = 'Error playing bitstream'

    VALID_INPUT = set(['0', '1'])

    def __init__(self, *args, **kwargs):
        super(BuzzerResource, self).__init__(*args, **kwargs)
        self.parser.add_argument('stream', type=str, required=True)
        self.parser.add_argument('high_time', type=int, default=self.DEFAULT_HIGH_TIME)
        
    def set_stream(self, stream):
        validity_list = [char in self.VALID_INPUT for char in stream]
        if False in validity_list:
            raise InvalidStreamError()
        else:
            return stream
        
        
    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args.get('pin')
        high_time = parser_args.get('high_time')
        try:
            stream = self.set_stream(parser_args['stream'])
            """
                play_buzzer function from helpers.py
            """
            play_buzzer(pin, stream, high_time)
            
            response = {'message': self.SUCCESS_MESSAGE.format(pin)}
            return response
        except:
            return self.error_response()

"""
    Add Resource to API.
"""
api.add_resource(BlinkResource, '/api/blink')
api.add_resource(TemperatureResource, '/api/temperature')
api.add_resource(ServoResource, '/api/servo')
api.add_resource(BuzzerResource, '/api/buzzer')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')