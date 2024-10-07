import json
import os

class ManagerData:
    def __init__(self):
        self.path = "manager.dat"
        self.data = {}
        
        self.load()
        
    def raw_data(self):
        return {
            "servers/limit": 20,
            "servers/registered": 0,
            "servers/registered-private": 0,
            "servers/running": 0,
            "servers/running-private": 0,
            "useage/cpu": 0.0,
            "useage/ram": 0.0
        }
    
    def load(self):
        if not os.path.exists(self.path):
            file = open(self.path, "w")
            json.dump({}, file)
            file.close()
            return
        
        with open(self.path, "r") as file:
            self.data = json.load(file)
    
    def save(self):
        with open(self.path, "w") as file:
            json.dump(self.data, file)
    
    def get(self, key):
        if key not in self.data:
            return None
        
        return self.data.get(key)
    
    def set(self, key, value):
        if key not in self.data:
            return None
        
        self.data[key] = value
        self.save()
        
        return self.data
    
    def increment(self, key):
        if key not in self.data:
            return None
        
        self.data[key] += 1
        self.save()
        
        return self.data
    
    def decrement(self, key):
        if key not in self.data:
            return None
        
        self.data[key] -= 1
        self.save()
        
        return self.data
        
    def reset(self):
        self.data = self.raw_data()
        self.save()
        
        return self.data
    
    def reset_specific(self, key):
        if key not in self.raw_data():
            return None
        
        self.data[key] = self.raw_data()[key]
        self.save()
        
        return self.data
    
    def get_all(self):
        self.load()
        return self.data