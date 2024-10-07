from flask import json, request, jsonify

class RESULT_STATUS:
    SUCCESS = "success"
    ERROR = "error"

def result(payload):
    status, data, code = payload
    
    result = {
        "status": status,
        "data": data
    }
    
    return jsonify(result), code

def check_json(keys):
    if not keys or not request.json:
        return None
    
    for key in keys:
        if key not in request.json and not key.endswith("?"):
            return result((RESULT_STATUS.ERROR, f"error/missing_json_value/{key}", 400))

def check_params(params):
    if not params:
        return None
    
    values = list(params.values())
    keys = list(params.keys())
    
    for i, param in enumerate(values):
        if param is None:
            return result((RESULT_STATUS.ERROR, f"error/invalid_param/{keys[i]}", 400))
        
def get_json(keys):
    if not keys:
        return None
    
    json = {}
    
    for key in keys:
        if key.endswith("?"):
            key = key[:-1]
            
            if key not in request.json:
                json[key] = None
                continue
        
        if key in request.json:
            json[key] = request.json[key]
            
    return json

def process_request(func, params=None, keys=None):
    json_check = check_json(keys)
    params_check = check_params(params)
    token = request.headers.get("Authorization")
    
    if json_check or params_check:
        return json_check or params_check
    
    json = get_json(keys)
    
    if not params:
        return result(func())
    elif not token:
        return result(func(params))
    elif not json:
        return result(func(params, token))
    return result(func(params, token, get_json(keys)))