import os
from agents import summarize_jd, match_cv, shortlist_candidate, schedule_interview
from database import get_shortlisted_candidates, close_connection
from utils import extract_text_from_pdf, extract_email

def main():
    try:
        # Summarize JD
        jd_file = "data/job_description.csv"
        if not os.path.exists(jd_file):
            raise FileNotFoundError(f"Job description file not found: {jd_file}")
        try:
            jd_summary = summarize_jd(jd_file)
            print(f"JD Summary: {jd_summary}")
        except UnicodeDecodeError as e:
            print(f"UTF-8 encoding failed for {jd_file}: {e}")
            # Fallback to Windows-1252
            with open(jd_file, encoding='windows-1252') as f:
                jd_text = f.read()
            # Assuming summarize_jd can take text instead of a file path
            jd_summary = summarize_jd(jd_text)  # Modify if summarize_jd expects a file
            print(f"JD Summary (using fallback encoding): {jd_summary}")

        # Process CVs
        cv_dir = "data/CVs1"
        if not os.path.isdir(cv_dir):
            raise FileNotFoundError(f"CV directory not found: {cv_dir}")
        cv_files = [f for f in os.listdir(cv_dir) if f.endswith(".pdf")]

        for cv_file in cv_files:
            cv_id = os.path.splitext(cv_file)[0]
            cv_path = os.path.join(cv_dir, cv_file)
            
            # Extract email and match CV
            try:
                cv_text = extract_text_from_pdf(cv_path)
                email = extract_email(cv_text)
                score = match_cv(cv_path, jd_summary)
                print(f"{cv_id} Score: {score}, Email: {email or 'Not found'}")
            except UnicodeDecodeError as e:
                print(f"Encoding error in {cv_file}: {e}")
                continue

            # Shortlist and schedule
            if email and shortlist_candidate(cv_id, score, email):
                print(schedule_interview(cv_id, email))

        # Show results
        shortlisted = get_shortlisted_candidates()
        print("\nFinal Shortlisted Candidates:")
        for cv_id, score, email in shortlisted:
            print(f"{cv_id}: Score={score}, Email={email}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        close_connection()

if __name__ == "__main__":
    main()