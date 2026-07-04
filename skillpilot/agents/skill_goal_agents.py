"""Goal Mapping Agent + Skill Analysis Agent."""
from agents import gemini_client
from agents.knowledge_base import ROLE_SKILLS, GENERIC_ROLE_SKILLS


class GoalMappingAgent:
    """Maps a target career goal to the concrete skill set required for it."""
    name = "goal_mapping_agent"

    def required_skills(self, target_role: str):
        if target_role in ROLE_SKILLS:
            return ROLE_SKILLS[target_role]

        system = (
            "You are the Goal Mapping Agent inside SkillPilot AI. Given a student's "
            "target career role, return the 8-10 most important, concrete skills "
            "required to be hire-ready for that role. Respond ONLY as JSON: "
            "{\"skills\": [...]}"
        )
        prompt = f"Target role: {target_role}"

        def mock_fn():
            return {"skills": GENERIC_ROLE_SKILLS}

        result = gemini_client.generate(prompt, system=system, json_mode=True, mock_fn=mock_fn)
        skills = result.get("skills") if isinstance(result, dict) else None
        return skills or GENERIC_ROLE_SKILLS


class SkillAnalysisAgent:
    """Compares skills the student has vs skills the goal requires -> gap + readiness score."""
    name = "skill_analysis_agent"

    def analyze_gap(self, have_skills, required_skills):
        have_norm = {s.strip().lower() for s in have_skills}

        def matches(req_skill):
            req_lower = req_skill.lower()
            # loose match: any overlapping token counts as "have"
            for h in have_norm:
                if h in req_lower or req_lower in h:
                    return True
                if set(h.split()) & set(req_lower.replace("/", " ").split()):
                    return True
            return False

        matched = [r for r in required_skills if matches(r)]
        missing = [r for r in required_skills if r not in matched]

        readiness_score = round((len(matched) / len(required_skills)) * 100) if required_skills else 0

        return {
            "have_skills": matched,
            "missing_skills": missing,
            "readiness_score": readiness_score,
        }
