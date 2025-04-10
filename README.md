# HireSmart

HireSmart is an AI-powered recruitment automation tool designed to streamline the hiring process. It extracts, processes, and matches candidate CVs with job descriptions, shortlists candidates, and schedules interviews.

## Features
- Extracts text from PDF CVs.
- Summarizes job descriptions using AI.
- Matches CVs with job descriptions and scores them.
- Shortlists candidates based on a threshold score.
- Sends interview invitations via email.

## Prerequisites
- Python 3.8+
- Virtual environment (optional but recommended)

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Hackathon-1
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file:
   - Create a `.env` file in the root directory.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
     ```

5. Run the application:
   ```bash
   python main.py
   ```

6. Push the project to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <repository-url>
   git push -u origin main
   ```

## File Structure
- `main.py`: Entry point for the application.
- `agents.py`: Contains AI agents for summarization, matching, and scheduling.
- `utils.py`: Utility functions for text extraction and preprocessing.
- `database.py`: Handles database operations.
- `requirements.txt`: Lists Python dependencies.
- `data/`: Contains job descriptions and CVs.

## Notes
- Ensure you have a valid Gemini API key for the application.
- Do not push the `.env` file or database file to GitHub.

## License
This project is licensed under the MIT License.
