import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import psycopg2

app = Flask(__name__)
CORS(app)

# Configure the API key safely from Vercel's Environment Settings
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Diagnostic helper
@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "AI Exam API is running"}), 200

@app.route('/api/generate-questions/', methods=['POST'])
def generate_questions():
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            return jsonify({"success": False, "error": "API Key is missing in Vercel settings"}), 500
            
        data = request.get_json() or {}
        student_notes = data.get('notes', 'No study notes provided.')
        
        prompt = (
            f"You are an expert academic examiner. Read the following student study notes carefully. "
            f"Generate exactly 10 distinct, exam-style test questions based purely on this content.\n\n"
            f"Constraints:\n"
            f"- Return your final output ONLY as a valid JSON array of strings.\n"
            f"- Do not include markdown formatting like ```json or wrappers. Just the raw array.\n\n"
            f"Student Notes:\n{student_notes}"
        )
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # CLEANUP LAYER: Remove any backticks or markdown words the AI might append
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            # Strip out opening block lines like ```json or ```
            raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            # Strip out closing block lines
            raw_text = raw_text.rsplit("\n", 1)[0]
        cleaned_text = raw_text.strip()
        
        # Verify it can be read as structural JSON before sending to frontend
        try:
            json_check = json.loads(cleaned_text)
            return jsonify({
                "success": True,
                "questions": json.dumps(json_check)
            }), 200
        except Exception:
            # Fallback if text is structured but has subtle formatting loose ends
            return jsonify({
                "success": True,
                "questions": cleaned_text
            }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/grade-answer/', methods=['POST'])
def grade_answer():
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            return jsonify({"success": False, "error": "API Key configuration missing"}), 500
            
        data = request.get_json() or {}
        question = data.get('question', '')
        student_answer = data.get('answer', '')
        
        prompt = (
            f"You are an academic assessor grading an exam question.\n"
            f"Question: {question}\n"
            f"Student's Answer: {student_answer}\n\n"
            f"Tasks:\n"
            f"1. Score the answer out of 100 points.\n"
            f"2. Provide a 2-3 sentence explanation detailing what critical data points were missing or correct.\n\n"
            f"Response format constraint: Return your response ONLY as a valid JSON object matching this structure:\n"
            f'{{"score": 85, "explanation": "Your explanation goes here"}}'
        )
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("\n", 1)[0]
        cleaned_text = raw_text.strip()
        
        # --- DATABASE INTERACTION LAYER ---
        try:
            # Extract the score safely from Gemini's JSON response
            evaluation_data = json.loads(cleaned_text)
            final_score = int(evaluation_data.get("score", 0))
            
            # Connect to Vercel Postgres using the environment variable automatically provided
            postgres_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
            if postgres_url:
                conn = psycopg2.connect(postgres_url)
                cursor = conn.cursor()
                
                # Create the history table seamlessly if it hasn't been created yet
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exam_history (
                        id SERIAL PRIMARY KEY,
                        score INTEGER,
                        date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                
                # Insert the numeric score safely to avoid security vulnerabilities
                cursor.execute(
                    "INSERT INTO exam_history (score) VALUES (%s);", 
                    (final_score,)
                )
                
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as db_err:
            # If the database fails for any reason, print the error but DO NOT crash the app,
            # ensuring the student still gets their grade on screen.
            print("Database tracking error logged:", str(db_err))
        # ----------------------------------
        
        return jsonify({
            "success": True,
            "evaluation": cleaned_text
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500