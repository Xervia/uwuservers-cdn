from .cloudflare import cloudflare
import random
import json
import pathlib


class Ports:
    def __init__(self):
        self.port_var = [25022, 25028, 25506, 25474, 25416, 25234, 25250, 25289, 25152,
                         25455, 25379, 25008, 25103, 25295, 25214, 25285, 25528, 25274, 25018, 25428]
        self.port_dif = len(self.port_var)
        self.ports = []

        self.ports_path = "./ports.json"

        self.load_ports()
        
    def reset(self):
        self.ports = []
        self.save_ports()
        
        try:
            cloudflare().reset()
        except Exception as e:
            raise Exception("Failed to reset ports on Cloudflare")

    def load_ports(self):
        if not pathlib.Path(self.ports_path).exists():
            self.save_ports()

        with open(self.ports_path) as f:
            content = f.read().strip()
            if not content:
                self.save_ports()
                return

            self.ports = json.loads(content)

    def save_ports(self):
        with open(self.ports_path, "w") as f:
            json.dump(self.ports, f)

    def remove_port(self, port):
        if port not in self.ports:
            return
        
        self.ports.remove(port)
        self.save_ports()
        
        try:
            cloudflare().remove_port(port)
        except Exception as e:
            raise Exception("Failed to remove port from Cloudflare")
    
    def add_port(self, port):
        if port in self.ports:
            return
        
        self.ports.append(port)
        self.save_ports()
        
        try:
            cloudflare().add_port(port)
        except Exception as e:
            raise Exception("Failed to add port to Cloudflare")

    def add_random_port(self):
        self.load_ports()
        
        if len(self.ports) >= self.port_dif:
            return None

        free_ports = list(set(self.port_var) - set(self.ports))

        if not free_ports:
            return None

        i = random.randint(0, len(free_ports) - 1)
        port = free_ports[i]

        while port in self.ports:
            port = self.add_random_port()

        if port is None:
            return None

        self.add_port(port)

        return port
