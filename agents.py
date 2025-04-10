from dotenv import load_dotenv  # Add this import
import ollama
import pandas as pd
from database import save_candidate, get_shortlisted_candidates
from utils import extract_text_from_pdf, preprocess_text
import smtplib
from email.mime.text import MIMEText
import os
import requests  # Add this import

# Load environment variables from .env file
load_dotenv()

# Replace Ollama API calls with Gemini API calls
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# JD Summarizer Agent
def summarize_jd(file_path):
    """Summarizes job description from CSV using Gemini."""
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
        payload = {
            "contents": [{"parts": [{"text": f"Summarize this job description into key skills and experience: {jd_text}"}]}]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params={"key": GEMINI_API_KEY})
        response_data = response.json()
        if response.status_code == 200 and "contents" in response_data:
            return response_data["contents"][0]["parts"][0]["text"]
        else:
            print(f"Error: Unexpected response format from Gemini API. {response_data}")
            return None
    except Exception as e:
        print(f"Error in JD summarization: {str(e)}")
        return None

# CV Matching Agent
def match_cv(cv_path, jd_summary):
    """Extracts CV data and matches it with JD summary using Gemini."""
    try:
        cv_text = extract_text_from_pdf(cv_path)
        cv_processed = preprocess_text(cv_text)
        prompt = f"Extract skills and experience from: {cv_processed}\nMatch with: {jd_summary}\nReturn a score (0-100)."
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params={"key": GEMINI_API_KEY})
        response_data = response.json()
        if response.status_code == 200 and "contents" in response_data:
            try:
                score = float(response_data["contents"][0]["parts"][0]["text"].split("Score: ")[-1].strip())
                return score
            except (IndexError, ValueError):
                print("Error parsing score from response.")
                return 0
        else:
            print(f"Error: Unexpected response format from Gemini API. {response_data}")
            return 0
    except FileNotFoundError:
        print(f"Error: CV file not found at {cv_path}")
        return 0
    except Exception as e:
        print(f"Error in CV matching: {str(e)}")
        return 0

# Shortlisting Agent
def shortlist_candidate(cv_id, score, email=None, threshold=80):
    """Shortlists candidates based on match score."""
    try:
        score = float(score)  # Ensure score is a float
    except ValueError:
        print(f"Invalid score for {cv_id}: {score}")
        return False
    if score >= threshold:
        save_candidate(cv_id, score, email or "unknown@example.com")
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
        if shortlist_candidate("C1061", score, email="alyssachavez88@gmail.com"):
            print(schedule_interview("C1061", "alyssachavez88@gmail.com"))