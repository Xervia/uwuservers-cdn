from .server_details import SERVER_TYPE
import pathlib
import requests
import re
import paramiko
import os

global TIMEMOUT
TIMEMOUT = 10

def download_server(path: str, type: str, version: str):
    print(f"Downloading {type} server with version {version}")

    if type == SERVER_TYPE.VANILLA:
        VanillaServerDownloader(version, path)
    elif type == SERVER_TYPE.FORGE:
        ForgeServerDownloader(version, path)


def write_file(path: str, content: str):
    with open(path, "w", encoding='cp1252', errors='replace') as file:
        file.write(content)


class VanillaServerDownloader:
    def __init__(self, version: str, path: str):
        self.versions_url = f"https://mcversions.net/download/{version}"

        jar_url = None

        session, request = self.create_session()

        html = request.text
        links = re.findall(r'href=[\'"]?([^\'" >]+)', html)

        for link in links:
            if link.endswith("server.jar"):
                jar_url = link
                break
            
        print(f"Downloading server from {jar_url}")

        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        with open(f"{path}server.jar", "wb") as file:
            file.write(session.get(jar_url).content)

        session.close()

        write_file(f"{path}server.properties", "allow-flight=true\nserver-port=-1\nmotd=§8Server hostet by §5§luwuservers.com§r§8!§r                    §9Create your own §b§lfree§r§9 server now!")
        write_file(f"{path}eula.txt", "eula=true")
        write_file(f"{path}start.bat", f"@echo off\njava -Xms1024M -Xmx1024M -jar server.jar nogui")
        write_file(f"{path}start.sh", f"java -Xms1024M -Xmx1024M -jar server.jar nogui")

    def create_session(self):
        session = requests.Session()
        request = session.get(self.versions_url, timeout=TIMEMOUT)

        return session, request


class ForgeServerDownloader:
    def __init__(self, version: str, path: str):
        source = f"uwuservers-mirror/forge/{version}"
        target = path

        _host = "217.72.195.219"
        _port = 22
        username = "root"
        password = "QwEQwEQwE1"

        connection = paramiko.Transport((_host, _port))
        connection.connect(username=username, password=password)
        
        self.sftp = paramiko.SFTPClient.from_transport(connection)
        
        self.put_dir(source, target)
        print("Finished copying %s to %s" % (source, target))

        write_file(f"{path}server.properties", "allow-flight=true\nserver-port=-1\nmotd=§8Server hostet by §5§luwuservers.com§r§8!§r                    §9Create your own §b§lfree§r§9 server now!")
        
    def isFile(self, source, item):
        try:
            self.sftp.listdir('%s/%s' % (source, item))
            return False
        except:
            return True
    
    def put_dir(self, source, target):
        print("Downloading files from %s to %s" % (source, target))
        
        for item in self.sftp.listdir(source):
            print("Checking %s" % item)
                
            if self.isFile(source, item):
                print("Copying file %s" % item)
                
                self.sftp.get('%s/%s' % (source, item), '%s/%s' % (target, item))
            else:
                print("Copying directory %s" % item)
                
                if not os.path.exists('%s/%s' % (target, item)):
                    os.mkdir('%s/%s' % (target, item))
                    
                self.put_dir('%s/%s' % (source, item), '%s/%s' % (target, item))