import numpy as np
import json
import re
from typing import List, Set

from app.services.embedding_service import create_embedding
from app.core.chroma import collection
from app.services.groq_service import generate_justification


SKILL_SET = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin",
    # Web & Frontend
    "react", "vue", "angular", "nextjs", "nuxt", "html", "css", "tailwind", "bootstrap", "sass", "webpack", "vite",
    # Backend & Databases
    "django", "flask", "fastapi", "express", "nodejs", "spring", "asp.net", "sql", "mysql", "postgresql", "mongodb",
    "sqlite", "redis", "firebase",
    # AI/ML & Data
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow", "scikit-learn",
    "pandas", "numpy", "langchain", "rag", "generative ai", "llm", "openai", "groq", "chromadb",
    "sentence transformers", "yolo", "opencv", "pytesseract", "ocr",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "github actions", "ci/cd", "terraform",
    # Tools & Misc
    "git", "github", "postman", "jira", "figma", "rest api", "graphql", "jwt", "oauth"
}


def extract_skills_from_text(text: str) -> Set[str]:
    """Extract skills from a text using a predefined keyword set."""
    text_lower = text.lower()
    found = set()
    for skill in SKILL_SET:
        # Use word boundary for exact matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def compute_skill_overlap(candidate_skills: List[str], jd_skills: Set[str]) -> float:
    """Overlap score = number of common skills / total candidate skills."""
    candidate_set = set(s.lower() for s in candidate_skills)
    if not candidate_set:
        return 0.0
    common = candidate_set.intersection(jd_skills)
    return len(common) / len(candidate_set)


def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search_candidates(jd_text):
    jd_embedding = create_embedding(jd_text)
    results = collection.query(
        query_embeddings=[jd_embedding],
        n_results=50
    )
    return results


def rank_candidates(jd_text: str, resumes_data: list) -> list:
    """
    resumes_data: list of dicts with keys:
        resume_id, profile_text (JSON string), years_experience, embedding
    """
    jd_embedding = create_embedding(jd_text)
    jd_skills = extract_skills_from_text(jd_text)

    ranked = []
    for resume in resumes_data:
        embedding = resume["embedding"]
        similarity = cosine_sim(jd_embedding, embedding)

        years = resume.get("years_experience", 0)
        experience_score = min(years / 10, 1)

        # Parse profile JSON to get name and skills
        profile_json = resume.get("profile_text")
        name = None
        candidate_skills = []
        if profile_json:
            try:
                profile = json.loads(profile_json)
                name = profile.get("name") or "Unknown"
                candidate_skills = profile.get("skills", [])
            except json.JSONDecodeError:
                name = "Unknown"

        skill_overlap = compute_skill_overlap(candidate_skills, jd_skills)

        # Get top_skills from resume (already stored as comma-separated)
        top_skills = resume.get("top_skills")  # we'll need to pass this from ranking.py

        justification = generate_justification(jd_text, profile_json or "")

        final_score = (
            similarity * 0.7 +
            experience_score * 0.2 +
            skill_overlap * 0.1
        )

        ranked.append({
            "resume_id": resume["resume_id"],
            "score": round(final_score * 100, 2),
            "justification": justification,
            "name": name,
            "top_skills": top_skills,
            "years_experience": years,
        })

    return sorted(ranked, key=lambda x: x["score"], reverse=True)