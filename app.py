from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import shutil
from bs4 import BeautifulSoup

app = Flask(__name__)

# Base directory for the websites folder
WEBSITES_DIR = 'websites'

# Log file for processed files
PROCESSED_FILES_LOG = 'processed_files.txt'

# Log file for JavaScript-injected files
JS_INJECTED_FILES_LOG = 'js_injected_files.txt'

# Log file for visit counts
VISIT_COUNTS_LOG = 'visit_counts.txt'

# Functions for processing HTML files
def load_processed_files(log_file):
    """Load the list of already processed files from a log file."""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_processed_file(log_file, filename):
    """Append the newly processed file to the log file."""
    with open(log_file, 'a') as f:
        f.write(filename + '\n')

def remove_file_from_log(log_file, filename):
    """Remove the specified file from the log file."""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
        with open(log_file, 'w') as f:
            for line in lines:
                if line.strip() != filename:
                    f.write(line)

def load_visit_counts():
    """Load visit counts from the log file."""
    visit_counts = {}
    if os.path.exists(VISIT_COUNTS_LOG):
        with open(VISIT_COUNTS_LOG, 'r') as f:
            for line in f:
                name, count = line.strip().split(':')
                visit_counts[name] = int(count)
    return visit_counts

def save_visit_counts(visit_counts):
    """Save visit counts to the log file."""
    with open(VISIT_COUNTS_LOG, 'w') as f:
        for name, count in visit_counts.items():
            f.write(f"{name}:{count}\n")

def increment_visit_count(filename):
    """Increment the visit count for the given filename."""
    visit_counts = load_visit_counts()
    if filename in visit_counts:
        visit_counts[filename] += 1
    else:
        visit_counts[filename] = 1
    save_visit_counts(visit_counts)

def remove_visit_count(filename):
    """Remove the visit count entry for the specified filename."""
    visit_counts = load_visit_counts()
    if filename in visit_counts:
        del visit_counts[filename]
    save_visit_counts(visit_counts)

def remove_href_from_file(html_file):
    """Make HTML static by removing interactive elements."""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Remove href attributes from all <a> tags
    for a_tag in soup.find_all('a', href=True):
        a_tag['href'] = '#'

    # Remove onclick attributes from all elements
    for tag in soup.find_all(onclick=True):
        del tag['onclick']

    # Remove other event attributes like onmouseover, onmouseout, etc.
    event_attributes = ['onmouseover', 'onmouseout', 'onchange', 'onsubmit', 'onload']
    for event in event_attributes:
        for tag in soup.find_all(attrs={event: True}):
            del tag[event]

    # Disable forms by removing the action attribute or setting it to '#'
    for form_tag in soup.find_all('form', action=True):
        form_tag['action'] = '#'

    # Remove all <script> tags to disable JavaScript
    for script_tag in soup.find_all('script'):
        script_tag.decompose()

    # Write the modified HTML back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"Modified HTML saved: {html_file}")

def process_html_file_if_needed(file_path, log_file='processed_files.txt'):
    """Process the HTML file if it hasn't been processed already, only within the base directory."""
    if os.path.dirname(file_path) != WEBSITES_DIR:
        print(f"Skipping file in subdirectory: {file_path}")
        return

    processed_files = load_processed_files(log_file)
    filename = os.path.basename(file_path)

    if filename not in processed_files:
        print(f"Processing file: {file_path}")
        remove_href_from_file(file_path)
        save_processed_file(log_file, filename)
    else:
        print(f"Skipping already processed file: {filename}")

def inject_js_to_file(html_file, js_code, log_file='js_injected_files.txt'):
    """Inject JavaScript code at the top of the body of the HTML file if not already injected."""
    injected_files = load_processed_files(log_file)
    filename = os.path.basename(html_file)

    if filename in injected_files:
        print(f"Skipping JavaScript injection as it is already added: {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    js_element = BeautifulSoup(js_code, 'html.parser')

    if soup.body:
        soup.body.insert(0, js_element)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"Injected JavaScript at the top of the body in: {html_file}")
    save_processed_file(log_file, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inject_js', methods=['POST'])
def inject_js():
    site_name = request.form.get('site_name')
    js_code = request.form.get('js_code')
    full_path = os.path.join(WEBSITES_DIR, site_name)

    if os.path.exists(full_path) and full_path.endswith('.html'):
        process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
        inject_js_to_file(full_path, js_code, JS_INJECTED_FILES_LOG)
        return render_template('code_injected.html', site_name=site_name)
    else:
        return render_template('404.html', site_name=site_name)

@app.route('/websites')
def list_websites():
    websites = [f for f in os.listdir(WEBSITES_DIR) if f.endswith('.html')]
    return render_template('websites.html', websites=websites)

@app.route('/delete_website', methods=['POST'])
def delete_website():
    site_name = request.form.get('site_name')
    full_path = os.path.join(WEBSITES_DIR, site_name)

    if os.path.exists(full_path):
        # Remove the HTML file
        os.remove(full_path)
        
        # Check if there's a corresponding folder with the same name as the HTML file, but with '_files' appended
        folder_name = os.path.splitext(site_name)[0] + '_files'
        folder_path = os.path.join(WEBSITES_DIR, folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        # Remove the file from both log files
        remove_file_from_log(PROCESSED_FILES_LOG, site_name)
        remove_file_from_log(JS_INJECTED_FILES_LOG, site_name)

        # Remove the visit count for the deleted website
        remove_visit_count(site_name)

        return redirect(url_for('list_websites'))
    else:
        return render_template('404.html', site_name=site_name)

@app.route('/visit_counts')
def visit_counts():
    visit_counts = load_visit_counts()
    return render_template('visit_counts.html', visit_counts=visit_counts)

@app.route('/<path:site_path>')
def serve_site(site_path):
    full_path = os.path.join(WEBSITES_DIR, site_path)

    if os.path.exists(full_path):
        if full_path.endswith(".html"):
            process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
            # Increment the visit count for the website
            increment_visit_count(site_path)
        return send_from_directory(WEBSITES_DIR, site_path)
    else:
        return render_template('404.html', site_name=site_path)

if __name__ == '__main__':
    app.run(debug=True)
