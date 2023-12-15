import cgi
import time
import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler

tasklist = ['Task 1', 'Task 2', 'Task 3']

HOST = "127.0.0.1"
PORT = 9001


class HTTP10RequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            output = ''
            output += '<html><head><style>'
            output += 'body { font-family: Arial, sans-serif; margin: 20px; }'
            output += 'h1 { color: #333; }'
            output += 'a { color: #007BFF; text-decoration: none; margin-right: 10px; }'
            output += 'a:hover { text-decoration: underline; }'
            output += '</style></head><body>'
            output += '<h1>Welcome to the Task List App</h1>'
            output += '<p>Visit the <a href="/tasklist">Task List</a> to view or manage tasks.</p>'
            output += '</body></html>'

            self.wfile.write(output.encode())
        if self.path.endswith('/tasklist'):
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            output = ''
            output += '<html><head><style>'
            output += 'body { font-family: Arial, sans-serif; margin: 20px; }'
            output += 'h1 { color: #333; }'
            output += 'a { color: #007BFF; text-decoration: none; margin-right: 10px; }'
            output += 'a:hover { text-decoration: underline; }'
            output += '.task { margin-bottom: 10px; }'
            output += '</style></head><body>'
            output += '<h1>Task List</h1>'
            output += ('<h3><a href="/tasklist/new">Add New Task</a></h3>')
            for task in tasklist:
                output += '<div class="task">'
                output += f'{task} <a href="/tasklist/{task}/remove">X</a>'
                output += '</div>'
            output += '</body></html>'
            self.wfile.write(output.encode())
        if self.path.endswith('/new'):
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            output = ''
            output += '<html><head><style>'
            output += 'body { font-family: Arial, sans-serif; margin: 20px; }'
            output += 'h1 { color: #333; }'
            output += 'form { margin-top: 20px; }'
            output += 'input[type="text"] { padding: 5px; margin-right: 10px; }'
            output += 'input[type="submit"] { padding: 5px 10px; background-color: #007BFF; color: #fff; border: none; cursor: pointer; }'
            output += '</style></head><body>'
            output += '<h1>Add New Task</h1>'
            output += '<form method="POST" enctype="multipart/form-data" action="/tasklist/new">'
            output += '<input name="task" type="text" placeholder="Add new task">'
            output += '<input type="submit" value="Add">'
            output += '</form>'
            output += '</body></html>'

            self.wfile.write(output.encode())

        if self.path.endswith('/remove'):
            listIDPath = self.path.split('/')[2]
            print(listIDPath)
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            output = ''
            output += '<html><head><style>'
            output += 'body { font-family: Arial, sans-serif; margin: 20px; }'
            output += 'h1 { color: #333; }'
            output += 'form { margin-top: 20px; }'
            output += 'input[type="submit"] { padding: 5px 10px; background-color: #007BFF; color: #fff; border: none; cursor: pointer; }'
            output += 'a { color: #007BFF; text-decoration: none; margin-right: 10px; }'
            output += 'a:hover { text-decoration: underline; }'
            output += '</style></head><body>'
            output += '<h1>Remove task: %s</h1>' % listIDPath.replace('%20', ' ')
            output += '<form method="POST" enctype="multipart/form-data" action="/tasklist/%s/remove">' % listIDPath
            output += '<input type="submit" value="Remove">'
            output += '<a href="/tasklist">Cancel</a>'
            output += '</body></html>'

            self.wfile.write(output.encode())

    def do_POST(self):
        if self.path.endswith('/new'):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            content_len = int(self.headers.get('Content-length'))
            pdict['CONTENT-LENGTH'] = content_len

            if ctype == 'multipart/form-data':
                try:
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    new_task = fields.get('task')
                    print("Received task:", new_task)

                    if new_task:
                        tasklist.append(new_task[0])
                        print("Task added to the list:", new_task[0])
                    else:
                        print("Error: Task data not found in form fields.")

                except Exception as e:
                    print("Error parsing form data:", e)

            self.send_response(301)
            self.send_header('content-type', 'text/html')
            self.send_header('Location', '/tasklist')
            self.end_headers()

        if self.path.endswith('/remove'):
            listIDPath = self.path.split('/')[2]
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                list_item = listIDPath.replace('%20', ' ')
                tasklist.remove(list_item)

            self.send_response(301)
            self.send_header('content-type', 'text/html')
            self.send_header('Location', '/tasklist')
            self.end_headers()

    def do_DELETE(self):
        listIDPath = self.path.split('/')[2]
        list_item = listIDPath.replace('%20', ' ')

        if list_item in tasklist:
            tasklist.remove(list_item)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(f'Task {list_item} removed successfully', 'utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(f'Task {list_item} not found', 'utf-8'))

    def do_PUT(self):
        listIDPath = self.path.split('/')[2]
        list_item = listIDPath.replace('%20', ' ')

        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length).decode('utf-8')
        updated_task = urllib.parse.parse_qs(raw_data).get('task', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ''
        output += '<html><head><style>'
        output += 'body { font-family: Arial, sans-serif; margin: 20px; }'
        output += 'h1 { color: #333; }'
        output += 'a { color: #007BFF; text-decoration: none; margin-right: 10px; }'
        output += 'a:hover { text-decoration: underline; }'
        output += '</style></head><body>'

        if list_item in tasklist:
            if updated_task is not None:
                tasklist[tasklist.index(list_item)] = updated_task
                output += f'<h1>Task {list_item} updated to {updated_task} successfully</h1>'
            else:
                output += '<h1>Error: No updated task provided in the request</h1>'
        else:
            output += f'<h1>Error: Task {list_item} not found</h1>'

        output += '<a href="/tasklist">Back to Task List</a>'
        output += '</body></html>'

        self.wfile.write(output.encode())


def main():
    PORT = 9001
    server_address = ('localhost', PORT)
    server = HTTPServer(server_address, HTTP10RequestHandler)
    print(f'Server running on port {PORT} using HTTP/1.0')
    server.serve_forever()


if __name__ == '__main__':
    main()
