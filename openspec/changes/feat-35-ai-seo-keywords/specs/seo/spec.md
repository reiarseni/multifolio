## ADDED Requirements

### Requirement: SEO keyword suggestions
The system SHALL analyze facet content and generate SEO-optimized meta title and description suggestions using OpenAI.

#### Scenario: Successful SEO suggestion
- **WHEN** user requests SEO suggestions for a published facet with skills, experiences, or projects
- **THEN** system returns 3 variants of (meta_title, meta_description, rationale) within 10 seconds

#### Scenario: Facet not found
- **WHEN** user requests suggestions for a non-existent facet ID
- **THEN** system returns 404 Not Found

#### Scenario: Not own facet
- **WHEN** user requests suggestions for another user's facet
- **THEN** system returns 403 Forbidden

### Requirement: Three variants
The system SHALL provide exactly 3 distinct variants of meta title and description for each suggestion request.

#### Scenario: Three variants returned
- **WHEN** suggestion completes successfully
- **THEN** response includes exactly 3 variants, each with title, description, and rationale

### Requirement: Save SEO metadata
The system SHALL allow users to update meta_title and meta_description on their facets.

#### Scenario: Save SEO metadata
- **WHEN** user submits meta_title and meta_description for their facet
- **THEN** system updates the facet and returns updated data

#### Scenario: Save with empty values
- **WHEN** user submits empty meta_title and meta_description
- **THEN** system clears the fields and returns success

### Requirement: Get current SEO config
The system SHALL return the current meta_title and meta_description for a facet.

#### Scenario: Get SEO config
- **WHEN** user requests SEO config for their facet
- **THEN** system returns current meta_title and meta_description (may be null)
