import numpy as np
import os
from datetime import datetime as dt
from flasgger import Swagger
from flasgger.utils import swag_from
from flask import Flask, make_response, request, jsonify
from flask_expects_json import expects_json
from functools import wraps
from jsonschema import ValidationError
from werkzeug.exceptions import BadRequest


# Inputs
class TempDataSchema:
    def __init__(self):
        """ Define format of data request, used by expects_json
            minLength 31=semicolon(3)+epoch_ms(13)+'Temperature'(13)
            pattern = regex to assert for 3 semicolons
        """
        self.data = {
            "type": "string",
            "minLength": 29,
            "pattern": "^(?:(?!:).)*(?::(?:(?!:).)*){3}$"
        }


class TempSchema:
    def __init__(self):
        """ Define format required for expects_json
            "data" is a required key in the request
        """
        self.type = "object"
        self.properties = TempDataSchema().__dict__
        self.required = ["data"]


class TempData():
    """ Convert response object to useful variables
    """
    def __init__(self, request):
        self.data_string = request.get_json().get("data")
        self.split_data = self.data_string.split(":")
        self.device_id = self.split_data[0]
        self.epoch_ms = self.split_data[1]
        self.temp_key = self.split_data[2]
        self.temp = self.split_data[3]


# Outputs
class ErrorResponse:
    """ Response for error messages
        Convert message string to object {"error":message}
    """
    def __init__(self, message):
        self.error = message


class ErrorList:
    """ Response for GET /errors
        Convert errors_list to object {"errors":errors_list}
    """
    def __init__(self, errors_list):
        self.errors = errors_list


class OverTempTrue:
    """ Response for temp value that is "Over Temp" (aka >= 90)
    """
    def __init__(self, device_id, epoch_ms):
        self.overtemp = True
        self.device_id = int(np.int32(device_id))
        self.epoch_ms = dt.fromtimestamp(int(epoch_ms)/1000.0) \
                          .strftime('%Y/%m/%d %H:%M:%S')


class OverTempFalse:
    """ Response for temp value that is not "Over Temp" (aka < 90)
    """
    def __init__(self):
        self.overtemp = False


def create_app(test_config=None):
    # create and configure the app
    seia_api = Flask(__name__, instance_relative_config=True)
    swagger = Swagger(seia_api)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        seia_api.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        seia_api.config.from_mapping(test_config)

    # Establish list object to collect error messages
    # TODO: substitute with database
    errors_list = []

    # Error Handling and Validations
    @seia_api.errorhandler(400)
    def handle_badrequest(e):
        """ Response handling for format issues.
            Used with POST body is formatted wrong
        """
        # handle incorrect schema errors
        if isinstance(e.description, ValidationError):
            response = ErrorResponse(e.description.message).__dict__
            return make_response(jsonify(response), 200)

        # handle other "Bad Request" errors
        else:
            response = ErrorResponse(e.description).__dict__
            return make_response(jsonify(response), 200)

    def validate_tempdata(f):
        """ Checks if data string from request meets expectations
            Format expectations are checked
            Value expectations are checked
            Returns 404 'bad request' if expectation is not met
        """
        @wraps(f)
        def wrapper(*args, **kw):
            # load request data string into variables
            data = TempData(request)

            # validate format
            try:
                np.int32(data.device_id)
                int(data.epoch_ms)
                str(data.temp_key)
                np.float64(data.temp)
            except Exception:
                errors_put(data.data_string)
                raise BadRequest(description='bad request')

            # validate value
            if len(str(data.epoch_ms)) != 13:
                errors_put(data.data_string)
                raise BadRequest(description='bad request')

            if str(data.temp_key) != "'Temperature'":
                errors_put(data.data_string)
                raise BadRequest(description='bad request')
            return f(*args, **kw)

        return wrapper

    # Endpoints
    @seia_api.post("/temp")
    @expects_json(TempSchema().__dict__)
    @validate_tempdata
    @swag_from("swagger/temp_post.yml", endpoint='temp', methods=['POST'])
    def temp_post():
        # load request data string into vars
        data = TempData(request)

        # When temp is over 90 return overtemp True response
        if np.float64(data.temp) >= 90:
            response = OverTempTrue(data.device_id, data.epoch_ms).__dict__
            return make_response(jsonify(response), 200)
        else:
            response = OverTempFalse().__dict__
            return make_response(jsonify(response), 200)

    @seia_api.get("/errors")
    @swag_from("swagger/errors_get.yml", endpoint='errors', methods=['GET'])
    def errors_get():
        response = ErrorList(errors_list).__dict__
        return make_response(jsonify(response), 200)

    @seia_api.put("/errors/<data>")
    def errors_put(data):
        errors_list.append(data)
        response = ErrorResponse(data).__dict__
        return make_response(jsonify(response), 200)

    @seia_api.delete("/errors")
    @swag_from("swagger/errors_delete.yml", endpoint='errors', methods=['DELETE'])
    def errors_delete():
        errors_list.clear()
        return make_response(jsonify({}), 204)

    return seia_api


seia_api = create_app()


if __name__ == '__main__':
    seia_api.run()
