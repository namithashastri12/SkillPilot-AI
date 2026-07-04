"""Course & Project Recommendation Agent."""
from agents import gemini_client
from agents.knowledge_base import COURSE_LIBRARY, PROJECT_LIBRARY


class RecommendationAgent:
    name = "recommendation_agent"

    def recommend(self, target_role: str, missing_skills):
        system = (
            "You are the Course & Project Recommendation Agent inside SkillPilot AI. "
            "Given missing skills and a target role, recommend specific courses "
            "(title, provider, level) for the top skills, and 2-3 portfolio project "
            "ideas tailored to the target role. Respond ONLY as JSON: "
            "{\"courses\": [{\"skill\": str, \"title\": str, \"provider\": str, \"level\": str}], "
            "\"projects\": [str]}"
        )
        prompt = f"Target role: {target_role}\nMissing skills: {missing_skills}"

        def mock_fn():
            return self._mock_recommend(target_role, missing_skills)

        result = gemini_client.generate(prompt, system=system, json_mode=True, mock_fn=mock_fn)
        if not isinstance(result, dict) or not result.get("courses"):
            result = self._mock_recommend(target_role, missing_skills)
        return result

    @staticmethod
    def _mock_recommend(target_role, missing_skills):
        courses = []
        for skill in missing_skills:
            options = COURSE_LIBRARY.get(skill)
            if not options:
                # fuzzy fallback: partial key match
                for key, opts in COURSE_LIBRARY.items():
                    if key.lower() in skill.lower() or skill.lower() in key.lower():
                        options = opts
                        break
            if options:
                for opt in options[:1]:
                    courses.append({"skill": skill, **opt})
            else:
                courses.append({
                    "skill": skill,
                    "title": f"Search: '{skill} for beginners'",
                    "provider": "Coursera / YouTube / freeCodeCamp",
                    "level": "Beginner",
                })

        projects = PROJECT_LIBRARY.get(target_role, [
            "Build and deploy a small end-to-end project that showcases 2-3 of your target skills",
            "Contribute to an open-source project relevant to your target role",
        ])
        return {"courses": courses, "projects": projects}
