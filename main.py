import os
from flask import Flask, request, render_template, jsonify, send_from_directory
from agents import summarize_jd, match_cv, shortlist_candidate, schedule_interview
from database import get_shortlisted_candidates, close_connection
from utils import extract_text_from_pdf, extract_email

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = 'data/CVs1'
JD_FILE = 'data/job_description.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle JD file upload
        if 'jd_file' not in request.files:
            return jsonify({'error': 'No JD file uploaded'}), 400
        jd_file = request.files['jd_file']
        if jd_file.filename == '':
            return jsonify({'error': 'No JD file selected'}), 400
        jd_file.save(JD_FILE)

        # Handle CV files upload
        if 'cv_files' not in request.files:
            return jsonify({'error': 'No CV files uploaded'}), 400
        cv_files = request.files.getlist('cv_files')

        # Save uploaded CVs
        for cv_file in cv_files:
            if cv_file and cv_file.filename.endswith('.pdf'):
                cv_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_file.filename)
                cv_file.save(cv_path)

        # Process JD and CVs
        try:
            jd_summary = summarize_jd(JD_FILE)
            if not jd_summary:
                return jsonify({'error': 'Failed to summarize JD'}), 500

            results = []
            for cv_file in os.listdir(app.config['UPLOAD_FOLDER']):
                if cv_file.endswith('.pdf'):
                    cv_id = os.path.splitext(cv_file)[0]
                    cv_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_file)
                    cv_text = extract_text_from_pdf(cv_path)
                    email = extract_email(cv_text)
                    score = match_cv(cv_path, jd_summary)
                    shortlisted = shortlist_candidate(cv_id, score)
                    if shortlisted and email != "unknown@example.com":
                        email_result = schedule_interview(cv_id, email)
                    else:
                        email_result = "Not shortlisted or no valid email"
                    results.append({
                        'cv_id': cv_id,
                        'score': score,
                        'email': email,
                        'shortlisted': shortlisted,
                        'email_result': email_result
                    })

            shortlisted_candidates = get_shortlisted_candidates()
            return render_template('index.html', results=results, shortlisted=shortlisted_candidates)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # GET request: Show the upload form
    shortlisted = get_shortlisted_candidates()
    return render_template('index.html', results=None, shortlisted=shortlisted)

@app.teardown_appcontext
def shutdown_db(exception=None):
    """Closes the database connection at the end of the request."""
    close_connection()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)