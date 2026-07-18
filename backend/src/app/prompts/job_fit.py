EXTRACT_ENTRIES_PROMPT = """Extract structured information from the following job posting.

Return a JSON object with these fields:
- title: the job title (string)
- company: the company name (string, or null if not found)
- required_skills: array of strings, technical and soft skills mentioned
- required_experience_years: number or null, minimum years of experience
- tech_stack: array of strings, technologies, frameworks, tools mentioned
- preferred_skills: array of strings, nice-to-have skills
- responsibilities: array of strings, key responsibilities

Job posting:
{job_posting}

Return ONLY valid JSON, no markdown, no explanation."""

COMPARE_WITH_FACET_PROMPT = """You are a job market fit analyst. Compare a professional's profile against job requirements.

FACET CONTENT:
{facet_json}

JOB REQUIREMENTS:
{entities_json}

Analyze compatibility across these 4 dimensions (score 0-100 each):
1. SKILLS - How well does their skill set match the required and preferred skills?
2. EXPERIENCE - How well does their work experience match the requirements?
3. TECH STACK - How well does their tech stack match what the job requires?
4. TONE - How well does their headline/title/bio tone match the job's seniority and culture?

Return ONLY valid JSON with this structure:
{{
  "overall_score": <float 0-100>,
  "skills_score": <float 0-100>,
  "experience_score": <float 0-100>,
  "stack_score": <float 0-100>,
  "tone_score": <float 0-100>,
  "gaps": [
    {{
      "category": "skills|experience|stack|tone",
      "description": "specific missing or weak area",
      "severity": "high|medium|low",
      "suggestion": "concrete actionable suggestion"
    }}
  ],
  "suggestions": ["suggestion 1", "suggestion 2"],
  "reorder_suggestion": {{
    "rationale": "explanation of optimal ordering",
    "proposed_order": ["skills", "experience", "projects", ...]
  }}
}}

Be specific and honest in your assessment. Base suggestions on the actual content of the profile."""


SUGGEST_REORDER_PROMPT = """Given a professional's facet content and detected gaps for a job, propose an optimal reordering of their profile sections.

FACET CONTENT:
{facet_json}

DETECTED GAPS:
{gaps_json}

Return ONLY valid JSON with this structure:
{{
  "rationale": "explanation of why this order maximizes match",
  "proposed_order": ["section1", "section2", "section3", ...]
}}

Sections can include: skills, experience, education, projects, certifications, about.

Consider:
- Put strongest matching sections first
- De-emphasize weak areas by placing them later
- If specific skills are critical for the job, feature them prominently"""
