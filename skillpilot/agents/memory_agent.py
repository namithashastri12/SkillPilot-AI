"""Memory & Progress Agent — persists context across sessions and reports on trends."""
from database import db


class MemoryProgressAgent:
    name = "memory_progress_agent"

    def remember_session(self, student_id, key, value):
        db.remember(student_id, self.name, key, value)

    def recall_session(self, student_id, key, default=None):
        return db.recall(student_id, self.name, key, default)

    def log_roadmap_as_milestones(self, student_id, roadmap):
        """Seed the progress log with milestones from a freshly generated roadmap."""
        phases = roadmap.get("phases", [])
        for phase in phases:
            weeks = phase.get("weeks", "")
            try:
                week_number = int(weeks.split("-")[0])
            except Exception:
                week_number = 1
            db.upsert_progress(
                student_id,
                week_number,
                f"{phase['phase']}: {phase.get('milestone', '')[:80]}",
                status="pending",
            )

    def readiness_insight(self, student_id, readiness_score, missing_skills_count):
        progress = db.get_progress(student_id)
        done = len([p for p in progress if p["status"] == "done"])
        total = len(progress) or 1
        completion_pct = round((done / total) * 100)

        if readiness_score >= 80:
            tone = "You're close to hire-ready — focus on interview polish and networking."
        elif readiness_score >= 50:
            tone = "Solid foundation. Stay consistent on your roadmap and you'll close the gap fast."
        else:
            tone = "Early stage — that's fine. Prioritize the Foundations phase before jumping to projects."

        return {
            "readiness_score": readiness_score,
            "missing_skills_count": missing_skills_count,
            "milestones_completed_pct": completion_pct,
            "milestones_total": total,
            "milestones_done": done,
            "insight": tone,
        }
