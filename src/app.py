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
cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app) # API Singleton

"""
    Resources
"""

class PiResource(Resource):
    """
        Abstract Resource for POST actions.
    """
    parser = reqprase.RequestParser()

    ERROR_MESSAGE = 'Failure'
    ERROR_STATUS_CODE = 400

    def post(self):
        args = self.parser.parse_args()

        return post_action(args)

    def post_action(self, args):
        raise NotImplementedError()

    def error_response(self, *args, **kwargs):
        response_json = {
            'message': self.ERROR_MESSAGE
        }

        data = kwargs.get('data')
        if data is not None:
            response_json.update(data)
        
        return make_response(response_json, status=self.ERROR_MESSAGE)

class BlinkResource(PiResource):
    """
        /blink
        Blink an led on a pin for required seconds.
        POST Arguments:
            `pin`: pin to blink on. Default = 17
            `seconds`: seconds to blink for. Default = 2s

        Example:
            /blink?pin=17&seconds=2
    """
    DEFAULT_PIN = 17 # GPIO17
    DEFAULT_BLINK_TIME = 2 # seconds

    parser.add_argument('pin', type=int, required=True, default=self.DEFAULT_PIN)
    parser.add_argument('seconds', type=int, default=self.DEFAULT_BLINK_TIME)

    SUCCESS_MESSAGE = 'Blink successful on Pin {} for {} seconds'
    ERROR_MESSAGE = 'Blink Failed'

    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args['pin']
        seconds = parser_args['seconds']
        try:
            """
                blink function from helpers.py.
            """
            blink(pin, seconds)
            
            return make_response(
                {'message': self.SUCCESS_MESSAGE.format(pin, seconds)}
            )
        except:
            return self.error_response()
        
class TemperatureResource(PiResource):
    """
        /temperature
        Return the current temperature from the temperature sensor
        
        POST Arguments:
            `pin`: pin to read temp from. Default=24
        Example:
            /temperature?pin=24
    """
    
    DEFAULT_PIN = 24 # GPIO24

    parser.add_argument('pin', type=int, required=True, default=self.DEFAULT_PIN)
    
    ERROR_MESSAGE = 'Error retrieving temperature'

    def post_action(self, parser_args, *args, **kwargs):
        pin = parser_args['pin']
        try:
            """
                read_temperature function from helpers.py
            """
            temperature = read_temperature(pin)
            return make_response({
                'temperature': temperature
            })
        except:
            return self.error_response()


"""
    Add Resource to API.
"""
api.add_resource(BlinkResource, "/blink")
api.add_resource(TemperatureResource, "/temperature")

if __name__ == "__main__":
    app.run(debug=True)