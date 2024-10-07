from .server_details import SERVER_TYPE, SERVER_VERSION, SERVER_STATUS, isInstanceOf
from .minecraft_server_api import ServerApi
from .cloudflare import cloudflare
from .result import RESULT_STATUS
from .server_downloader import *
from .server_ports import Ports
from .data import ManagerData
from .threads import Threads
from time import sleep
from .log import Log
from . import modUtil
import subprocess
import datetime
import pathlib
import psutil
import shutil
import json
import sys
import os
import re

class Server:
    def __init__(self, uuid: str, name: str, type: SERVER_TYPE, version: SERVER_VERSION, private: bool = True):
        self.uuid = uuid
        self.name = name
        self.type = type
        self.version = version
        self.port = -1
        self.private = private
        self.was_online = False

        self.servers_path = "X:\\.projects\\uwuservers\\uwuservers-cdn\\servers\\" if sys.platform == "win32" else "/root/uwuservers-cdn/servers/"
        self.start_file = [
            "start.bat"] if sys.platform == "win32" else ["./start.sh"]

        self.threads = Threads()
        self.ports = Ports()
        self.manager_data = ManagerData()
        self.server_api = ServerApi()

        self.server = None
        self.stdout = None
        self.stdin = None
        self.stderr = None
        self.pid = None

        self.startet_at_timestamp = None
        self.stopped_at_timestamp = None
        
        self.restarting = False
        self.stopping = False
        self.starting = False

        self.path = f"servers/{uuid}/"

        self.log = Log(f"{self.path}")
        self.log_file = None

    def __get_status__(self):
        if self.stderr is not None:
            return SERVER_STATUS.ERROR

        if self.starting:
            return SERVER_STATUS.STARTING
        
        if self.stopping:
            return SERVER_STATUS.STOPPING
        
        if self.restarting:
            return SERVER_STATUS.RESTARTING

        if self.server is None or self.server.poll() is not None:
            return SERVER_STATUS.STOPPED

        if self.server.poll() is None:
            return SERVER_STATUS.RUNNING

        return SERVER_STATUS.UNKNOWN

    def __close_file__(self, check=False):
        if self.log_file is None or check and self.__get_status__() == SERVER_STATUS.RUNNING:
            return

        self.log_file.close()
        self.log_file = None

    def __write_server_data__(self):
        data = self.get_details()
        data["was_online"] = self.was_online

        with open(f"{self.path}server.json", "w") as f:
            data_string = json.dumps(data)
            f.write(data_string)

    def create(self):
        if not isInstanceOf(self.version, SERVER_VERSION):
            return RESULT_STATUS.ERROR, "error/invalid_version", 400

        if not isInstanceOf(self.type, SERVER_TYPE):
            return RESULT_STATUS.ERROR, "error/invalid_type", 400

        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)

        try:
            pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)

            download_server(self.path, self.type, self.version)

            self.__write_property__(
                "motd", '§8Server hosted by §5§luwuservers.com§r§8!§r                    §9Create your own §b§lfree§r§9 server now!')
            self.__write_server_data__()

            # Set server owner op in ops.json
            with open(f"{self.path}ops.json", "w") as f:
                f.write('[{"uuid": "%s", "name": "%s", "level": 4, "bypassesPlayerLimit": false}]' % (
                    self.uuid, self.name))

            if sys.platform != "win32":
                subprocess.run(["chmod", "+x", f"{self.path}start.sh"])

            self.manager_data.increment("servers/registered")
            return RESULT_STATUS.SUCCESS, self.get_details(), 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def run(self, internal=False):
        if not internal and self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400  
        if not internal and self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if not internal and self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if not internal and self.__get_status__() in [SERVER_STATUS.RUNNING, SERVER_STATUS.STARTING]:
            return RESULT_STATUS.ERROR, "error/running", 400
        
        self.starting = True
        self.port = self.ports.add_random_port()

        if self.port is None:
            self.starting = False
            return RESULT_STATUS.ERROR, "error/no_ports_available", 400

        self.__write_server_data__()
        self.__write_property__("server-port", self.port)

        try:
            self.clear_logs()
            self.threads.append(self.__run_server__)()

            self.manager_data.increment("servers/running")

            if self.private:
                self.manager_data.increment("servers/running-private")
            
            sleep(1)

            self.starting = False
            return RESULT_STATUS.SUCCESS, self.get_details(), 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def __run_server__(self):
        self.__reset_server_stats__()

        self.log_file = open(f"{self.path}console.log", "w+")

        self.server = subprocess.Popen(self.start_file,
                                       cwd=f'{self.servers_path}{self.uuid}',
                                       stdout=self.log_file,
                                       stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)

        self.stdout = self.server.stdout
        self.stdin = self.server.stdin
        self.stderr = self.server.stderr
        self.pid = self.server.pid

        self.startet_at_timestamp = datetime.datetime.now().timestamp()

        while self.__get_status__() in [SERVER_STATUS.RUNNING, SERVER_STATUS.STARTING, SERVER_STATUS.STOPPING]:
            sleep(1)

        self.ports.remove_port(self.port)
        self.port = -1
        self.__write_server_data__()
        self.__write_property__("server-port", self.port)

        self.kill()
        self.server = None
        self.stopped_at_timestamp = datetime.datetime.now().timestamp()

        self.manager_data.decrement("servers/running")

        if self.private:
            self.manager_data.decrement("servers/running-private")

    def send(self, command: str, internal=False):
        if not internal and self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400   
        if not internal and self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if not internal and self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if not internal and self.__get_status__() != SERVER_STATUS.RUNNING:
            return RESULT_STATUS.ERROR, "error/stopped", 400

        try:
            self.stdin.write(command + '\n')
            self.stdin.flush()
            return RESULT_STATUS.SUCCESS, command, 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def restart(self):
        if self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400 
        if self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if self.__get_status__() in [SERVER_STATUS.STOPPED, SERVER_STATUS.STOPPING, SERVER_STATUS.ERROR, SERVER_STATUS.UNKNOWN]:
            return RESULT_STATUS.ERROR, "error/stopped", 400
        
        self.restarting = True

        try:
            self.stop(True)
            
            sleep(2)
            while self.server and self.server.poll is None or self.port != -1:
                sleep(2)
            self.restarting = False
            self.starting = True
            sleep(1)
            
            self.run(True)
            
            sleep(2)
            self.starting = False
            return RESULT_STATUS.SUCCESS, self.get_details(), 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def stop(self, internal=False):
        if not internal and self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400   
        if not internal and self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if not internal and self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if not internal and self.__get_status__() == SERVER_STATUS.STOPPED:
            return RESULT_STATUS.ERROR, "error/stopped", 400
        
        self.stopping = True

        try:
            self.send("stop", True)
            sleep(3)
            
            self.stopping = False
            return RESULT_STATUS.SUCCESS, self.get_details(), 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def kill(self):
        try:
            psutil.Process(self.pid).kill()
        except:
            pass

    def delete(self):
        self.manager_data.decrement("servers/registered")
        self.stop()

        try:
            self.clear_logs()
            shutil.rmtree(self.path)
            return RESULT_STATUS.SUCCESS, self.uuid, 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def get_log(self):
        try:
            result = self.log.read_all_limited()

            if result is None:
                return RESULT_STATUS.ERROR, "error/log_not_found", 404

            return RESULT_STATUS.SUCCESS, result, 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def get_log_line(self, int: int):
        try:
            result = self.log.read(int)

            if result is None:
                return RESULT_STATUS.ERROR, "error/log_not_found", 404

            return RESULT_STATUS.SUCCESS, result, 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def clear_logs(self):
        if self.__get_status__() == SERVER_STATUS.RUNNING:
            return RESULT_STATUS.ERROR, "error/running", 400

        try:
            self.__close_file__(True)

            success = self.log.clear()

            if not success:
                return RESULT_STATUS.ERROR, "error/log_not_found", 404

            return RESULT_STATUS.SUCCESS, self.get_details(), 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500
        
    def __get_folder_contents__(self, folder: str):
        if not os.path.isdir(f"{self.path}{folder}"):
            return None
        return os.listdir(f"{self.path}{folder}")
    
    def __parse_mods_data__(self, mods: str):
        files = self.__get_folder_contents__(mods)
        if files is None: return None
        return modUtil.parse(files)

    def __get_server_stats__(self):
        return {
            "startet_at_timestamp": self.startet_at_timestamp,
            "stopped_at_timestamp": self.stopped_at_timestamp,
            "server_data": self.server_api.request(self.port, self.__get_status__() == SERVER_STATUS.RUNNING),
            "status": self.__get_status__(),
            "mods": self.__get_folder_contents__("mods"),
            "plugins": self.__get_folder_contents__("plugins"),
        }

    def __reset_server_stats__(self):
        self.startet_at_timestamp = None
        self.stopped_at_timestamp = None

    def get_details(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "private": self.private,
            "stats": self.__get_server_stats__(),
            "port": self.port
        }

    def set_private(self, private: bool):
        self.private = private
        self.__write_server_data__()

        if private and self.__get_status__() == SERVER_STATUS.RUNNING:
            self.manager_data.increment("servers/running-private")
        elif not private and self.__get_status__() == SERVER_STATUS.RUNNING:
            self.manager_data.decrement("servers/running-private")

        return RESULT_STATUS.SUCCESS, self.get_details(), 200

    def upgrade(self, type: SERVER_TYPE = None, version: SERVER_VERSION = None):
        if self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400   
        if self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if self.__get_status__() == SERVER_STATUS.RUNNING:
            return RESULT_STATUS.ERROR, "error/running", 400

        if type is None and version is None or type == self.type and version == self.version:
            return RESULT_STATUS.ERROR, "error/no_changes_could_be_made", 400

        if type is not None and not isInstanceOf(type, SERVER_TYPE):
            return RESULT_STATUS.ERROR, "error/invalid_type", 400

        if version is not None and not isInstanceOf(version, SERVER_VERSION):
            return RESULT_STATUS.ERROR, "error/invalid_version", 400

        files = os.listdir(self.path)

        for file in files:
            if re.match(r".+\.jar", file) or re.match(r".+\.properties", file) or file in ["user_jvm_args.txt", "libraries"]:
                if os.path.isdir(f"{self.path}{file}"):
                    shutil.rmtree(f"{self.path}{file}")
                else:
                    os.remove(f"{self.path}{file}")

        self.type = type if type is not None else self.type
        self.version = version if version is not None else self.version

        download_server(self.path, self.type, self.version)

        self.__write_server_data__()

        if sys.platform != "win32":
            subprocess.run(["chmod", "+x", f"{self.path}start.sh"])

        return RESULT_STATUS.SUCCESS, self.get_details(), 200

    def allowed_properties(self):
        return [
            "allow-flight",
            "allow-nether",
            "difficulty",
            "enable-command-block",
            "enforce-whitelist",
            "force-gamemode",
            "gamemode",
            "generate-structures",
            "generator-settings",
            "hardcore",
            "hide-online-players",
            "level-name",
            "level-seed",
            "level-type",
            "max-players",
            "max-world-size",
            "motd",
            "online-mode",
            "op-permission-level",
            "player-idle-timeout",
            "pvp",
            "resource-pack",
            "resource-pack-sha1",
            "spawn-animals",
            "spawn-monsters",
            "spawn-npcs",
            "spawn-protection",
            "view-distance",
            "white-list",
        ]

    def get_properties(self):
        try:
            with open(f"{self.path}server.properties", "r") as f:
                lines = f.readlines()

            properties = {}

            for line in lines:
                if line.startswith("#"):
                    continue

                key, value = line.split("=")
                if key in self.allowed_properties():
                    value = value.replace("\n", "")

                    if value in ["true", "false"]:
                        value = True if value == "true" else False
                    elif value.isdigit():
                        value = int(value)

                    properties[key] = value

            return RESULT_STATUS.SUCCESS, properties, 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def change_properties(self, properties: dict):
        if self.starting:
            return RESULT_STATUS.ERROR, "error/starting", 400   
        if self.restarting:
            return RESULT_STATUS.ERROR, "error/restarting", 400
        if self.stopping:
            return RESULT_STATUS.ERROR, "error/stopping", 400
        
        if self.__get_status__() == SERVER_STATUS.RUNNING:
            return RESULT_STATUS.ERROR, "error/running", 400

        try:
            # Read the file with cp1252 encoding
            with open(f"{self.path}server.properties", "r", encoding='cp1252', errors='replace') as f:
                content = f.read()

            # Process each property
            for key, value in properties.items():
                if key not in self.allowed_properties():
                    return RESULT_STATUS.ERROR, f"error/property_not_allowed/{key}", 400

                if key not in content:
                    return RESULT_STATUS.ERROR, f"error/property_not_found/{key}", 404

                # Write the property with its new value
                self.__write_property__(key, value)

            return RESULT_STATUS.SUCCESS, self.get_properties()[1], 200
        except Exception as e:
            return RESULT_STATUS.ERROR, str(e), 500

    def __write_property__(self, key: str, value: str):
        try:
            # Read the file with cp1252 encoding
            with open(f"{self.path}server.properties", "r", encoding='cp1252', errors='replace') as f:
                content = f.read()

            # Modify content
            pattern = re.compile(rf'^{re.escape(key)}=.*$', re.MULTILINE)
            if pattern.search(content):
                content = pattern.sub(f'{key}={value}', content)
            else:
                content += f'\n{key}={value}'

            # Write the file with cp1252 encoding
            with open(f"{self.path}server.properties", "w", encoding='cp1252', errors='replace') as f:
                f.write(content.strip())
            
        except Exception as e:
            str(e)
