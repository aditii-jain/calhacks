from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# Add the parent backend directory to Python path to import config and supabase
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_path)  # Insert at beginning to prioritize our config

try:
    # Import our backend config specifically
    import config
    from supabase import create_client
    settings = config.settings
    SUPABASE_AVAILABLE = True
    print("✅ Supabase integration available")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    print(f"⚠️  Supabase not available: {e}")
    print("   Falling back to JSON-only storage")
    settings = None

class PostsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Initialize Supabase client if available
        self.supabase_client = None
        if SUPABASE_AVAILABLE and settings and hasattr(settings, 'supabase_url') and hasattr(settings, 'supabase_service_key'):
            if settings.supabase_url and settings.supabase_service_key:
                try:
                    # Use minimal options to avoid compatibility issues
                    self.supabase_client = create_client(
                        settings.supabase_url, 
                        settings.supabase_service_key
                    )
                    print("✅ Supabase client initialized in server")
                except Exception as e:
                    print(f"⚠️  Failed to initialize Supabase client: {e}")
                    self.supabase_client = None
        
        super().__init__(*args, **kwargs)

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
        elif self.path == '/get-posts':
            # Fetch posts from database
            self._handle_get_posts()
            return
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def _handle_get_posts(self):
        """Handle GET request for fetching posts from database"""
        try:
            # Try to get posts from Supabase first
            posts_from_db = self._get_posts_from_supabase()
            
            # If Supabase fails, fall back to local JSON
            if not posts_from_db:
                posts_from_db = self._get_posts_from_json()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'posts': posts_from_db,
                'total_count': len(posts_from_db),
                'source': 'supabase' if self.supabase_client and posts_from_db else 'local_json'
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"❌ Error fetching posts: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'status': 'error',
                'message': 'Failed to fetch posts',
                'posts': [],
                'total_count': 0
            }
            
            self.wfile.write(json.dumps(error_response).encode())

    def _get_posts_from_supabase(self):
        """Fetch posts from Supabase database"""
        if not self.supabase_client:
            print("⚠️  Supabase client not available for fetching posts")
            return []
        
        try:
            # Fetch all posts ordered by timestamp (newest first)
            response = self.supabase_client.table('mock_twitter_posts').select('*').order('timestamp', desc=True).execute()
            
            if response.data:
                print(f"✅ Fetched {len(response.data)} posts from Supabase")
                # Convert database format to frontend format
                posts = []
                for db_post in response.data:
                    post = {
                        'text': db_post.get('text', ''),
                        'image': db_post.get('image'),
                        'timestamp': db_post.get('timestamp', ''),
                        'location': None  # Extract location from text if needed
                    }
                    posts.append(post)
                return posts
            else:
                print("📭 No posts found in Supabase")
                return []
                
        except Exception as e:
            print(f"❌ Failed to fetch from Supabase: {e}")
            return []

    def _get_posts_from_json(self):
        """Fetch posts from local JSON file (fallback)"""
        try:
            posts_file = 'posts.json'
            if os.path.exists(posts_file):
                with open(posts_file, 'r') as f:
                    all_posts = json.load(f)
                
                posts = all_posts.get('posts', [])
                # Sort by timestamp (newest first)
                posts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                print(f"✅ Fetched {len(posts)} posts from local JSON")
                return posts
            else:
                print("📭 No local JSON file found")
                return []
                
        except Exception as e:
            print(f"❌ Failed to fetch from JSON: {e}")
            return []

    def do_POST(self):
        if self.path == '/save-post':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            # Enhanced storage: Save to Supabase first, then local JSON as backup
            success_supabase = self._save_to_supabase(post_data)
            success_json = self._save_to_json(post_data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'storage': {
                    'supabase': success_supabase,
                    'local_json': success_json
                },
                'message': self._get_storage_message(success_supabase, success_json)
            }
            
            self.wfile.write(json.dumps(response).encode())
            return

        return SimpleHTTPRequestHandler.do_POST(self)
    
    def _save_to_supabase(self, post_data):
        """Save post to Supabase database"""
        if not self.supabase_client:
            print("⚠️  Supabase client not available, skipping database save")
            return False
        
        try:
            # Prepare data for Supabase
            db_record = {
                'text': post_data.get('text', ''),
                'image': post_data.get('image'),  # Can be None
                'timestamp': post_data.get('timestamp', datetime.now().isoformat())
            }
            
            # Insert into mock_twitter_posts table
            response = self.supabase_client.table('mock_twitter_posts').insert(db_record).execute()
            
            if response.data:
                print(f"✅ Post saved to Supabase: ID {response.data[0].get('id', 'unknown')}")
                return True
            else:
                print("⚠️  Supabase insert returned no data")
                return False
                
        except Exception as e:
            print(f"❌ Failed to save to Supabase: {e}")
            return False
    
    def _save_to_json(self, post_data):
        """Save post to local JSON file (backup storage)"""
        try:
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
            all_posts['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(posts_file, 'w') as f:
                json.dump(all_posts, f, indent=2)
            
            print("✅ Post saved to local JSON file")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save to JSON: {e}")
            return False
    
    def _get_storage_message(self, supabase_success, json_success):
        """Generate appropriate message based on storage results"""
        if supabase_success and json_success:
            return "Post saved to both Supabase and local JSON"
        elif supabase_success:
            return "Post saved to Supabase (local JSON failed)"
        elif json_success:
            return "Post saved to local JSON only (Supabase unavailable)"
        else:
            return "Failed to save post to any storage"

if __name__ == '__main__':
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n🚨 Mock Twitter Server with Supabase Integration")
    print("=" * 50)
    
    # Initialize posts.json file if it doesn't exist (but don't reset existing data)
    posts_file = 'posts.json'
    if not os.path.exists(posts_file):
        initial_posts = {
            'metadata': {
                'total_posts': 0,
                'last_updated': None,
                'server_started': datetime.now().isoformat()
            },
            'posts': []
        }
        
        try:
            with open(posts_file, 'w') as f:
                json.dump(initial_posts, f, indent=2)
            print(f"✅ Created initial {posts_file}")
        except Exception as e:
            print(f"⚠️  Could not create {posts_file}: {e}")
    else:
        print(f"📄 Using existing {posts_file} as backup storage")
    
    # Test Supabase connection
    if SUPABASE_AVAILABLE and settings and settings.supabase_url and settings.supabase_service_key:
        try:
            test_client = create_client(
                settings.supabase_url, 
                settings.supabase_service_key
            )
            # Test connection by trying to access the table
            test_response = test_client.table('mock_twitter_posts').select('id').limit(1).execute()
            print("✅ Supabase connection tested successfully")
        except Exception as e:
            print(f"⚠️  Supabase connection test failed: {e}")
            print("   Posts will be saved to JSON only")
    
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PostsHandler)
    print(f"\n🚀 Server running on http://localhost:8000")
    print(f"📁 Current directory: {os.getcwd()}")
    print("📝 Storage: Supabase (primary) + Local JSON (backup)")
    print("\n🔄 Ready to receive posts...\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        httpd.server_close() 