from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

# Base directory for the websites folder
WEBSITES_DIR = 'websites'

# Serve the index page (optional if needed)
@app.route('/')
def index():
    return '<h1>Hello mate</h1><p>Append the website name after the slash to view it.</p>'

# Route to serve the requested website files
@app.route('/<path:site_path>')
def serve_site(site_path):
    # Full path to the requested file in the websites folder
    full_path = os.path.join(WEBSITES_DIR, site_path)

    # Check if the file exists
    if os.path.exists(full_path):
        # Serve the file from the websites folder
        return send_from_directory(WEBSITES_DIR, site_path)
    else:
        return '<h1>Website not found</h1>', 404


if __name__ == '__main__':
    app.run(debug=True)