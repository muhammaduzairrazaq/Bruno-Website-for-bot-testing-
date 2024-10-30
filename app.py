# from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, session
# import os
# import shutil
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Needed for session handling

# # Log files
# PROCESSED_FILES_LOG = 'processed_files.txt'
# JS_INJECTED_FILES_LOG = 'js_injected_files.txt'
# VISIT_COUNTS_LOG = 'visit_counts.txt'
# ONE_DAY_VISITS_LOG = 'one_day_visits.txt'
# THREE_DAY_VISITS_LOG = 'three_day_visits.txt'
# SEVEN_DAY_VISITS_LOG = 'seven_day_visits.txt'
# ONE_DAY_TIMESTAMP_LOG = 'one_day_timestamp.txt'
# THREE_DAY_TIMESTAMP_LOG = 'three_day_timestamp.txt'
# SEVEN_DAY_TIMESTAMP_LOG = 'seven_day_timestamp.txt'
# CREATED_TIMESTAMP_LOG = 'processed_files_creation.txt'


# # Directory for uploaded websites
# UPLOAD_FOLDER = 'websites'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Functions for processing HTML files
# def load_processed_files(log_file):
#     """Load the list of already processed files from a log file."""
#     if os.path.exists(log_file):
#         with open(log_file, 'r') as f:
#             return set(line.strip() for line in f)
#     return set()

# def save_processed_file(log_file, filename):
#     """Append the newly processed file to the log file."""
#     with open(log_file, 'a') as f:
#         f.write(filename + '\n')

# def remove_file_from_log(log_file, filename):
#     """Remove the specified file from the log file."""
#     if os.path.exists(log_file):
#         with open(log_file, 'r') as f:
#             lines = f.readlines()
#         with open(log_file, 'w') as f:
#             for line in lines:
#                 if line.strip() != filename:
#                     f.write(line)

# def load_visit_counts():
#     """Load visit counts from the log file."""
#     visit_counts = {}
#     if os.path.exists(VISIT_COUNTS_LOG):
#         with open(VISIT_COUNTS_LOG, 'r') as f:
#             for line in f:
#                 try:
#                     name, count = line.strip().split(':')
#                     visit_counts[name] = int(count)
#                 except ValueError:
#                     print(f"Skipping invalid line in visit counts: {line.strip()}")

#     reversed_visit_counts = {k: v for k, v in list(visit_counts.items())[::-1]}
#     return reversed_visit_counts

# def save_visit_counts(visit_counts):
#     """Save visit counts to the log file."""
#     with open(VISIT_COUNTS_LOG, 'w') as f:
#         for name, count in visit_counts.items():
#             f.write(f"{name}:{count}\n")

# def load_timeframe_visits(log_file):
#     """Load timeframe visits from a log file."""
#     if not os.path.exists(log_file):
#         return {}

#     timeframe_visits = {}
#     with open(log_file, 'r') as f:
#         for line in f:
#             try:
#                 name, count = line.strip().split(':')
#                 timeframe_visits[name] = int(count)
#             except ValueError:
#                 print(f"Skipping invalid line in timeframe visits: {line.strip()}")
#     return timeframe_visits

# def save_timeframe_visits(log_file, visits):
#     """Save timeframe visits to the log file."""
#     with open(log_file, 'w') as f:
#         for name, count in visits.items():
#             f.write(f"{name}:{count}\n")

# def load_timestamp(log_file):
#     """Load timestamps from a log file."""
#     timestamps = {}
#     if os.path.exists(log_file):
#         with open(log_file, 'r') as f:
#             for line in f:
#                 try:
#                     name, timestamp = line.strip().split(':')
#                     timestamps[name] = datetime.fromisoformat(timestamp)
#                 except ValueError:
#                     print(f"Skipping invalid line in timestamps: {line.strip()}")
#     return timestamps

# def save_timestamp(log_file, website, timestamp):
#     """Append the current timestamp for a website to the log file."""
#     with open(log_file, 'a') as f:
#         f.write(f"{website}:{timestamp.isoformat()}\n")

# def reset_timeframe_visits(filename, timeframe):
#     """Reset the visit count for the specified timeframe."""
#     if timeframe == '1_day':
#         reset_file = ONE_DAY_VISITS_LOG
#         timestamp_file = ONE_DAY_TIMESTAMP_LOG
#     elif timeframe == '3_day':
#         reset_file = THREE_DAY_VISITS_LOG
#         timestamp_file = THREE_DAY_TIMESTAMP_LOG
#     elif timeframe == '7_day':
#         reset_file = SEVEN_DAY_VISITS_LOG
#         timestamp_file = SEVEN_DAY_TIMESTAMP_LOG
#     else:
#         return

#     # Load existing visits and timestamp
#     visits = load_timeframe_visits(reset_file)
#     timestamps = load_timestamp(timestamp_file)

#     # Determine if a reset is necessary
#     reset_duration = {
#         '1_day': timedelta(days=1),
#         '3_day': timedelta(days=3),
#         '7_day': timedelta(days=7)
#     }

#     if timestamps.get(filename) is None or (datetime.now() - timestamps[filename]) >= reset_duration[timeframe]:
#         visits[filename] = 0  # Reset the visit count
#         save_timeframe_visits(reset_file, visits)  # Save the updated visits
#         save_timestamp(timestamp_file, filename, datetime.now())  # Update the timestamp

# def clear_processed_files_if_needed():
#     """Clear processed_files.txt if it is older than 40 days."""
#     # Check if the creation timestamp file exists
#     if not os.path.exists(CREATED_TIMESTAMP_LOG):
#         # If it doesn't exist, create it and write the current timestamp
#         with open(CREATED_TIMESTAMP_LOG, 'w') as f:
#             f.write(datetime.now().isoformat())
#         return

#     # Load the timestamp
#     with open(CREATED_TIMESTAMP_LOG, 'r') as f:
#         creation_time = datetime.fromisoformat(f.read().strip())

#     # Check if it's older than 40 days
#     if datetime.now() - creation_time > timedelta(days=40):
#         # Clear the processed files log
#         with open(PROCESSED_FILES_LOG, 'w') as f:
#             f.write("")  # Clear the file
#         # Update the creation timestamp
#         with open(CREATED_TIMESTAMP_LOG, 'w') as f:
#             f.write(datetime.now().isoformat())  # Reset the timestamp


# def increment_visit_count(filename):
#     """Increment the visit count for the given filename only if it exists in the websites directory."""
#     websites_dir_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]

#     if filename not in websites_dir_files:
#         print(f"File {filename} does not match any file in the directory, count not incremented.")
#         return

#     # Increment total visits
#     visit_counts = load_visit_counts()
#     if filename in visit_counts:
#         visit_counts[filename] += 1
#     else:
#         visit_counts[filename] = 1
#     save_visit_counts(visit_counts)

#     # Increment timeframe visits
#     increment_timeframe_visits(filename)

# def increment_timeframe_visits(filename):
#     """Increment the visit count for 1-day, 3-day, and 7-day visits."""
#     # Load existing counts
#     one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
#     three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
#     seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

#     # Reset counts if necessary
#     reset_timeframe_visits(filename, '1_day')
#     reset_timeframe_visits(filename, '3_day')
#     reset_timeframe_visits(filename, '7_day')

#     # Increment counts
#     one_day_visits[filename] = one_day_visits.get(filename, 0) + 1
#     three_day_visits[filename] = three_day_visits.get(filename, 0) + 1
#     seven_day_visits[filename] = seven_day_visits.get(filename, 0) + 1

#     # Save updated counts
#     save_timeframe_visits(ONE_DAY_VISITS_LOG, one_day_visits)
#     save_timeframe_visits(THREE_DAY_VISITS_LOG, three_day_visits)
#     save_timeframe_visits(SEVEN_DAY_VISITS_LOG, seven_day_visits)

# def remove_visit_count(filename):
#     """Remove the visit count entry for the specified filename."""
#     visit_counts = load_visit_counts()
#     if filename in visit_counts:
#         del visit_counts[filename]
#     save_visit_counts(visit_counts)

# def remove_timeframe_visit_count(filename):
#     """Remove the visit count entries for the specified filename from the timeframe logs."""
#     one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
#     three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
#     seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

#     # Remove counts for the filename
#     if filename in one_day_visits:
#         del one_day_visits[filename]
#     if filename in three_day_visits:
#         del three_day_visits[filename]
#     if filename in seven_day_visits:
#         del seven_day_visits[filename]

#     # Save updated counts
#     save_timeframe_visits(ONE_DAY_VISITS_LOG, one_day_visits)
#     save_timeframe_visits(THREE_DAY_VISITS_LOG, three_day_visits)
#     save_timeframe_visits(SEVEN_DAY_VISITS_LOG, seven_day_visits)

# def remove_timestamp(filename, timeframe):
#     """Remove the timestamp for the specified timeframe."""
#     if timeframe == '1_day':
#         timestamp_file = ONE_DAY_TIMESTAMP_LOG
#     elif timeframe == '3_day':
#         timestamp_file = THREE_DAY_TIMESTAMP_LOG
#     elif timeframe == '7_day':
#         timestamp_file = SEVEN_DAY_TIMESTAMP_LOG
#     else:
#         return

#     # Load current timestamps
#     timestamps = load_timestamp(timestamp_file)

#     # Remove timestamp for the filename
#     if filename in timestamps:
#         del timestamps[filename]

#     # Save the updated timestamps
#     save_timeframe_visits(timestamp_file, timestamps)

# def remove_href_from_file(html_file):
#     """Make HTML static by removing interactive elements."""
#     with open(html_file, 'r', encoding='utf-8') as f:
#         soup = BeautifulSoup(f, 'html.parser')

#     # Remove href attributes from all <a> tags
#     for a_tag in soup.find_all('a', href=True):
#         a_tag['href'] = '#'

#     # Remove onclick attributes from all elements
#     for tag in soup.find_all(onclick=True):
#         del tag['onclick']

#     # Remove other event attributes like onmouseover, onmouseout, etc.
#     event_attributes = ['onmouseover', 'onmouseout', 'onchange', 'onsubmit', 'onload']
#     for event in event_attributes:
#         for tag in soup.find_all(attrs={event: True}):
#             del tag[event]

#     # Disable forms by removing the action attribute or setting it to '#'
#     for form_tag in soup.find_all('form', action=True):
#         form_tag['action'] = '#'

#     # Remove all <script> tags to disable JavaScript
#     for script_tag in soup.find_all('script'):
#         script_tag.decompose()

#     # Write the modified HTML back to the file
#     with open(html_file, 'w', encoding='utf-8') as f:
#         f.write(str(soup))

#     print(f"Modified HTML saved: {html_file}")

# def process_html_file_if_needed(file_path, log_file='processed_files.txt'):
#     """Process the HTML file if it hasn't been processed already."""
#     processed_files = load_processed_files(log_file)
#     filename = os.path.basename(file_path)

#     if filename not in processed_files:
#         print(f"Processing file: {file_path}")
#         remove_href_from_file(file_path)
#         save_processed_file(log_file, filename)
#     else:
#         print(f"Skipping already processed file: {filename}")

# def inject_js_to_file(html_file, js_code, log_file='js_injected_files.txt'):
#     """Inject JavaScript code at the top of the body of the HTML file if not already injected."""
#     injected_files = load_processed_files(log_file)
#     filename = os.path.basename(html_file)

#     if filename in injected_files:
#         print(f"Skipping JavaScript injection as it is already added: {html_file}")
#         return

#     with open(html_file, 'r', encoding='utf-8') as f:
#         soup = BeautifulSoup(f, 'html.parser')

#     js_element = BeautifulSoup(js_code, 'html.parser')

#     if soup.body:
#         soup.body.insert(0, js_element)

#     with open(html_file, 'w', encoding='utf-8') as f:
#         f.write(str(soup))

#     print(f"Injected JavaScript at the top of the body in: {html_file}")
#     save_processed_file(log_file, filename)

# @app.route('/')
# def index():
#     if not session.get('logged_in'):  # Check if the user is logged in
#         return redirect(url_for('login'))  # Redirect to login if not logged in
#     return render_template('index.html')

# # Load the password from the password file
# def load_password():
#     try:
#         with open('password.txt', 'r') as f:
#             return f.read().strip()
#     except FileNotFoundError:
#         return None
    

# # Route for the password page
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         password = request.form.get('password')
#         if password == load_password():
#             session['logged_in'] = True  # Set session variable for logged in status
#             return redirect(url_for('index'))  # Redirect to the main app
#         else:
#             return render_template('login.html', error="Incorrect password. Please try again.")
#     return render_template('login.html')


# @app.route('/upload_directory', methods=['POST'])
# def upload_directory():
#     if 'directory' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     files = request.files.getlist('directory')

#     for file in files:
#         if file.filename == '':
#             return jsonify({"error": "No selected file"}), 400
        
#         # Construct the full path where the directory structure will be saved
#         save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
#         # Ensure the directory exists
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)

#         # Save the file
#         file.save(save_path)

#     return jsonify({"message": "Directory uploaded successfully!"}), 200

# @app.route('/upload_file', methods=['POST'])
# def upload_file():
#     if 'html_file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['html_file']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Save the uploaded HTML file
#     save_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(save_path)

#     return jsonify({"message": "HTML file uploaded successfully!"}), 200

# @app.route('/inject_js', methods=['POST'])
# def inject_js():
#     site_name = request.form.get('site_name')
#     js_code = request.form.get('js_code')
#     full_path = os.path.join(UPLOAD_FOLDER, site_name)
    
#     if os.path.exists(full_path) and full_path.endswith('.html'):
#         process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
#         inject_js_to_file(full_path, js_code, JS_INJECTED_FILES_LOG)
#         return render_template('code_injected.html', site_name=site_name)
#     else:
#         return render_template('404.html', site_name=site_name)

# @app.route('/websites')
# def list_websites():
#     websites = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]
#     return render_template('websites.html', websites=websites)

# @app.route('/delete_website', methods=['POST'])
# def delete_website():
#     site_name = request.form.get('site_name')
#     full_path = os.path.join(UPLOAD_FOLDER, site_name)
#     if os.path.exists(full_path):
#         os.remove(full_path)
#         folder_name = os.path.splitext(site_name)[0] + '_files'
#         folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
#         if os.path.exists(folder_path) and os.path.isdir(folder_path):
#             shutil.rmtree(folder_path)

#         remove_file_from_log(PROCESSED_FILES_LOG, site_name)
#         remove_file_from_log(JS_INJECTED_FILES_LOG, site_name)

#         # Remove visit count for the deleted website
#         remove_visit_count(site_name)

#         # Remove timeframe visits for the deleted website
#         remove_timeframe_visit_count(site_name)

#         # Remove timestamps for the deleted website
#         remove_timestamp(site_name, '1_day')
#         remove_timestamp(site_name, '3_day')
#         remove_timestamp(site_name, '7_day')

#         return redirect(url_for('list_websites'))
#     else:
#         return render_template('404.html', site_name=site_name)

# @app.route('/visit_counts')
# def visit_counts():
#     # Load counts for each timeframe
#     one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
#     three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
#     seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

#     # Combine data for rendering
#     visit_counts = load_visit_counts()
    
#     # Create a combined dictionary with all counts
#     combined_counts = {}
#     for website in visit_counts.keys():
#         combined_counts[website] = {
#             'total': visit_counts[website],
#             '1_day': one_day_visits.get(website, 0),
#             '3_day': three_day_visits.get(website, 0),
#             '7_day': seven_day_visits.get(website, 0)
#         }

#     return render_template('visit_counts.html', visit_counts=combined_counts)

# @app.route('/<path:site_path>')
# def serve_site(site_path):
#     full_path = os.path.join(UPLOAD_FOLDER, site_path)
#     if os.path.exists(full_path):
#         if full_path.endswith(".html"):
#             increment_visit_count(site_path)  # Increment the visit count only if the file exists in WEBSITES_DIR
#             process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
#         return send_from_directory(UPLOAD_FOLDER, site_path)
#     else:
#         return render_template('404.html', site_name=site_path)

# if __name__ == '__main__':
#     clear_processed_files_if_needed()
#     app.run(debug=True)



from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, session
import os
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

# Log files
PROCESSED_FILES_LOG = 'processed_files.txt'
JS_INJECTED_FILES_LOG = 'js_injected_files.txt'
VISIT_COUNTS_LOG = 'visit_counts.txt'
ONE_DAY_VISITS_LOG = 'one_day_visits.txt'
THREE_DAY_VISITS_LOG = 'three_day_visits.txt'
SEVEN_DAY_VISITS_LOG = 'seven_day_visits.txt'
ONE_DAY_TIMESTAMP_LOG = 'one_day_timestamp.txt'
THREE_DAY_TIMESTAMP_LOG = 'three_day_timestamp.txt'
SEVEN_DAY_TIMESTAMP_LOG = 'seven_day_timestamp.txt'
CREATED_TIMESTAMP_LOG = 'processed_files_creation.txt'

# Directory for uploaded websites
UPLOAD_FOLDER = 'websites'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
                try:
                    name, count = line.strip().split(':')
                    visit_counts[name] = int(count)
                except ValueError:
                    print(f"Skipping invalid line in visit counts: {line.strip()}")

    reversed_visit_counts = {k: v for k, v in list(visit_counts.items())[::-1]}
    return reversed_visit_counts

def save_visit_counts(visit_counts):
    """Save visit counts to the log file."""
    with open(VISIT_COUNTS_LOG, 'w') as f:
        for name, count in visit_counts.items():
            f.write(f"{name}:{count}\n")

def load_timeframe_visits(log_file):
    """Load timeframe visits from a log file."""
    if not os.path.exists(log_file):
        return {}

    timeframe_visits = {}
    with open(log_file, 'r') as f:
        for line in f:
            try:
                name, count = line.strip().split(':')
                timeframe_visits[name] = int(count)
            except ValueError:
                print(f"Skipping invalid line in timeframe visits: {line.strip()}")
    return timeframe_visits

def save_timeframe_visits(log_file, visits):
    """Save timeframe visits to the log file."""
    with open(log_file, 'w') as f:
        for name, count in visits.items():
            f.write(f"{name}:{count}\n")

def load_timestamp(log_file):
    """Load timestamps from a log file."""
    timestamps = {}
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    name, timestamp = line.strip().split(':')
                    timestamps[name] = datetime.fromisoformat(timestamp)
                except ValueError:
                    print(f"Skipping invalid line in timestamps: {line.strip()}")
    return timestamps

def save_timestamp(log_file, website, timestamp):
    """Append the current timestamp for a website to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{website}:{timestamp.isoformat()}\n")

def reset_timeframe_visits(filename, timeframe):
    """Reset the visit count for the specified timeframe."""
    if timeframe == '1_day':
        reset_file = ONE_DAY_VISITS_LOG
        timestamp_file = ONE_DAY_TIMESTAMP_LOG
    elif timeframe == '3_day':
        reset_file = THREE_DAY_VISITS_LOG
        timestamp_file = THREE_DAY_TIMESTAMP_LOG
    elif timeframe == '7_day':
        reset_file = SEVEN_DAY_VISITS_LOG
        timestamp_file = SEVEN_DAY_TIMESTAMP_LOG
    else:
        return

    # Load existing visits and timestamp
    visits = load_timeframe_visits(reset_file)
    timestamps = load_timestamp(timestamp_file)

    # Determine if a reset is necessary
    reset_duration = {
        '1_day': timedelta(days=1),
        '3_day': timedelta(days=3),
        '7_day': timedelta(days=7)
    }

    if timestamps.get(filename) is None or (datetime.now() - timestamps[filename]) >= reset_duration[timeframe]:
        visits[filename] = 0  # Reset the visit count
        save_timeframe_visits(reset_file, visits)  # Save the updated visits
        save_timestamp(timestamp_file, filename, datetime.now())  # Update the timestamp

def clear_processed_files_if_needed():
    """Clear processed_files.txt if it is older than 40 days."""
    # Check if the creation timestamp file exists
    if not os.path.exists(CREATED_TIMESTAMP_LOG):
        # If it doesn't exist, create it and write the current timestamp
        with open(CREATED_TIMESTAMP_LOG, 'w') as f:
            f.write(datetime.now().isoformat())
        return

    # Load the timestamp
    with open(CREATED_TIMESTAMP_LOG, 'r') as f:
        creation_time = datetime.fromisoformat(f.read().strip())

    # Check if it's older than 40 days
    if datetime.now() - creation_time > timedelta(days=40):
        # Clear the processed files log
        with open(PROCESSED_FILES_LOG, 'w') as f:
            f.write("")  # Clear the file
        # Update the creation timestamp
        with open(CREATED_TIMESTAMP_LOG, 'w') as f:
            f.write(datetime.now().isoformat())  # Reset the timestamp

def increment_visit_count(filename):
    """Increment the visit count for the given filename only if it exists in the websites directory."""
    websites_dir_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]

    if filename not in websites_dir_files:
        print(f"File {filename} does not match any file in the directory, count not incremented.")
        return

    # Increment total visits
    visit_counts = load_visit_counts()
    if filename in visit_counts:
        visit_counts[filename] += 1
    else:
        visit_counts[filename] = 1
    save_visit_counts(visit_counts)

    # Increment timeframe visits
    increment_timeframe_visits(filename)

def increment_timeframe_visits(filename):
    """Increment the visit count for 1-day, 3-day, and 7-day visits."""
    # Load existing counts
    one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
    three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
    seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

    # Reset counts if necessary
    reset_timeframe_visits(filename, '1_day')
    reset_timeframe_visits(filename, '3_day')
    reset_timeframe_visits(filename, '7_day')

    # Increment counts
    one_day_visits[filename] = one_day_visits.get(filename, 0) + 1
    three_day_visits[filename] = three_day_visits.get(filename, 0) + 1
    seven_day_visits[filename] = seven_day_visits.get(filename, 0) + 1

    # Save updated counts
    save_timeframe_visits(ONE_DAY_VISITS_LOG, one_day_visits)
    save_timeframe_visits(THREE_DAY_VISITS_LOG, three_day_visits)
    save_timeframe_visits(SEVEN_DAY_VISITS_LOG, seven_day_visits)

def remove_visit_count(filename):
    """Remove the visit count entry for the specified filename."""
    visit_counts = load_visit_counts()
    if filename in visit_counts:
        del visit_counts[filename]
    save_visit_counts(visit_counts)

def remove_timeframe_visit_count(filename):
    """Remove the visit count entries for the specified filename from the timeframe logs."""
    one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
    three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
    seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

    # Remove counts for the filename
    if filename in one_day_visits:
        del one_day_visits[filename]
    if filename in three_day_visits:
        del three_day_visits[filename]
    if filename in seven_day_visits:
        del seven_day_visits[filename]

    # Save updated counts
    save_timeframe_visits(ONE_DAY_VISITS_LOG, one_day_visits)
    save_timeframe_visits(THREE_DAY_VISITS_LOG, three_day_visits)
    save_timeframe_visits(SEVEN_DAY_VISITS_LOG, seven_day_visits)

def remove_timestamp(filename, timeframe):
    """Remove the timestamp for the specified timeframe."""
    if timeframe == '1_day':
        timestamp_file = ONE_DAY_TIMESTAMP_LOG
    elif timeframe == '3_day':
        timestamp_file = THREE_DAY_TIMESTAMP_LOG
    elif timeframe == '7_day':
        timestamp_file = SEVEN_DAY_TIMESTAMP_LOG
    else:
        return

    # Load current timestamps
    timestamps = load_timestamp(timestamp_file)

    # Remove timestamp for the filename
    if filename in timestamps:
        del timestamps[filename]

    # Save the updated timestamps
    save_timeframe_visits(timestamp_file, timestamps)

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
    """Process the HTML file if it hasn't been processed already."""
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
    if not session.get('logged_in'):  # Check if the user is logged in
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('index.html')

# Load the password from the password file
def load_password():
    try:
        with open('password.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    

# Route for the password page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == load_password():
            session['logged_in'] = True  # Set session variable for logged in status
            return redirect(url_for('index'))  # Redirect to the main app
        else:
            return render_template('login.html', error="Incorrect password. Please try again.")
    return render_template('login.html')


@app.route('/upload_directory', methods=['POST'])
def upload_directory():
    if 'directory' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('directory')

    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Construct the full path where the directory structure will be saved
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the file
        file.save(save_path)

    return jsonify({"message": "Directory uploaded successfully!"}), 200

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'html_file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['html_file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded HTML file
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({"message": "HTML file uploaded successfully!"}), 200

@app.route('/inject_js', methods=['POST'])
def inject_js():
    site_name = request.form.get('site_name')
    js_code = request.form.get('js_code')
    full_path = os.path.join(UPLOAD_FOLDER, site_name)
    
    if os.path.exists(full_path) and full_path.endswith('.html'):
        process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
        inject_js_to_file(full_path, js_code, JS_INJECTED_FILES_LOG)
        return render_template('code_injected.html', site_name=site_name)
    else:
        return render_template('404.html', site_name=site_name)

@app.route('/websites')
def list_websites():
    websites = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]
    return render_template('websites.html', websites=websites)

@app.route('/delete_website', methods=['POST'])
def delete_website():
    site_name = request.form.get('site_name')
    full_path = os.path.join(UPLOAD_FOLDER, site_name)
    if os.path.exists(full_path):
        os.remove(full_path)
        folder_name = os.path.splitext(site_name)[0] + '_files'
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        remove_file_from_log(PROCESSED_FILES_LOG, site_name)
        remove_file_from_log(JS_INJECTED_FILES_LOG, site_name)

        # Remove visit count for the deleted website
        remove_visit_count(site_name)

        # Remove timeframe visits for the deleted website
        remove_timeframe_visit_count(site_name)

        # Remove timestamps for the deleted website
        remove_timestamp(site_name, '1_day')
        remove_timestamp(site_name, '3_day')
        remove_timestamp(site_name, '7_day')

        return redirect(url_for('list_websites'))
    else:
        return render_template('404.html', site_name=site_name)

@app.route('/visit_counts')
def visit_counts():
    # Load counts for each timeframe
    one_day_visits = load_timeframe_visits(ONE_DAY_VISITS_LOG)
    three_day_visits = load_timeframe_visits(THREE_DAY_VISITS_LOG)
    seven_day_visits = load_timeframe_visits(SEVEN_DAY_VISITS_LOG)

    # Combine data for rendering
    visit_counts = load_visit_counts()
    
    # Create a combined dictionary with all counts
    combined_counts = {}
    for website in visit_counts.keys():
        combined_counts[website] = {
            'total': visit_counts[website],
            '1_day': one_day_visits.get(website, 0),
            '3_day': three_day_visits.get(website, 0),
            '7_day': seven_day_visits.get(website, 0)
        }

    return render_template('visit_counts.html', visit_counts=combined_counts)

@app.route('/<path:site_path>')
def serve_site(site_path):
    full_path = os.path.join(UPLOAD_FOLDER, site_path)
    if os.path.exists(full_path):
        if full_path.endswith(".html"):
            increment_visit_count(site_path)  # Increment the visit count only if the file exists in WEBSITES_DIR
            process_html_file_if_needed(full_path, PROCESSED_FILES_LOG)
        return send_from_directory(UPLOAD_FOLDER, site_path)
    else:
        return render_template('404.html', site_name=site_path)

if __name__ == '__main__':
    app.run(debug=True)
