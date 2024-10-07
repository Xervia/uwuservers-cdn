import requests

class ServerApi:
    def __init__(self):
        self.api_url = "https://api.mcstatus.io/v2/status/java/servers.uwuservers.com:"
        self.host = "servers.uwuservers.com"
        self.url = f"{self.api_url}{self.host}:"
    
    def request(self, port, running):
        result = {
            "motd": {
                "html": "",
                "raw": "",
                "clean": ""
            },
            "icon": "",
            "players": {
                "online": 0,
                "max": 0,
                "list": []
            },
        }
        
        if port == -1 or not running:
            return result
        
        try:
            response = requests.get(f'{self.api_url}{port}').json()
            
            result["motd"]["raw"] = response["motd"]["raw"]
            result["motd"]["html"] = response["motd"]["html"]
            result["motd"]["clean"] = response["motd"]["clean"]
            result["icon"] = response["icon"]
            result["players"]["online"] = response["players"]["online"]
            result["players"]["max"] = response["players"]["max"]
            result["players"]["list"] = response["players"]["list"]
            
            return result
        except Exception as e:
            return result