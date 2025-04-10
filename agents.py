from dotenv import load_dotenv  # Add this import
import ollama
import pandas as pd
from database import save_candidate, get_shortlisted_candidates
from utils import extract_text_from_pdf, preprocess_text
import smtplib
from email.mime.text import MIMEText
import os

# Load environment variables from .env file
load_dotenv()

# JD Summarizer Agent
def summarize_jd(file_path):
    """Summarizes job description from CSV using Ollama."""
    try:
        # Try reading with UTF-8 first
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to Windows-1252 if UTF-8 fails
        df = pd.read_csv(file_path, encoding='windows-1252')
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

    try:
        jd_text = df.iloc[0]['Job Description']  # Take first JD for demo
        prompt = f"Summarize this job description into key skills and experience: {jd_text}"
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]  # e.g., "Skills: Python, Java; Experience: 3+ years"
    except Exception as e:
        print(f"Error in JD summarization: {str(e)}")
        return None

# CV Matching Agent
def match_cv(cv_path, jd_summary):
    """Extracts CV data and matches it with JD summary."""
    try:
        cv_text = extract_text_from_pdf(cv_path)
        cv_processed = preprocess_text(cv_text)
        prompt = f"Extract skills and experience from: {cv_processed}\nMatch with: {jd_summary}\nReturn a score (0-100)."
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        try:
            score = float(response["message"]["content"].split("Score: ")[-1].strip())
        except (IndexError, ValueError):
            print("Error parsing score from response.")
            score = 0  # Fallback if parsing fails
        return score
    except FileNotFoundError:
        print(f"Error: CV file not found at {cv_path}")
        return 0
    except Exception as e:
        print(f"Error in CV matching: {str(e)}")
        return 0

# Shortlisting Agent
def shortlist_candidate(cv_id, score, threshold=80):
    """Shortlists candidates based on match score."""
    try:
        score = float(score)  # Ensure score is a float
    except ValueError:
        print(f"Invalid score for {cv_id}: {score}")
        return False
    if score >= threshold:
        save_candidate(cv_id, score)
        return True
    return False

# Interview Scheduler Agent
def schedule_interview(cv_id, candidate_email):
    """Sends an interview email using SMTP."""
    sender_email = os.getenv("SENDER_EMAIL")  # Fetch from environment
    sender_password = os.getenv("SENDER_PASSWORD")  # Fetch from environment

    if not sender_email or not sender_password:
        print("Error: Missing sender email or password in environment variables.")
        return "Failed to send email: Missing credentials"

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
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check your email and password.")
        return "Failed to send email: Authentication error"
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return f"Failed to send email: {str(e)}"

# Example usage (for testing)
if __name__ == "__main__":
    jd_summary = summarize_jd("data/job_description.csv")
    if jd_summary:
        score = match_cv("data/CVs1/C1061.pdf", jd_summary)
        if shortlist_candidate("C1061", score):
            print(schedule_interview("C1061", "alyssachavez88@gmail.com"))