## Tesla Energy Service Engineering Data Engineer Evaluation

### Welcome to the Data Engineer Evaluation. This is an precursor set of tasks to those you will be expcted to perform as part of the Energy Service Engineering Infrastructure and Analytics team.
#### Please reach out if you have any questions

Create an API that accepts:
- `POST` request at `/temp`
- `GET` request at `/errors`
- `DELETE` request at `/errors`


The `POST` request at `/temp` should accept a JSON blob in the following format:
- `{"data": __data_string__}`
- where `__data_string__` is format:
    - `__device_id__:__epoch_ms__:'Temperature':__temperature__`
      - where `__device_id__` is the device ID (int32)
      - `__epoch_ms__` is the timestamp in EpochMS (int64)
      - `__temperature__` is the temperature (float64)
      - and `'Temperature'` is the exact string
- Example `{"data": "365951380:1640995229697:'Temperature':58.48256793121914"}`
  
Response:
- If for any reason the data string is not formatted correctly, return `{"error": "bad request"}` with a `400` status code
- If the temperature is at or over 90
  - return `{"overtemp": true, "device_id": __device_id__, "formatted_time": __formatted_time__}`,
    - where `__device_id__` is the device ID (int32)
    - and `__formatted_time__` is the timestamp formatted to `%Y/%m/%d %H:%M:%S`
  - otherwise return `{"overtemp": false}`

The `GET` request at `/errors` should return all data strings which have been incorrectly formatted. The response should 
be in the following format:
- `{"errors": [__error1__, __error2__] }`
  - Where `__errorX__` is the exact data string received

The `DELETE` request at `/errors` should clear the errors buffer.

The API should be hosted on the public internet, accessible without running a local server. 
Please provide the URL of the API, as well as the source code.

We will be testing your program with a variety of inputs. 
Whilst there are many possible corner cases and extensions, ensure that your program performs the above criteria correctly.