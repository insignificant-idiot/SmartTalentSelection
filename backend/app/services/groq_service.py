import json
import re
import requests
from app.core.config import LOCAL_LLM_URL, LOCAL_LLM_MODEL

def _call_local_llm(prompt: str, temperature: float = 0.0) -> str:
    """Send prompt to Ollama and return the response text."""
    url = f"{LOCAL_LLM_URL}/api/generate"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "options": {
            "num_predict": 512
        }
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Local LLM request failed: {e}")

def extract_profile(text: str) -> dict:
    prompt = f"""
You are an expert resume parser and information extraction system.

TASK:
Analyze the resume below and extract structured information into a JSON object.

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON.
2. Do NOT include markdown, explanations, comments, or code fences.
3. Use the exact schema provided.
4. If a field cannot be determined, use the specified fallback value.
5. Extract information only from the resume content. Do not invent data.

FIELD DEFINITIONS:

"name":
- Candidate's full name.
- Prefer the most prominent name near the top of the resume.
- Include first and last name when available.
- Exclude job titles, email addresses, and company names.
- If no clear name is found, use "Unknown".

"skills":
- List all technical, professional, and domain skills.
- Include programming languages, frameworks, tools, platforms, databases, cloud technologies, methodologies, and relevant business skills.
- Remove duplicates.
- Return as an array of strings.

"years_experience":
- Estimate total professional experience in years.
- Calculate from employment history when possible.
- Use the difference between earliest relevant professional role and most recent role.
- Round to the nearest whole number.
- If experience cannot be determined, return 0.

"experience":
- Extract all professional work experiences.
- Include employment, internships, consulting, freelance, and contract work when clearly identified.
- Return as an array of objects.
- For each experience include:
  {{
    "title": "",
    "company": "",
    "start_date": "",
    "end_date": "",
    "description": ""
  }}
- Preserve date formats as shown in the resume when possible.
- Use "Present" if currently employed.
- If a value is unavailable, use an empty string.

"projects":
- Extract notable personal, academic, freelance, open-source, or professional projects.
- Return as an array of objects:
  {{
    "name": "",
    "description": "",
    "technologies": []
  }}
- Include technologies explicitly mentioned in the project.
- If none exist, return [].

"certifications":
- Extract certifications, licenses, certificates, and professional credentials.
- Return as an array of strings.
- Include issuer name if clearly stated.

NORMALIZATION RULES:
- Remove duplicate entries.
- Ignore contact information unless needed to identify the candidate name.
- Ignore references and generic resume sections.
- Preserve capitalization for names, companies, technologies, and certifications.
- Do not infer certifications, projects, or skills that are not mentioned.

OUTPUT SCHEMA:
{{
    "name": "",
    "skills": [],
    "years_experience": 0,
    "experience": [],
    "projects": [],
    "certifications": []
}}

Resume:
{text[:12000]}
"""
    content = _call_local_llm(prompt, temperature=0.0)
    # Remove markdown code fences if present
    content = re.sub(r"^```json|^```|```$", "", content, flags=re.MULTILINE).strip()
    try:
        profile = json.loads(content)
        # Ensure required fields exist
        if not profile.get("name"):
            profile["name"] = _extract_name_from_text(text)
        return profile
    except json.JSONDecodeError:
        # Fallback: create minimal profile
        return {
            "name": _extract_name_from_text(text),
            "skills": [],
            "years_experience": 0,
            "experience": [],
            "projects": [],
            "certifications": []
        }

def _extract_name_from_text(text: str) -> str:
    """Extract name from resume text using simple heuristics."""
    # Look for common patterns: "Name: ..." or the first line that looks like a name
    lines = text.split('\n')
    for line in lines[:10]:  # check first 10 lines
        line = line.strip()
        # Pattern: "Name: John Doe"
        name_match = re.search(r'Name\s*:\s*([A-Za-z\s\.]+)', line, re.IGNORECASE)
        if name_match:
            return name_match.group(1).strip()
        # If line is short (2-4 words) and contains only letters, spaces, dots, it might be a name
        if len(line.split()) in [2,3,4] and re.match(r'^[A-Za-z\.\s]+$', line):
            # Exclude common non-name lines
            if not re.search(r'(email|phone|contact|address|linkedin|github)', line, re.IGNORECASE):
                return line
    # If still nothing, return a default
    return "Unknown"

def generate_justification(jd: str, profile: str) -> str:
    prompt = f"""
You are an expert technical recruiter evaluating candidate-job fit.

TASK:
Given a job description and a candidate profile, explain why the candidate is a strong match.

STRICT RULES:
1. Use ONLY information present in the Job Description and Candidate Profile.
2. Do NOT invent skills, experience, or achievements.
3. Be precise, technical, and evidence-based.
4. Keep the answer to exactly 2 sentences.
5. Focus on direct skill/experience alignment with the job requirements.
6. Prefer specific technologies, domains, and role overlap over generic praise.

OUTPUT FORMAT:
- Exactly 2 sentences
- No bullet points
- No headings
- No extra commentary

EVALUATION GUIDELINES:
- Match must be based on: skills, tools, domain experience, years of experience, or relevant projects.
- Mention the most important overlaps first.
- If multiple strong matches exist, prioritize the most critical job requirements.

Job Description:
{jd}

Candidate Profile:
{profile}
"""
    return _call_local_llm(prompt, temperature=0.2)