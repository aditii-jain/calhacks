from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

class PostsHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            # Serve the main HTML file
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/save-post':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            # Initialize or load the posts file
            posts_file = 'posts.json'
            if os.path.exists(posts_file):
                with open(posts_file, 'r') as f:
                    all_posts = json.load(f)
            else:
                all_posts = {
                    'metadata': {
                        'total_posts': 0,
                        'last_updated': None
                    },
                    'posts': []
                }
            
            # Add the new post
            all_posts['posts'].append(post_data)
            all_posts['metadata']['total_posts'] = len(all_posts['posts'])
            
            # Save back to file
            with open(posts_file, 'w') as f:
                json.dump(all_posts, f, indent=2)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
            return

        return SimpleHTTPRequestHandler.do_POST(self)

if __name__ == '__main__':
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PostsHandler)
    print('Server running on port 8000...')
    print('Current directory:', os.getcwd())
    httpd.serve_forever() 