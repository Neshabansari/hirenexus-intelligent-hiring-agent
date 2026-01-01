import re
import io
import json
import PyPDF2
import google.genai as genai


class ResumeAnalysisAgent:
    def __init__(self, api_key, cutoff_score=75):
        self.cutoff_score = cutoff_score
        self.client = genai.Client(api_key=api_key)

        self.resume_text = None
        self.jd_text = None
        self.analysis_result = None
        self.resume_weaknesses = []

    # -------------------- FILE HANDLING --------------------

    def extract_text_from_pdf(self, pdf_file):
        try:
            if hasattr(pdf_file, "getvalue"):
                reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
            else:
                reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            print("PDF extraction error:", e)
            return ""

    def extract_text_from_file(self, file):
        if hasattr(file, "name"):
            ext = file.name.split(".")[-1].lower()
        else:
            ext = file.split(".")[-1].lower()

        if ext == "pdf":
            return self.extract_text_from_pdf(file)
        elif ext == "txt":
            return file.getvalue().decode("utf-8")
        return ""

    # -------------------- INTERNAL HELPER --------------------

    def _clean_json(self, text):
        """Safely extract JSON from Gemini output"""
        text = text.strip()
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No valid JSON found in Gemini response")
        return json.loads(match.group())

    # -------------------- CORE ANALYSIS --------------------

    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        self.resume_text = self.extract_text_from_file(resume_file)

        if not self.resume_text:
            raise ValueError("Resume text could not be extracted")

        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            skill_context = self.jd_text
        else:
            skill_context = ", ".join(role_requirements or [])

        prompt = f"""
You are an intelligent hiring assistant.

Analyze the resume against the job requirements.

Resume:
{self.resume_text}

Job Requirements:
{skill_context}

Return ONLY valid JSON:

{{
  "overall_score": 0-100,
  "selected": true/false,
  "strengths": ["skill1", "skill2"],
  "missing_skills": ["skillA", "skillB"],
  "reasoning": "short explanation",
  "detailed_weaknesses": [
    {{
      "skill": "skill name",
      "score": 0-10,
      "detail": "what is missing",
      "suggestions": ["suggestion1", "suggestion2"],
      "example": "example resume bullet"
    }}
  ]
}}
"""

        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        data = self._clean_json(response.text)

        self.analysis_result = data
        self.resume_weaknesses = data.get("detailed_weaknesses", [])
        return data

    # -------------------- RESUME Q&A --------------------

    def ask_question(self, question):
        if not self.resume_text:
            return "Please analyze a resume first."

        prompt = f"""
Answer strictly based on the resume.

Resume:
{self.resume_text}

Question:
{question}
"""

        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text.strip()

    # -------------------- INTERVIEW QUESTIONS --------------------

    def generate_interview_questions(self, question_types, difficulty, num_questions):
        if not self.resume_text:
            return []

        prompt = f"""
Generate {num_questions} {difficulty} interview questions.

Question Types: {", ".join(question_types)}

Resume:
{self.resume_text}

Return as:
("Type", "Question")
"""

        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        matches = re.findall(r'\("([^"]+)",\s*"([^"]+)"\)', response.text)
        return matches[:num_questions]

    # -------------------- RESUME IMPROVEMENTS --------------------

    def improve_resume(self, improvement_areas, target_role=""):
        if not self.resume_text:
            return {}

        prompt = f"""
Improve the resume for these areas:
{", ".join(improvement_areas)}

Target Role: {target_role}

Resume:
{self.resume_text}

Return ONLY JSON:
{{
  "Area": {{
    "description": "...",
    "specific": ["point1", "point2"]
  }}
}}
"""

        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        return self._clean_json(response.text)

    # -------------------- FULL RESUME REWRITE --------------------

    def get_improved_resume(self, target_role="", highlight_skills=""):
        if not self.resume_text:
            return "Please analyze a resume first."

        prompt = f"""
Rewrite this resume professionally.

Target Role: {target_role}
Skills to highlight: {highlight_skills}

Resume:
{self.resume_text}

Return ONLY the improved resume text.
"""

        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        return response.text.strip()

    # -------------------- CLEANUP --------------------

    def cleanup(self):
        pass
