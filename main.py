from src.server_ports import Ports
import src.api as api

if __name__ == "__main__":
    Ports().reset()
    api.run()