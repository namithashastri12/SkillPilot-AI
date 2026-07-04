"""Resume Analysis Agent — extracts skills + improvement suggestions from a resume."""
from agents import gemini_client
from agents.knowledge_base import RESUME_KEYWORDS


class ResumeAnalysisAgent:
    name = "resume_analysis_agent"

    def analyze(self, raw_text: str):
        system = (
            "You are the Resume Analysis Agent inside SkillPilot AI, a multi-agent "
            "career mentor system. Extract a clean list of technical/professional "
            "skills present in the resume, and give 4-6 concrete, specific "
            "improvement suggestions (formatting, quantifying impact, missing "
            "sections, weak bullet points, keyword gaps for ATS). "
            "Respond ONLY as JSON: {\"skills\": [...], \"suggestions\": [...]}"
        )
        prompt = f"Resume text:\n---\n{raw_text[:6000]}\n---"

        def mock_fn():
            return self._mock_analyze(raw_text)

        result = gemini_client.generate(prompt, system=system, json_mode=True, mock_fn=mock_fn)
        if not isinstance(result, dict) or "skills" not in result:
            result = self._mock_analyze(raw_text)
        result["skills"] = sorted(set(s.strip() for s in result.get("skills", []) if s.strip()))
        return result

    @staticmethod
    def _mock_analyze(raw_text: str):
        text_lower = raw_text.lower()
        found = [kw.title() if len(kw) > 3 else kw.upper() for kw in RESUME_KEYWORDS if kw in text_lower]

        suggestions = []
        word_count = len(raw_text.split())

        if word_count < 150:
            suggestions.append("Resume looks quite short — add more detail on projects and measurable outcomes.")
        if "%" not in raw_text and not any(ch.isdigit() for ch in raw_text):
            suggestions.append("Quantify your impact with numbers (e.g. 'reduced load time by 30%', 'served 500+ users').")
        if "project" not in text_lower:
            suggestions.append("Add a dedicated Projects section — recruiters weigh hands-on projects heavily for students.")
        if "education" not in text_lower:
            suggestions.append("Add an Education section with your degree, institution, and graduation year.")
        if len(found) < 5:
            suggestions.append("List more specific technical skills/tools to improve ATS keyword matching.")
        if "@" not in raw_text:
            suggestions.append("Make sure your contact email is clearly visible near the top.")
        if not suggestions:
            suggestions.append("Strong resume overall — focus on tailoring bullet points to each job description's keywords.")

        return {"skills": found, "suggestions": suggestions[:6]}
