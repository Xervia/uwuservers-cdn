class SERVER_STATUS:
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    RESTARTING = "restarting"
    CRASHED = "crashed"
    ERROR = "error"
    UNKNOWN = "unknown"

class SERVER_TYPE:
    VANILLA = "vanilla"
    FORGE = "forge"

class SERVER_VERSION:
    V171 = "1.17.1"
    V180 = "1.18"
    V181 = "1.18.1"
    V182 = "1.18.2"
    V190 = "1.19"
    V191 = "1.19.1"
    V192 = "1.19.2"
    V193 = "1.19.3"
    V194 = "1.19.4"
    V200 = "1.20"
    V201 = "1.20.1"
    V202 = "1.20.2"
    V203 = "1.20.3"
    V204 = "1.20.4"
    V206 = "1.20.6"
    V210 = "1.21"
    V211 = "1.21.1"

def getData(class_name):
    keys = class_name.__dict__.keys()
    filtered_keys = [ key for key in keys if key not in ["__module__", "__doc__", "__weakref__", "__dict__", "__doc__"] ]

    values = []

    for key in filtered_keys:
        values.append(getattr(class_name, key))
    
    return values

def isInstanceOf(data, class_name):
    if data not in getData(class_name):
        return False
    return True