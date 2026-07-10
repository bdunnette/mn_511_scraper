<!--
---
Sync Impact Report:
- Version change: [CONSTITUTION_VERSION] -> 1.0.0
- List of modified principles:
  - [PRINCIPLE_1_NAME] -> I. Direct API Querying
  - [PRINCIPLE_2_NAME] -> II. CSV Data Persistence
  - [PRINCIPLE_3_NAME] -> III. Logging and Observability
  - [PRINCIPLE_4_NAME] -> IV. Robust Error Handling
  - [PRINCIPLE_5_NAME] -> V. Minimal Dependencies
- Added sections: None
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: None
---
-->

# Minnesota 511 Camera Scraper Constitution

## Core Principles

### I. Direct API Querying
The project MUST interact directly with the 511mn.org GraphQL API to fetch structured camera data efficiently in bulk, avoiding screen-scraping raw HTML.

### II. CSV Data Persistence
Scraped camera data MUST be persisted in a standardized, human-readable CSV format (mn_cameras.csv) with clear column names (Title, URI, Web URL, Stream URL, Roadway, Route).

### III. Logging and Observability
The application MUST use Python's built-in logging module to output structured info, warning, and error messages to standard output. Silent failures are prohibited.

### IV. Robust Error Handling
Network requests and JSON decoding MUST be wrapped in robust exception handling. The scraper MUST handle failures gracefully, logging the error and returning an empty dataset, without crashing unexpectedly.

### V. Minimal Dependencies
The project MUST prioritize standard library components or lightweight, standard packages (like requests and pandas) to keep the codebase simple and easy to maintain.

## Tech Stack Requirements

The project uses Python 3.13+ with requests for network operations and pandas for data handling and CSV generation.

## Verification & Testing

Verification MUST be performed by executing the scraping scripts directly and verifying the integrity and structure of the generated CSV file.

## Governance

Any amendments to this constitution require a version bump and an update to the Sync Impact Report at the top of the file.

**Version**: 1.0.0 | **Ratified**: 2026-07-10 | **Last Amended**: 2026-07-10
