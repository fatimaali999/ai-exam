import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure the API key safely from Vercel's Environment Settings
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "AI Exam API is running"}), 200

@app.route('/api/generate-questions', methods=['POST', 'GET'])
@app.route('/generate-questions', methods=['POST', 'GET'])
def generate_questions():
    try:
        # Check if the API key was correctly injected in the environment settings
        if not os.environ.get("GEMINI_API_KEY"):
            return jsonify({"success": False, "error": "API Key is missing in Vercel settings"}), 500
        
        # Handle both GET and POST requests
        if request.method == 'GET':
            student_notes = request.args.get('notes', 'No study notes provided.')
        else:
            # Safely parse incoming payload data sent from your React app
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
        
        # Call the available Gemini model with fallback chain
        response = None
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
        except:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                except Exception as e:
                    raise Exception(f"All Gemini models failed: {str(e)}")
        
        return jsonify({
            "success": True,
            "questions": response.text
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/grade-answer', methods=['POST', 'GET'])
@app.route('/grade-answer', methods=['POST', 'GET'])
def grade_answer():
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            return jsonify({"success": False, "error": "API Key configuration missing"}), 500
            
        # Handle both GET and POST requests
        if request.method == 'GET':
            question = request.args.get('question', '')
            student_answer = request.args.get('answer', '')
        else:
            data = request.get_json() or {}
            question = data.get('question', '')
            student_answer = data.get('answer', '')
        
        # Grading prompt design template
        prompt = (
            f"You are an academic assessor grading an exam question.\n"
            f"Question: {question}\n"
            f"Student's Answer: {student_answer}\n\n"
            f"Tasks:\n"
            f"1. Score the answer out of 100 points.\n"
            f"2. Provide a 2-3 sentence candid explanation detailing what critical data points were missing or correct.\n\n"
            f"Response format constraint: Return your response ONLY as a valid JSON object matching this structure:\n"
            f'{{"score": 85, "explanation": "Your explanation goes here"}}'
        )
        
        # Grading model with fallback chain
        response = None
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
        except:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                except Exception as e:
                    raise Exception(f"All Gemini models failed: {str(e)}")
        
        return jsonify({
            "success": True,
            "evaluation": response.text
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500