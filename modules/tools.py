import subprocess
import urllib.request
import json

# TOOL 1: The Code Debugger
def execute_python_code(code_string: str) -> str:
    """
    Executes Python code on the local machine and returns the terminal output or errors.
    Use this to test code, debug algorithms, or perform complex math.
    """
    print("\n[Tool Executing]: Running Python Code...")
    try:
        # Save the AI's code to a temporary file
        with open("hermes_temp_sandbox.py", "w", encoding="utf-8") as f:
            f.write(code_string)
            
        # Run the file and capture the terminal output
        result = subprocess.run(["python", "hermes_temp_sandbox.py"], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return f"SUCCESS. Output:\n{result.stdout}"
        else:
            return f"ERROR. Output:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "ERROR: Code execution timed out (took longer than 15 seconds)."
    except Exception as e:
        return f"ERROR: {str(e)}"

# TOOL 2: The Web Scraper
def fetch_web_data(query: str) -> str:
    """
    Searches the web and returns JSON data. Use this when you need up-to-date factual information.
    """
    print(f"\n[Tool Executing]: Searching web for '{query}'...")
    # Using a free, no-key Wikipedia API as a safe starting scraper
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        
        if data.get('query', {}).get('search'):
            snippet = data['query']['search'][0]['snippet']
            # Clean HTML tags
            clean_snippet = snippet.replace('<span class="searchmatch">', '').replace('</span>', '')
            return clean_snippet
        return "No relevant data found on the web."
    except Exception as e:
        return f"Web search failed: {e}"

# List of tools to pass to Gemini
HERMES_TOOLS = [execute_python_code, fetch_web_data]
# ... (Keep your execute_python_code and fetch_web_data functions up here) ...

# TOOL 3: The Social Media Manager
def post_to_instagram(media_path: str, caption: str, is_video: bool = False) -> str:
    """
    Posts a photo or video to the user's Instagram account natively via API.
    Use this tool whenever the user asks to post, upload, or share something to Instagram.
    """
    print(f"\n[Tool Executing]: Connecting to Instagram Servers...")
    
    # ⚠️ ENTER YOUR ACTUAL INSTAGRAM LOGIN HERE ⚠️
    IG_USERNAME = "your_username_here"
    IG_PASSWORD = "your_password_here"

    if IG_USERNAME == "your_username_here":
        return "ERROR: Sir, you have not configured your Instagram credentials in tools.py yet."

    try:
        # Import inside the function so it doesn't slow down boot times
        from instagrapi import Client
        
        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)
        
        if is_video:
            print("[Tool Executing]: Uploading Video (This may take a minute)...")
            cl.video_upload(media_path, caption)
        else:
            print("[Tool Executing]: Uploading Photo...")
            cl.photo_upload(media_path, caption)
            
        return "SUCCESS: The media was successfully posted to Instagram, Sir."
    
    except ImportError:
        return "ERROR: The 'instagrapi' library is not installed. Please run 'pip install instagrapi'."
    except Exception as e:
        return f"ERROR posting to Instagram: {str(e)}"

# IMPORTANT: Add the new tool to the list!
HERMES_TOOLS = [execute_python_code, fetch_web_data, post_to_instagram]