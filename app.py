from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse, parse_qs
from todo import TodoManager

todo_manager = TodoManager()

class RequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the TODO application.
    """

    def _send_response(self, response, status=200):
        """
        Send a JSON response to the client.

        :param response: The response data to be sent.
        :param status: The HTTP status code (default is 200).
        """
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def _serve_static_file(self, path):
        """
        Serve a static file to the client.

        :param path: The path to the static file.
        """
        try:
            with open(path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-Type', self._get_content_type(path))
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, 'File Not Found')

    def _get_content_type(self, path):
        """
        Determine the content type based on the file extension.

        :param path: The path to the file.
        :return: The content type as a string.
        """
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        return 'application/octet-stream'

    def do_GET(self):
        """
        Handle GET requests.
        """
        parsed_path = urlparse(self.path)
        if (parsed_path.path == '/'):
            self._serve_static_file('static/index.html')
        elif (parsed_path.path == '/todos'):
            todos = todo_manager.get_todos()
            self._send_response(todos)
        elif parsed_path.path.startswith('/static/'):
            self._serve_static_file(self.path[1:])
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        """
        Handle POST requests.
        """
        if self.path == '/todos':
            length = int(self.headers.get('Content-Length'))
            data = json.loads(self.rfile.read(length))
            todo = todo_manager.add_todo(data['title'], data.get('description', ''))
            self._send_response(todo, 201)
        else:
            self.send_error(404, 'Not Found')

    def do_PUT(self):
        """
        Handle PUT requests.
        """
        if self.path.startswith('/todos/'):
            todo_id = int(self.path.split('/')[-1])
            length = int(self.headers.get('Content-Length'))
            data = json.loads(self.rfile.read(length))
            updated_todo = todo_manager.update_todo(todo_id, data['title'], data.get('description', ''), data.get('done', False))
            if updated_todo:
                self._send_response(updated_todo)
            else:
                self.send_error(404, 'Not Found')
        else:
            self.send_error(404, 'Not Found')

    def do_DELETE(self):
        """
        Handle DELETE requests.
        """
        if self.path.startswith('/todos/'):
            todo_id = int(self.path.split('/')[-1])
            if todo_manager.delete_todo(todo_id):
                self.send_response(204)
                self.end_headers()
            else:
                self.send_error(404, 'Not Found')
        else:
            self.send_error(404, 'Not Found')

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    """
    Run the HTTP server.

    :param server_class: The HTTP server class (default is HTTPServer).
    :param handler_class: The request handler class (default is RequestHandler).
    :param port: The port to bind the server to (default is 8000).
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
