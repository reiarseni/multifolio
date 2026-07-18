EXTRACT_KEYWORDS_PROMPT = """
Analyze the following profile (facet) and extract the most relevant SEO keywords
for the target role.

FACET CONTENT:
{facet_json}

Return ONLY valid JSON with this structure:
{{
  "role": "<primary target role based on the profile>",
  "keywords": ["keyword1", "keyword2", ...],
  "industry": "<primary industry>",
  "seniority_level": "<junior|mid|senior|lead>"
}}

Include 8-12 relevant keywords that recruiters would search for on Google.
Focus on: role-specific terms, technologies, soft skills, and industry terms."""

GENERATE_META_PROMPT = """
You are an SEO specialist. Generate 3 distinct variants of meta title and
meta description for a professional portfolio page.

Each variant should target different angles while staying accurate to the profile.

TARGET ROLE: {role}
KEYWORDS: {keywords}
SENIORITY: {seniority_level}
INDUSTRY: {industry}

FACET CONTENT:
{facet_json}

Return ONLY valid JSON with this structure:
{{
  "variants": [
    {{
      "title": "<meta title 50-60 characters>",
      "description": "<meta description 150-160 characters>",
      "rationale": "<why this variant works for SEO>"
    }}
  ]
}}

Guidelines:
- Title: 50-60 chars, include primary keyword near the start
- Description: 150-160 chars, compelling, includes call-to-action
- Each variant must be meaningfully different in approach
- Variant 1: Most direct/traditional approach
- Variant 2: More creative/benefit-focused
- Variant 3: Niche/specialized angle"""
