import requests
import os
from dotenv import load_dotenv

load_dotenv()

class cloudflare:
    def __init__(self):
        self.zoneId = os.getenv("ZONE_ID")
        self.token = os.getenv("TOKEN")
        self.email = os.getenv("EMAIL")
        
        self.api_url = f"https://api.cloudflare.com/client/v4/zones/{self.zoneId}/dns_records"
        
        self.headers = {
            "X-Auth-Email": self.email,
            # "X-Auth-Key": self.token,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def reset(self):
        response = requests.get(self.api_url, headers=self.headers)
        json = response.json()
        
        for record in json['result']:
            if "data" not in record:
                continue
            
            if record['type'] == "SRV" and record['name'] == "_minecraft_tcp.uwuservers.com" and "port" in record['data']:
                self.remove_port(record['data']['port'])
    
    def get_port(self, port: int):
        response = requests.get(self.api_url, headers=self.headers)

        for record in response.json()['result']:
            if "data" not in record or "port" not in record['data']:
                continue
            
            if record['data']['port'] == port:
                return record

        return None

    def add_port(self, port: int):
        data = {
            "content": f"0 0 {port} servers.uwuservers.com",
            "data": {
                "priority": 0,
                "weight": 0,
                "port": port,
                "target": "servers.uwuservers.com"
            }, 
            "name": "_minecraft_tcp.uwuservers.com",
            "proxiable": False,
            "proxied": False,
            "ttl": 1,
            "type": "SRV",
            "zone_id": self.zoneId,
            "zone_name": "uwuservers.com",
            "priority": 0,
            "comment": "",
            "tags": []
        }

        response = requests.post(self.api_url, headers=self.headers, json=data)

        return response.json()
    
    def remove_port(self, port: int):
        record = self.get_port(port)

        if record is None:
            return None

        response = requests.delete(f"{self.api_url}/{record['id']}", headers=self.headers)

        return response.json()
