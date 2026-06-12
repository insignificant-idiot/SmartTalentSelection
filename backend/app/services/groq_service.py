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
Analyze the following resume and extract the information into a JSON object.

IMPORTANT: The 'name' field must contain the full name of the candidate. If you cannot find a name, use "Unknown".

Return ONLY valid JSON in exactly this format:
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
Job Description:
{jd}

Candidate Profile:
{profile}

Explain in 2 short sentences why this candidate is a strong match.
Be precise and technical.
"""
    return _call_local_llm(prompt, temperature=0.2)