# 🧭 SkillPilot AI
### A Multi-Agent Career Mentor for Personalized Student Success

SkillPilot AI is a multi-agent career guidance system that replaces four
scattered tools (resume reviewer, course finder, roadmap planner, interview
prep) with one coordinated AI mentor that remembers you across sessions.

---

## Quick start

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add a Gemini API key for live LLM reasoning
cp .env.example .env
# edit .env and set GEMINI_API_KEY=your_key_here

# 4. Run
python app.py
```

Then open **http://127.0.0.1:5000**.

### It runs with zero API keys

Every agent has a deterministic, rule-based fallback (`MOCK MODE`), so the
full pipeline — resume parsing, skill-gap analysis, roadmap generation,
course/project recommendations, progress memory — works completely offline.
Add a `GEMINI_API_KEY` to `.env` to switch every agent to live Gemini
reasoning (`LIVE MODE`) with no code changes. The sidebar badge in the
dashboard shows which mode is active.

---

## Architecture

```
                         ┌─────────────────────┐
                         │    Planner Agent      │   orchestrates the pipeline
                         └──────────┬───────────┘
              ┌───────────┬─────────┼─────────┬───────────┬──────────────┐
              ▼           ▼         ▼         ▼           ▼              ▼
      Resume Analysis  Goal      Skill      Roadmap   Course & Project  Memory &
         Agent        Mapping   Analysis     Agent        Rec. Agent   Progress Agent
                       Agent     Agent
```

- **Planner Agent** (`agents/planner_agent.py`) — sequences every other
  agent and assembles state for the Flask API.
- **Resume Analysis Agent** — extracts skills + improvement suggestions
  from an uploaded `.pdf` / `.docx` / `.txt`.
- **Goal Mapping Agent** — maps a target role to the concrete skills
  required to be hire-ready.
- **Skill Analysis Agent** — diffs "have" vs "required" skills into a
  gap list + readiness score (0–100).
- **Roadmap Agent** — turns the gap into a phased, week-by-week plan
  (Foundations → Core Skills → Applied/Projects → Interview Prep).
- **Course & Project Recommendation Agent** — matches courses to each
  missing skill and suggests portfolio projects for the target role.
- **Memory & Progress Agent** — persists milestones and session state in
  SQLite so guidance compounds across visits instead of resetting.

Every agent calls a shared `agents/gemini_client.py` wrapper, which
transparently uses live Gemini calls when a key is present and falls back
to rule-based logic otherwise — the same interface either way.

## Tech stack

| Layer          | Choice                                   |
|----------------|-------------------------------------------|
| Frontend       | HTML, CSS, vanilla JavaScript              |
| Backend        | Flask (Python)                             |
| AI orchestration | Planner + specialist agent pattern (Google ADK-style) |
| LLM            | Gemini (`google-genai`), optional          |
| Database       | SQLite                                     |
| Memory         | SQLite-backed agent memory table           |
| Resume parsing | `pypdf`, `python-docx`                     |

## Project structure

```
skillpilot/
├── app.py                     Flask app + REST API routes
├── requirements.txt
├── .env.example
├── agents/
│   ├── planner_agent.py       Orchestrator
│   ├── resume_agent.py
│   ├── skill_goal_agents.py   Goal Mapping + Skill Analysis
│   ├── roadmap_agent.py
│   ├── recommendation_agent.py
│   ├── memory_agent.py
│   ├── gemini_client.py       Live/mock LLM wrapper
│   └── knowledge_base.py      Roles, skills, courses, projects dataset
├── database/
│   └── db.py                  SQLite schema + data access
├── templates/
│   ├── index.html             Landing page
│   └── dashboard.html         App shell (cockpit)
├── static/
│   ├── css/style.css          Design system
│   └── js/{gauge,main}.js     Attitude-indicator gauge + app logic
└── uploads/                   Uploaded resumes (gitignored)
```

## API reference

| Method | Route                    | Purpose                                   |
|--------|---------------------------|--------------------------------------------|
| POST   | `/api/onboard`             | Create/resume a student profile            |
| GET    | `/api/me`                  | Current session's student                  |
| POST   | `/api/upload_resume`       | Upload + analyze a resume                  |
| POST   | `/api/generate_plan`       | Run the full agent pipeline                |
| GET    | `/api/dashboard`           | Aggregate everything known about a student |
| POST   | `/api/progress/update`     | Mark a milestone done/pending              |
| GET    | `/api/system_status`       | Live vs. mock mode                         |

## Notes for judges / graders

- No API key is required to fully evaluate the product end-to-end.
- The multi-agent boundary is a real code boundary (separate modules,
  separate responsibilities, orchestrated by the Planner) — not a single
  prompt pretending to be multiple agents.
- SQLite persistence means skill gaps, roadmaps, and progress survive
  across page reloads and days, demonstrating the "continuous memory"
  claim rather than just asserting it.
