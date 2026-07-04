"""Roadmap Agent — turns a skill gap into a structured, phased weekly roadmap."""
import math
from agents import gemini_client


class RoadmapAgent:
    name = "roadmap_agent"

    def generate(self, target_role: str, missing_skills, weeks_available: int = 12):
        system = (
            "You are the Roadmap Agent inside SkillPilot AI. Build a phased, "
            "week-by-week learning roadmap for a student to close their skill "
            "gaps for a target role. Group skills into logical phases "
            "(Foundations, Core Skills, Applied/Projects, Interview Prep). "
            "Respond ONLY as JSON: {\"phases\": [{\"phase\": str, "
            "\"weeks\": \"1-3\", \"focus_skills\": [...], \"milestone\": str}]}"
        )
        prompt = (
            f"Target role: {target_role}\n"
            f"Missing skills to close: {missing_skills}\n"
            f"Total weeks available: {weeks_available}"
        )

        def mock_fn():
            return self._mock_roadmap(target_role, missing_skills, weeks_available)

        result = gemini_client.generate(prompt, system=system, json_mode=True, mock_fn=mock_fn)
        if not isinstance(result, dict) or "phases" not in result or not result["phases"]:
            result = self._mock_roadmap(target_role, missing_skills, weeks_available)
        return result

    @staticmethod
    def _mock_roadmap(target_role, missing_skills, weeks_available):
        if not missing_skills:
            missing_skills = ["Portfolio polish", "Mock interviews", "Networking"]

        n = len(missing_skills)
        phase_defs = [
            ("Foundations", 0.3, "Get comfortable with the fundamentals before going deeper."),
            ("Core Skills", 0.4, "Build real depth in the skills that matter most for this role."),
            ("Applied / Projects", 0.2, "Prove the skills with a portfolio-ready project."),
            ("Interview Prep", 0.1, "Sharpen resume, mock interviews, and behavioral prep."),
        ]

        phases = []
        week_cursor = 1
        skill_cursor = 0
        for i, (phase_name, frac, blurb) in enumerate(phase_defs):
            phase_weeks = max(1, round(weeks_available * frac))
            if i == len(phase_defs) - 1:
                phase_weeks = max(1, weeks_available - (week_cursor - 1))
            end_week = min(weeks_available, week_cursor + phase_weeks - 1)

            if phase_name == "Interview Prep":
                focus = ["Mock interviews", "Resume tailoring", "Behavioral stories (STAR method)"]
            elif phase_name == "Applied / Projects":
                focus = ["Capstone/portfolio project", "Code review & polish", "Deploy + document project"]
            else:
                take = max(1, math.ceil(n * frac))
                focus = missing_skills[skill_cursor: skill_cursor + take] or ["Review & consolidate"]
                skill_cursor += take

            phases.append({
                "phase": phase_name,
                "weeks": f"{week_cursor}-{end_week}",
                "focus_skills": focus,
                "milestone": f"{blurb} Milestone: demonstrate progress in {', '.join(focus[:2])}.",
            })
            week_cursor = end_week + 1
            if week_cursor > weeks_available:
                break

        return {"phases": phases}
