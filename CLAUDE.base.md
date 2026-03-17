---
summary: "Meeting lifecycle — standups, preparation, transcription processing, and smart routing"
triggers: ["generate standup", "prep for meeting", "meeting agenda", "my questions", "process transcript"]
context: on_match
---

# Meetings Module

## Purpose

Automates the full meeting lifecycle: zero-input standup generation from journals, meeting preparation with pre-researched context, transcript processing with action item and knowledge extraction, and smart routing between daily and weekly meetings. Your journal remembers -- AI prepares.

## Quick Start
> Say "generate standup" to create a standup report from yesterday's journal.

## How It Works

### Standup Generation
Parses yesterday's journal for accomplishments, pulls today's tasks from `next_actions.org`, surfaces WAITING tasks older than 3 days as blockers. Supports Team, Personal, and Investor modes with content filtering.

### Meeting Preparation
Gathers open questions (GitHub Issues with `question` label), tasks needing discussion, and escalated items (3+ daily mentions). Optionally triggers AI research.

### Transcript Processing
Fetches transcript (Google Doc or local file), extracts action items with confidence scores, captures decisions, creates zettels for key concepts, and resolves matching GitHub questions.

## Agents & Commands

| Name | Type | When to use |
|------|------|-------------|
| `/weekly` | command | Prepare recurring weekly meetings |
| `/meeting-prep` | command | Prepare for a specific meeting |
| `/meeting-process` | command | Process transcript into notes + tasks |
| `standup` | skill | Generate standup from journal |
| `my-questions` | skill | View open questions needing input |
| `standup-generator` | agent | Standup content generation |
| `agenda-generator` | agent | Meeting agenda creation |
| `transcription-processor` | agent | Transcript parsing and extraction |
| `question-researcher` | agent | Research answers for queued questions |
| `meeting-router` | agent | Route items between daily/weekly |

## Key Paths

| Path | Purpose |
|------|---------|
| `notes/journals/` | Source for standup accomplishments |
| `org/next_actions.org` | Tasks, blockers, escalation tracking |
| `org/calendar.org` | Meeting detection and scheduling |
| `notes/2-knowledge/zettel/` | Knowledge extraction output |

## Boundaries

- Reads journals and org files but does NOT modify org tasks or delete journal content
- Action items below confidence threshold (default 0.7) are flagged, not auto-created
- Cannot create new GitHub Issues -- only resolves existing ones

---

*This file covers structure, capability, and stable configuration. Learned behavior, user corrections, and operational preferences live as engrams -- call `datacore.recall` for those.*
