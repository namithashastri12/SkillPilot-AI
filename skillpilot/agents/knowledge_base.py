"""
SkillPilot AI — Knowledge base.

Small curated dataset the agents ground themselves on. In LIVE mode this is
passed to Gemini as context; in MOCK mode it powers the rule-based fallback
directly so the app is fully functional offline.
"""

ROLE_SKILLS = {
    "Software Engineer": [
        "Data Structures & Algorithms", "Python", "Git", "SQL", "System Design",
        "REST APIs", "Testing & Debugging", "OOP", "Linux/CLI", "Cloud Basics (AWS/GCP)",
    ],
    "Data Analyst": [
        "SQL", "Python", "Excel", "Statistics", "Data Visualization",
        "Power BI/Tableau", "Pandas", "A/B Testing", "Storytelling with Data",
    ],
    "Data Scientist": [
        "Python", "Statistics", "Machine Learning", "SQL", "Pandas/NumPy",
        "Model Evaluation", "Data Visualization", "Deep Learning Basics", "MLOps Basics",
    ],
    "Machine Learning Engineer": [
        "Python", "Machine Learning", "Deep Learning", "PyTorch/TensorFlow", "SQL",
        "Model Deployment", "MLOps", "System Design", "Cloud Basics (AWS/GCP)", "Data Structures & Algorithms",
    ],
    "Frontend Developer": [
        "HTML/CSS", "JavaScript", "React", "Responsive Design", "Git",
        "REST APIs", "Web Accessibility", "Testing (Jest)", "Performance Optimization",
    ],
    "Backend Developer": [
        "Python/Node.js", "SQL", "REST APIs", "System Design", "Databases",
        "Authentication & Security", "Git", "Docker", "Cloud Basics (AWS/GCP)",
    ],
    "Full Stack Developer": [
        "HTML/CSS", "JavaScript", "React", "Node.js/Python", "SQL",
        "REST APIs", "Git", "System Design", "Cloud Basics (AWS/GCP)", "Docker",
    ],
    "Product Manager": [
        "Product Strategy", "User Research", "Data Analysis", "Roadmapping",
        "Stakeholder Communication", "Wireframing", "Agile/Scrum", "SQL Basics",
    ],
    "DevOps Engineer": [
        "Linux/CLI", "Docker", "Kubernetes", "CI/CD", "Cloud Basics (AWS/GCP)",
        "Scripting (Bash/Python)", "Networking Basics", "Monitoring & Logging", "Git",
    ],
    "Cybersecurity Analyst": [
        "Networking Basics", "Linux/CLI", "Security Fundamentals", "Risk Assessment",
        "SIEM Tools", "Python/Scripting", "Cryptography Basics", "Incident Response",
    ],
}

# fallback for any custom role text the student types that isn't in ROLE_SKILLS
GENERIC_ROLE_SKILLS = [
    "Communication", "Problem Solving", "Git", "SQL Basics",
    "Domain Fundamentals", "Portfolio Project", "Resume & Interview Readiness",
]

COURSE_LIBRARY = {
    "Data Structures & Algorithms": [
        {"title": "NeetCode 150 Roadmap", "provider": "NeetCode", "level": "Intermediate"},
        {"title": "Grokking the Coding Interview", "provider": "DesignGurus", "level": "Intermediate"},
    ],
    "Python": [
        {"title": "Python for Everybody", "provider": "Coursera (UMich)", "level": "Beginner"},
        {"title": "Automate the Boring Stuff with Python", "provider": "Al Sweigart / Udemy", "level": "Beginner"},
    ],
    "SQL": [
        {"title": "SQL for Data Analysis", "provider": "Udacity", "level": "Beginner"},
        {"title": "The Complete SQL Bootcamp", "provider": "Udemy", "level": "Intermediate"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization", "provider": "Coursera (Andrew Ng)", "level": "Intermediate"},
        {"title": "Hands-On ML with Scikit-Learn & TensorFlow", "provider": "O'Reilly", "level": "Intermediate"},
    ],
    "React": [
        {"title": "React — The Complete Guide", "provider": "Udemy", "level": "Beginner"},
        {"title": "Official React Docs (react.dev)", "provider": "React Team", "level": "Beginner"},
    ],
    "System Design": [
        {"title": "Grokking the System Design Interview", "provider": "DesignGurus", "level": "Advanced"},
        {"title": "System Design Primer", "provider": "GitHub (donnemartin)", "level": "Intermediate"},
    ],
    "Cloud Basics (AWS/GCP)": [
        {"title": "AWS Cloud Practitioner Essentials", "provider": "AWS Skill Builder", "level": "Beginner"},
        {"title": "Google Cloud Fundamentals", "provider": "Coursera", "level": "Beginner"},
    ],
    "Docker": [
        {"title": "Docker for Beginners", "provider": "KodeKloud", "level": "Beginner"},
    ],
    "Statistics": [
        {"title": "Statistics with Python", "provider": "Coursera (Michigan)", "level": "Beginner"},
    ],
    "Data Visualization": [
        {"title": "Data Visualization with Python", "provider": "Coursera (IBM)", "level": "Beginner"},
    ],
}

PROJECT_LIBRARY = {
    "Software Engineer": [
        "Build a URL shortener with a REST API and rate limiting",
        "Implement a mini LeetCode-style judge that runs and scores code submissions",
    ],
    "Data Analyst": [
        "End-to-end sales dashboard: clean raw CSV data, model it, visualize KPIs in Power BI/Tableau",
        "A/B test analysis report on a public e-commerce dataset",
    ],
    "Data Scientist": [
        "Predictive model for customer churn with full EDA + model comparison notebook",
        "NLP sentiment classifier on product reviews, deployed as a small API",
    ],
    "Machine Learning Engineer": [
        "Train and deploy an image classifier behind a REST API with Docker",
        "Build an MLOps pipeline: data versioning, training job, model registry, monitoring",
    ],
    "Frontend Developer": [
        "Responsive portfolio site with animated transitions and accessibility audit",
        "Clone a real product's UI (e.g. a dashboard) with React + component library",
    ],
    "Backend Developer": [
        "Design and build a multi-tenant SaaS backend with auth, rate limiting, and background jobs",
        "Build a job-queue based notification service (email/SMS) with retries",
    ],
    "Full Stack Developer": [
        "Full-stack task/CRM app with auth, roles, and a deployed demo",
        "Real-time chat app using WebSockets end to end",
    ],
    "Product Manager": [
        "Write a full PRD + roadmap for a feature, including success metrics",
        "Conduct 5 mock user interviews and synthesize into a research report",
    ],
    "DevOps Engineer": [
        "CI/CD pipeline that builds, tests, and deploys a sample app to the cloud automatically",
        "Kubernetes cluster with monitoring/alerting for a sample microservice",
    ],
    "Cybersecurity Analyst": [
        "Set up a home SOC lab and document a simulated incident response",
        "Perform and report a vulnerability assessment on a deliberately vulnerable app (e.g. DVWA)",
    ],
}

RESUME_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "sql", "react", "node",
    "flask", "django", "aws", "gcp", "azure", "docker", "kubernetes", "git",
    "machine learning", "deep learning", "pandas", "numpy", "tensorflow", "pytorch",
    "excel", "tableau", "power bi", "html", "css", "rest api", "agile", "scrum",
    "linux", "data structures", "algorithms", "statistics", "nlp", "computer vision",
]
