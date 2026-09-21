---
name: Meetings for Datacore
description: "Meeting lifecycle — standup generation, prep, transcription, and smart routing"
version: 0.4.0
author: datacore-one
license: MIT
tags: [meetings, standup, agenda, transcription, calendar]
x-datacore:
  module: meetings
  tools: 2
  skills: 2
  agents: 5
  commands: 3
  workflows: 0
  engram_count: 0
  injection_policy: on_match
  match_terms: [meeting, standup, agenda, weekly, transcription, prep, questions]
---

# Meetings for Datacore

Meeting lifecycle management — auto-generate standups from journals,
prepare agendas, process transcriptions, and smart-route between meetings.

Tagline: "Your journal remembers. AI prepares."

## What This Module Provides

**Tools** (MCP):
- `datacore.meetings.standup` — Generate standup from recent journal entries
- `datacore.meetings.upcoming` — List upcoming meetings with prep status

**Skills**:
- Standup generation
- Open questions view

**Agents** (5):
- `standup-generator` — Parse journal, extract accomplishments
- `agenda-generator` — Generate meeting agendas with context
- `question-researcher` — Pre-research open questions
- `transcription-processor` — Extract actions from transcripts
- `meeting-router` — Smart routing between meetings

**Commands**:
- `/weekly` — Weekly prep workflow
- `/meeting-prep` — Personal prep for any meeting
- `/meeting-process` — Process transcripts

## When to Use

Triggers: meeting, standup, agenda, weekly, transcription, prep, questions.
