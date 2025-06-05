#!/usr/bin/env python3
"""
Simple HTMX + Supabase File Upload Example
The HTMX-preferred way: minimal, hypermedia-driven
"""

from flask import Flask, request, render_template_string
from supabase import create_client
import os

app = Flask(__name__)

# Simple Supabase setup
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# Simple HTML template - pure HTMX style
SIMPLE_UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <title>Simple HTMX + Supabase Upload</title>
</head>
<body>
    <h1>Simple File Upload</h1>
    
    <!-- This is all HTMX needs for file upload -->
    <form hx-post="/upload" 
          hx-encoding="multipart/form-data" 
          hx-target="#result">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>
    
    <!-- Results appear here -->
    <div id="result"></div>
</body>
</html>
"""

# Simple success template
SUCCESS_TEMPLATE = """
<div style="color: green; padding: 10px; border: 1px solid green;">
    ✅ File uploaded successfully!<br>
    <a href="{{url}}" target="_blank">View file</a>
</div>
"""

# Simple error template  
ERROR_TEMPLATE = """
<div style="color: red; padding: 10px; border: 1px solid red;">
    ❌ Upload failed: {{error}}
</div>
"""

@app.route('/')
def index():
    """Serve the simple upload page"""
    return render_template_string(SIMPLE_UPLOAD_PAGE)

@app.route('/upload', methods=['POST'])
def upload():
    """
    Simple HTMX + Supabase upload handler
    The HTMX way: just return HTML fragments
    """
    
    # HTMX approach: minimal validation, maximum simplicity
    if 'file' not in request.files:
        return render_template_string(ERROR_TEMPLATE, error="No file selected")
    
    file = request.files['file']
    if file.filename == '':
        return render_template_string(ERROR_TEMPLATE, error="No file selected")
    
    try:
        # Simple Supabase upload - just the essentials
        file_path = f"uploads/{file.filename}"
        
        # Upload to Supabase Storage (simple version)
        supabase.storage.from_('referrals').upload(
            file_path, 
            file.read()
        )
        
        # Get public URL
        url = supabase.storage.from_('referrals').get_public_url(file_path)
        
        # Return success HTML fragment (HTMX way)
        return render_template_string(SUCCESS_TEMPLATE, url=url)
        
    except Exception as e:
        # Return error HTML fragment (HTMX way)
        return render_template_string(ERROR_TEMPLATE, error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=3002) 