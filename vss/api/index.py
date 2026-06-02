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

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        # Check if the API key was correctly injected in the environment settings
        if not os.environ.get("GEMINI_API_KEY"):
            return jsonify({"success": False, "error": "API Key is missing in Vercel settings"}), 500
            
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
        
        # Call the classic serverless-stable model wrapper
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return jsonify({
            "success": True,
            "questions": response.text
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500