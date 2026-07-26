## ADDED Requirements

### Requirement: Job posting analysis
The system SHALL accept a job posting text (max 10,000 characters) and return a compatibility analysis against the selected facet profile. The analysis SHALL be performed using OpenAI GPT-4 and SHALL NOT store the job posting text.

#### Scenario: Successful job posting analysis
- **WHEN** user submits a valid job posting (≤10K chars) for a published facet
- **THEN** system returns overall_score (0-100), dimension scores, gaps list, and reorder suggestion within 10 seconds

#### Scenario: Job posting too long
- **WHEN** user submits a job posting exceeding 10,000 characters
- **THEN** system returns 422 Unprocessable Entity with error message "Job posting must not exceed 10,000 characters"

#### Scenario: Facet not found
- **WHEN** user submits analysis for a non-existent facet ID
- **THEN** system returns 404 Not Found

#### Scenario: Job posting text not stored
- **WHEN** analysis completes successfully
- **THEN** the original job posting text is NOT persisted in any database table

### Requirement: Dimension scores
The system SHALL compute and return scores for four dimensions: skills, experience, tech stack, and headline tone. Each score SHALL be a float between 0 and 100.

#### Scenario: All dimension scores returned
- **WHEN** analysis completes
- **THEN** response includes skills_score, experience_score, stack_score, and tone_score, each between 0 and 100

### Requirement: Gap detection with suggestions
The system SHALL detect gaps between the facet content and job posting requirements, and provide concrete suggestions for each gap.

#### Scenario: Gaps detected
- **WHEN** the facet lacks skills, experience level, or technologies mentioned in the job posting
- **THEN** response includes a gaps array with objects containing: category, description, severity (high/medium/low), and suggestion text

#### Scenario: No gaps found
- **WHEN** the facet content fully matches the job posting requirements
- **THEN** gaps array is empty

### Requirement: Skill/experience reordering
The system SHALL propose an optimal reordering of skills and experiences to maximize match perception for the specific job.

#### Scenario: Reorder suggestion generated
- **WHEN** analysis includes skill/experience sections
- **THEN** response includes reorder_suggestion with a suggested ordering rationale

### Requirement: Analysis history
The system SHALL return a list of past analyses for a given facet, including scores and creation date.

#### Scenario: History retrieval
- **WHEN** user requests history for a facet with previous analyses
- **THEN** system returns list of FacetAnalysis records with scores and dates

#### Scenario: No history
- **WHEN** user requests history for a facet with no previous analyses
- **THEN** system returns empty list

### Requirement: Delete analysis
The system SHALL allow users to delete a specific analysis record.

#### Scenario: Delete existing analysis
- **WHEN** user deletes an analysis that belongs to their facet
- **THEN** system returns 200 with success message and removes the record

#### Scenario: Delete non-existent analysis
- **WHEN** user deletes a non-existent analysis ID
- **THEN** system returns 404 Not Found

### Requirement: Privacy-first design
The system SHALL NOT store, cache, or log the job posting text submitted by the user.

#### Scenario: Job posting not in response
- **WHEN** analysis history is retrieved
- **THEN** response does NOT contain the original job posting text

#### Scenario: Database inspection
- **WHEN** inspecting the facet_analyses table
- **THEN** no column contains the original job posting text
