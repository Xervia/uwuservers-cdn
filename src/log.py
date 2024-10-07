import os
import re

class Log:
    def __init__(self, path: str):
        self.path = path + f"console.log"
        self.log_limit = 100
    
    def remove_line(self, int):
        if not os.path.exists(self.path):
            return None
        
        with open(self.path, "r+") as file:
            lines = file.readlines()
            file.close()
        
        with open(self.path, "w") as file:
            if int <= len(lines) - 1 or int == -1:
                lines.pop(int)
                file.writelines(lines)
            file.close()
        
    def write(self, log: str):
        with open(self.path, "a") as file:
            file.write(log)
            file.close()
    
    def read(self, int):
        if not os.path.exists(self.path):
            return None
        
        with open(self.path, "r+") as file:
            lines = self.read_all()
            return lines[int]
    
    def read_all(self):
        if not os.path.exists(self.path):
            return None
        
        with open(self.path, "r+") as file:
            lines = file.readlines()
            file.close()
            
            lines = [ line.replace('/root/uwuservers-cdn/servers', '...') for line in lines ]
            
            return lines
    
    def read_all_limited(self, log_limit: int = None):
        log_limit = log_limit or self.log_limit
        
        lines = self.read_all()
        
        if lines is None:
            return []
        
        return lines[-log_limit:]
    
    def clear(self):
        if os.path.exists(self.path):
            os.unlink(self.path)
            return True