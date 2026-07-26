ANALYZE_REPO_PROMPT = """
You are an AI assistant that helps professionals import their GitHub repositories
into their portfolio website as showcase projects.

Analyze the following GitHub repository data and generate portfolio-friendly content.

REPOSITORY:
- Name: {repo_name}
- Full name: {repo_full_name}
- Description: {repo_description}
- Language: {repo_language}
- Stars: {repo_stars}
- Forks: {repo_forks}
- Topics: {repo_topics}

README CONTENT:
{readme_content}

Generate a portfolio project entry that:
1. Has a compelling title (don't just use the repo name — make it human-readable)
2. Has a concise description (1-2 paragraphs) suitable for a portfolio
3. Has detailed markdown content explaining what the project does, key features,
   technologies used, and what was learned

Return ONLY valid JSON with this structure:
{{
  "title": "<human-readable project title>",
  "description": "<1-2 paragraph description>",
  "markdown_content": "<detailed markdown with sections: Overview, Key Features, Technologies>"
}}
"""
