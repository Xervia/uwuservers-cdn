import requests

class DataBase:
    def __init__(self):
        self.uri = "https://uwuservers.com/api/v1/"
        
    def request(self, path, headers=None):
        response = requests.get(f"{self.uri}{path}", headers=headers)
        if response.status_code != 200:
            return None
        return response.json()['data']
    
    def get_user_by_token(self, token: str):
        return self.request("user", {"Authorization": token})
    
    def get_user_by_uuid(self, uuid: str):
        return self.request(f"user/{uuid}")
    
    def get_user_permissions(self, uuid: str):
        return self.request(f"user/{uuid}/permissions")
    
    def check_user_permission(self, uuid: str, permission: str):
        return self.request(f"user/{uuid}/permissions/{permission}")
        
    def get_user_name(self, uuid: str):
        return self.request(f"user/{uuid}/name")