from .server_details import SERVER_TYPE, SERVER_VERSION, SERVER_STATUS
from .result import RESULT_STATUS
from .data import ManagerData
from .threads import Threads
from .server import Server
from .db import DataBase

from datetime import datetime as dt
from time import sleep
import atexit
import psutil
import shutil
import json
import sys
import os

class PERMISSIONS:
    ADMIN = 2
    MODERATOR = 1
    USER = 0


class Manager:
    def __init__(self):
        self.__servers_path__ = "servers"
        self.__servers__ = {}
        self.__server_not_found__ = RESULT_STATUS.ERROR, "error/server_not_found", 404

        self.__invalid_token__ = RESULT_STATUS.ERROR, "error/invalid_token", 401
        self.__access_denied__ = RESULT_STATUS.ERROR, "error/access_denied", 403
        self.__invalid_uuid__ = RESULT_STATUS.ERROR, "error/invalid_uuid", 400
        self.__no_token__ = RESULT_STATUS.ERROR, "error/no_token", 401

        self.database = DataBase()
        self.threads = Threads()

        self.__load_servers__()
        self.__data__ = ManagerData()

        self.__data__.reset()
        self.__data__.set("servers/registered", len(self.servers))
        self.__data__.set("servers/registered-private",
                          len([server for server in self.servers.values() if server.private]))

        self.__data__.set("useage/cpu", 0)
        self.__data__.set("useage/ram", 0)
        self.threads.append(self.__update_useage__)()
        
        # Run time 2 days in seconds
        self.__ttl__ = 172800
        # self.__ttl__ = 60 * 3
        self.__ttl_check__ = 60
        self.__startup_timestamp__ = dt.now().timestamp()
        self.threads.append(self.__restart_timer__)()

        atexit.register(self.__close__)
    
    def __ttl_under_check__(self, remaining_ttl=None):
        remaining_ttl =  self.__get_remaining_ttl__() if not remaining_ttl else remaining_ttl
        return remaining_ttl <= self.__ttl_check__
    
    def __get_remaining_ttl__(self):
        current_timestamp = dt.now().timestamp()
        distance = int(current_timestamp - self.__startup_timestamp__)
        remaining_ttl = self.__ttl__ - distance

        return remaining_ttl
    
    def __restart_timer__(self):
        while True:
            remaining_ttl = self.__get_remaining_ttl__()
            
            if self.__ttl_under_check__(remaining_ttl):
                self.__ttl_check__ = 1
            if remaining_ttl in [60, 30, 10, 5, 4, 3, 2, 1]:
                print(f"Restarting in {remaining_ttl} seconds")
                for server in self.__servers__.values():
                    if server.__get_status__() != SERVER_STATUS.RUNNING: continue
                    server.send('tellraw @a ["",{"text":"UwU Servers","bold":true,"color":"dark_purple"},{"text":" » ","color":"dark_gray"},{"text":"Our service will restart in ","color":"gray"},{"text":"%s seconds","bold":true,"color":"gold"},{"text":"!","color":"gray"}]' % remaining_ttl)
                    
                    if remaining_ttl == 60:
                        server.send('tellraw @a ["",{"text":"UwU Servers","bold":true,"color":"dark_purple"},{"text":" » ","color":"dark_gray"},{"text":"Your server will be automatically restarted, once our service is up and running!","color":"dark_green"}]')
            if remaining_ttl <= 0:
                print('Retarting servers...')
                for server in self.__servers__.values():
                    if server.__get_status__()  != SERVER_STATUS.RUNNING: continue
                    server.send('tellraw @a ["",{"text":"UwU Servers","bold":true,"color":"dark_purple"},{"text":" » ","color":"dark_gray"},{"text":"Our service is restarting...","color":"dark_red"}]')
                
                for server in self.__servers__.values():
                    if server.__get_status__()  != SERVER_STATUS.RUNNING: continue
                    print(f"Stopping server {server.uuid}")
                    server.stop()
                    
                    sleep(1)
                    
                    while server.__get_status__() == SERVER_STATUS.RUNNING:
                        sleep(1)
                    
                    print(f"Restarting server {server.uuid}")
                    server.was_online = True
                    server.__write_server_data__()
                
                with open("/root/uwuservers-cdn/service.dat", "w") as file:
                    file.write("restart")
            
            sleep(self.__ttl_check__)

    def __load_servers__(self):
        self.servers = {}

        if os.path.exists(self.__servers_path__):
            servers = os.listdir(self.__servers_path__)

            self.__loop_servers__(servers)

    def __loop_servers__(self, servers):
        for server in servers:
            if not os.path.exists(f"{self.__servers_path__}/{server}"):
                continue
            
            if 'server.json' not in os.listdir(f"{self.__servers_path__}/{server}"):
                print(f"Deleting server {server}")
                shutil.rmtree(f"{self.__servers_path__}/{server}")
                continue
            
            print(f"Loading server {server}")

            with open(f"{self.__servers_path__}/{server}/server.json", "r") as file:
                data = json.load(file)

                uuid = data["uuid"] if "uuid" in data else None
                name = data["name"] if "name" in data else None
                type = data["type"] if "type" in data else None
                version = data["version"] if "version" in data else None
                private = data["private"] if "private" in data else True
                was_online = data["was_online"] if "was_online" in data else False
                
                if server != uuid:
                    uuid = server

                server = Server(uuid, name, type, version, private)
                server.__write_server_data__()
                server.__write_property__("server-port", -1)

                self.__add_server__(data["uuid"], server)
                
                if was_online:
                    print(f"Restarting server {server.uuid}")
                    server.run()

    def __update_useage__(self):
        while True:
            try:
                cpu_useage = psutil.cpu_percent(interval=1)
                ram_useage = psutil.virtual_memory().percent

                self.__data__.set("useage/cpu", cpu_useage)
                self.__data__.set("useage/ram", ram_useage)

            except psutil.NoSuchProcess:
                print("Process terminated")
                break

            except Exception as e:
                print(f"Error occurred while monitoring server: {e}")

            sleep(30)

    def __fetch_server__(self, uuid: str):
        if uuid not in self.__servers__:
            return None

        return self.__servers__[uuid]

    def __add_server__(self, uuid: str, server: Server):
        self.__servers__[uuid] = server

    def __remove_server__(self, uuid: str):
        del self.__servers__[uuid]

    def GET_data(self):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        return RESULT_STATUS.SUCCESS, self.__data__.get_all(), 200

    def GET_public_servers(self):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        servers = {}

        for uuid, server in self.__servers__.items():
            if server.private or server.__get_status__() != SERVER_STATUS.RUNNING:
                continue
            servers[uuid] = server.get_details()

        return RESULT_STATUS.SUCCESS, servers, 200

    def GET_server(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return RESULT_STATUS.SUCCESS, server.get_details(), 200

    def POST_server(self, params: dict, token, data: dict):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        type, version, private = data["type"], data["version"], data["private"]
        
        if uuid in self.__servers__:
            return RESULT_STATUS.ERROR, "error/server_exists", 400

        name = self.database.get_user_name(uuid)
        if not name:
            return self.__invalid_uuid__

        server = Server(uuid, name, type, version, private)
        result = server.create()
        
        if result[0] != RESULT_STATUS.ERROR:
            self.__add_server__(uuid, server)
        
        return result
        

    def DELETE_server(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        result = server.delete()
        
        if result[0] != RESULT_STATUS.ERROR:
            self.__remove_server__(uuid)

        return result

    def POST_server_start(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.run()

    def POST_server_stop(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.stop()
    
    def POST_server_restart(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.restart()

    def GET_server_log(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.get_log()

    def GET_server_log_line(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid, line = params["uuid"], int(params["line"])

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.get_log_line(line)

    def DELETE_server_log(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.clear_logs()

    def POST_server_command(self, params: dict, token, data: dict):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        command = data["command"]
        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.send(command)

    def POST_server_private(self, params: dict, token, data: dict):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        private = data["private"]
        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.set_private(private)

    def POST_server_upgrade(self, params: dict, token, data: dict):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        type, version = data["type"], data["version"]
        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.upgrade(type, version)

    def GET_server_properties(self, params: dict, token):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.get_properties()

    def POST_server_properties(self, params: dict, token, data: dict):
        if self.__ttl_under_check__():
            return RESULT_STATUS.ERROR, "error/service_is_restarting", 503
        
        uuid = params["uuid"]

        result = self.__check_token__(token, uuid)
        if result:
            return result

        properties = data["properties"]
        server = self.__fetch_server__(uuid)

        if not server:
            return self.__server_not_found__

        return server.change_properties(properties)

    def __check_token__(self, token, uuid):
        if not token:
            return self.__no_token__

        userData = self.database.get_user_by_token(token)

        if not userData:
            return self.__invalid_token__

        user = userData["user"]

        if user["uuid"] != uuid and PERMISSIONS.ADMIN not in user["permissions"]:
            return self.__access_denied__

        return None

    def __close__(self):
        for uuid, server in self.__servers__.items():
            print(f"Stopping server {uuid}")
            server.stop()
            server.kill()

    def __stop__(self):
        exit(0)
        non_exist_stop()