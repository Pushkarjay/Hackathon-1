import ollama
import pandas as pd
from database import save_candidate, get_shortlisted_candidates
from utils import extract_text_from_pdf, preprocess_text
import smtplib
from email.mime.text import MIMEText

# JD Summarizer Agent
def summarize_jd(file_path):
    """Summarizes job description from CSV using Ollama."""
    try:
        # Try reading with UTF-8 first
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to Windows-1252 if UTF-8 fails
        df = pd.read_csv(file_path, encoding='windows-1252')
    jd_text = df.iloc[0]['Job Description']  # Take first JD for demo
    prompt = f"Summarize this job description into key skills and experience: {jd_text}"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]  # e.g., "Skills: Python, Java; Experience: 3+ years"

# CV Matching Agent
def match_cv(cv_path, jd_summary):
    """Extracts CV data and matches it with JD summary."""
    cv_text = extract_text_from_pdf(cv_path)
    cv_processed = preprocess_text(cv_text)
    prompt = f"Extract skills and experience from: {cv_processed}\nMatch with: {jd_summary}\nReturn a score (0-100)."
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    try:
        score = float(response["message"]["content"].split("Score: ")[-1].strip())
    except (IndexError, ValueError):
        score = 0  # Fallback if parsing fails
    return score

# Shortlisting Agent
def shortlist_candidate(cv_id, score, threshold=80):
    """Shortlists candidates based on match score."""
    if score >= threshold:
        save_candidate(cv_id, score)
        return True
    return False

# Interview Scheduler Agent
def schedule_interview(cv_id, candidate_email):
    """Sends an interview email using SMTP."""
    sender_email = "sickob0ygaming69@gmail.com"  # Replace with your email
    sender_password = "chiw nfdq dfck hezw"  # Use app-specific password for Gmail
    
    subject = "Interview Invitation"
    body = f"Dear {cv_id},\n\nYou are invited for an interview on April 10, 2025, at 10:00 AM.\n\nBest regards,\nTeam Gulu"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = candidate_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return f"Interview email sent to {candidate_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Example usage (for testing)
if __name__ == "__main__":  # Fixed typo from "_main_" to "__main__"
    jd_summary = summarize_jd("data/job_description.csv")
    score = match_cv("data/CVs1/C1061.pdf", jd_summary)
    if shortlist_candidate("C1061", score):
        print(schedule_interview("C1061", "alyssachavez88@gmail.com"))