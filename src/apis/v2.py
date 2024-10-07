from ..result import process_request, result
from .ipRatelimit import ratelimit
from flask import request

class V2:
    def __init__(self, manager, app):
        self.uri = '/api/v2/'
        self.ratelimit = ratelimit()
        
        # Get every server that private is False
        @app.route(self.get_uri('public-servers'), methods=["GET"])
        @app.route(self.get_uri('public-servers/'), methods=["GET"])
        def get_servers():
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.GET_public_servers, {}, [])
        
        # Get all data from a server
        @app.route(self.get_uri('server/<uuid>'), methods=["GET"])
        @app.route(self.get_uri('server/<uuid>/'), methods=["GET"])
        def get_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.GET_server, {"uuid": uuid}, [])
        
        # Create a new server
        @app.route(self.get_uri('server/<uuid>'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/'), methods=["POST"])
        def create_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server, {"uuid": uuid}, ["type", "version", "private"])
        
        # Delete a server
        @app.route(self.get_uri('server/<uuid>'), methods=["DELETE"])
        @app.route(self.get_uri('server/<uuid>/'), methods=["DELETE"])
        def delete_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.DELETE_server, {"uuid": uuid}, [])
        
        # Start a server
        @app.route(self.get_uri('server/<uuid>/start'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/start/'), methods=["POST"])
        def start_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_start, {"uuid": uuid}, [])
        
        # Stop a server
        @app.route(self.get_uri('server/<uuid>/stop'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/stop/'), methods=["POST"])
        def stop_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_stop, {"uuid": uuid}, [])
        
        # Restart a server
        @app.route(self.get_uri('server/<uuid>/restart'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/restart/'), methods=["POST"])
        def restart_server(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_restart, {"uuid": uuid}, [])
        
        # Clear the log of a server
        @app.route(self.get_uri('server/<uuid>/log'), methods=["DELETE"])
        @app.route(self.get_uri('server/<uuid>/log/'), methods=["DELETE"])
        def clear_server_log(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.DELETE_server_log, {"uuid": uuid}, [])
        
        # Get the log from a server
        @app.route(self.get_uri('server/<uuid>/log'), methods=["GET"])
        @app.route(self.get_uri('server/<uuid>/log/'), methods=["GET"])
        def get_server_log(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.GET_server_log, {"uuid": uuid}, [])
        
        # Get a specific line from the log of a server
        @app.route(self.get_uri('server/<uuid>/log/<line>'), methods=["GET"])
        @app.route(self.get_uri('server/<uuid>/log/<line>/'), methods=["GET"])
        def get_server_log_line(uuid=None, line=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.GET_server_log_line, {"uuid": uuid, "line": line}, [])
        
        # Send a command to a server
        @app.route(self.get_uri('server/<uuid>/command'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/command/'), methods=["POST"])
        def send_server_command(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_command, {"uuid": uuid}, ["command"])
        
        # Set the private status of a server
        @app.route(self.get_uri('server/<uuid>/private'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/private/'), methods=["POST"])
        def set_private(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_private, {"uuid": uuid}, ["private"])
        
        # Upgrade the server
        @app.route(self.get_uri('server/<uuid>/upgrade'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/upgrade/'), methods=["POST"])
        def change_data(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_upgrade, {"uuid": uuid}, ["type", "version"])
        
        # Get server properties
        @app.route(self.get_uri('server/<uuid>/properties'), methods=["GET"])
        @app.route(self.get_uri('server/<uuid>/properties/'), methods=["GET"])
        def get_server_properties(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.GET_server_properties, {"uuid": uuid}, [])
        
        # Change the properties of a server
        @app.route(self.get_uri('server/<uuid>/properties'), methods=["POST"])
        @app.route(self.get_uri('server/<uuid>/properties/'), methods=["POST"])
        def change_server_properties(uuid=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return process_request(manager.POST_server_properties, {"uuid": uuid}, ["properties"])
        
        # Get manager data
        @app.route(self.get_uri(), methods=["GET", "POST", "PUT", "DELETE"])
        @app.route(self.get_uri("<first>"), methods=["GET", "POST", "PUT", "DELETE"])
        @app.route(self.get_uri("<first>/<path:rest>"), methods=["GET", "POST", "PUT", "DELETE"])
        def get_data(first=None, rest=None):
            ip = request.remote_addr
            if not self.ratelimit.check_ip(ip):
                return result({"error": "error/rate_limit_exceeded"}, 429)
            return result(manager.GET_data())
    
    def get_uri(self, route=''):
        return self.uri + route