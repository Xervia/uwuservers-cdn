from ..threads import Threads
import time

class ratelimit:
    def __init__(self):
        self.ipList = {}
        self.limit = 1000 # requests per minute
        
        self.threads = Threads()
        self.threads.append(self.update_ipList)()
    
    def update_ipList(self):
        while True:
            time.sleep(60)
            for ip in self.ipList:
                self.ipList[ip] = 0
    
    def check_ip(self, ip):
        if ip not in self.ipList:
            self.ipList[ip] = 1
        self.ipList[ip] += 1
        if self.ipList[ip] >= self.limit:
            return False
        return True