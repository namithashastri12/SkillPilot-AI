"""
Planner Agent — the orchestrator of SkillPilot AI's multi-agent system.

This is the entry point the Flask API talks to. It coordinates:
  ResumeAnalysisAgent -> SkillAnalysisAgent -> GoalMappingAgent
  -> RoadmapAgent -> RecommendationAgent -> MemoryProgressAgent

Each sub-agent is a small, focused module (single responsibility), and the
Planner is responsible for sequencing them and passing state between them —
mirroring a real Google ADK multi-agent workflow (planner/orchestrator agent
delegating to specialist sub-agents, each with their own tools/memory).
"""
from agents.resume_agent import ResumeAnalysisAgent
from agents.skill_goal_agents import GoalMappingAgent, SkillAnalysisAgent
from agents.roadmap_agent import RoadmapAgent
from agents.recommendation_agent import RecommendationAgent
from agents.memory_agent import MemoryProgressAgent
from agents import gemini_client
from database import db


class PlannerAgent:
    name = "planner_agent"

    def __init__(self):
        self.resume_agent = ResumeAnalysisAgent()
        self.goal_agent = GoalMappingAgent()
        self.skill_agent = SkillAnalysisAgent()
        self.roadmap_agent = RoadmapAgent()
        self.recommendation_agent = RecommendationAgent()
        self.memory_agent = MemoryProgressAgent()

    def system_status(self):
        return gemini_client.status()

    # ---- Step 1: resume ingestion ----
    def process_resume(self, student_id, filename, raw_text):
        analysis = self.resume_agent.analyze(raw_text)
        db.save_resume(student_id, filename, raw_text, analysis["skills"], analysis["suggestions"])
        self.memory_agent.remember_session(student_id, "last_resume_skills", analysis["skills"])
        return analysis

    # ---- Step 2: full guidance pipeline (goal -> gap -> roadmap -> recs -> memory) ----
    def run_full_pipeline(self, student_id, target_role, have_skills, weeks_available=12):
        required_skills = self.goal_agent.required_skills(target_role)
        gap = self.skill_agent.analyze_gap(have_skills, required_skills)
        db.save_skill_gap(
            student_id, target_role, gap["have_skills"], gap["missing_skills"], gap["readiness_score"]
        )

        roadmap = self.roadmap_agent.generate(target_role, gap["missing_skills"], weeks_available)
        db.save_roadmap(student_id, target_role, roadmap)
        self.memory_agent.log_roadmap_as_milestones(student_id, roadmap)

        recs = self.recommendation_agent.recommend(target_role, gap["missing_skills"])
        db.save_recommendations(student_id, recs["courses"], recs["projects"])

        insight = self.memory_agent.readiness_insight(
            student_id, gap["readiness_score"], len(gap["missing_skills"])
        )

        self.memory_agent.remember_session(student_id, "last_target_role", target_role)
        self.memory_agent.remember_session(student_id, "required_skills", required_skills)

        return {
            "required_skills": required_skills,
            "gap": gap,
            "roadmap": roadmap,
            "recommendations": recs,
            "insight": insight,
        }

    # ---- Dashboard: assemble everything already known about a student ----
    def get_dashboard(self, student_id):
        student = db.get_student(student_id)
        resume = db.latest_resume(student_id)
        gap = db.latest_skill_gap(student_id)
        roadmap = db.latest_roadmap(student_id)
        recs = db.latest_recommendations(student_id)
        progress = db.get_progress(student_id)

        import json as _json
        return {
            "student": student,
            "resume": {
                **resume,
                "extracted_skills": _json.loads(resume["extracted_skills"]),
                "suggestions": _json.loads(resume["suggestions"]),
            } if resume else None,
            "skill_gap": {
                **gap,
                "have_skills": _json.loads(gap["have_skills"]),
                "missing_skills": _json.loads(gap["missing_skills"]),
            } if gap else None,
            "roadmap": {
                **roadmap,
                "roadmap": _json.loads(roadmap["roadmap_json"]),
            } if roadmap else None,
            "recommendations": {
                "courses": _json.loads(recs["courses_json"]),
                "projects": _json.loads(recs["projects_json"]),
            } if recs else None,
            "progress": progress,
        }
