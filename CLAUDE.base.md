# Meetings Module Context

> Your journal remembers. AI prepares.

This module automates the full meeting lifecycle: standup generation, meeting preparation, transcription processing, knowledge extraction, and smart routing.

## Commands

| Command | Description |
|---------|-------------|
| `/standup` | Generate standup from journal |
| `/meeting-prep` | Prepare for meeting with context |
| `/meeting-agenda` | Generate shareable agenda |
| `/my-questions` | View open questions |
| `/meeting-process` | Process transcript, extract knowledge |

### /standup

Generate a standup report from yesterday's journal and today's schedule.

**Workflow:**
1. Ask: Team, Personal, or Investor mode?
2. Parse yesterday's journal for accomplishments
3. Get today's tasks from Priority Tasks or next_actions.org
4. Find blockers from WAITING tasks > 3 days old
5. Apply content filters (team relevance, anti-anxiety)
6. Generate formatted output
7. Post to today's journal
8. Offer follow-up options

### /meeting-prep

Prepare for a specific meeting with full context.

**Workflow:**
1. Ask: Which meeting type?
2. Gather open questions from GitHub
3. Find tasks needing discussion
4. Check escalated items (3+ daily mentions)
5. Trigger AI research (if requested)
6. Generate preparation report
7. Offer follow-up options

### /meeting-agenda

Generate a shareable agenda document.

**Workflow:**
1. Ask: Which meeting type?
2. Gather items per meeting type
3. Apply routing rules (daily vs weekly)
4. Render with appropriate template
5. Post to team space (if requested)
6. Offer follow-up options

### /my-questions

View open questions requiring your input.

**Workflow:**
1. Ask: All, specific project, or for a meeting?
2. Query GitHub Issues with `question` label
3. Classify by status (ready, needs input, needs research)
4. Generate grouped output
5. Offer follow-up options

### /meeting-process

Process meeting transcription to extract knowledge.

**Workflow:**
1. Ask: Google Doc URL, local file, or recent?
2. Fetch and parse transcript
3. Extract action items with confidence scores
4. Capture decisions
5. Create zettels for key concepts
6. Update journal with meeting summary
7. Match and resolve GitHub questions
8. Generate summary report
9. Offer follow-up options

## Hooks

### /today Hook

When meetings module is installed, `/today` checks for Daily meetings:
- Parse `calendar.org` for meetings matching `standup_meeting_match` setting
- If found, generate standup preview section

### /gtd-weekly-review Hook

During weekly review:
- Check for unprocessed meeting transcripts
- Review escalated items
- Verify question resolution status

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_generate_standup` | true | Generate standup in /today |
| `standup_meeting_match` | "Daily" | Calendar title pattern |
| `blockers_threshold_days` | 3 | Days before WAITING is blocker |
| `post_to_journal` | true | Auto-post standup |
| `default_team_mode` | true | Default to team filtering |
| `action_confidence_threshold` | 0.7 | Min confidence for auto-create |
| `routing.escalation_threshold` | 3 | Daily appearances before escalate |

## Use Cases

1. **Zero-input standups** - Generate from yesterday's journal automatically
2. **Auto-trigger standup** - When Daily meeting is scheduled
3. **Surface blockers** - From WAITING tasks in org files
4. **Meeting preparation** - Context and pre-researched questions
5. **Question tracking** - Via GitHub Issues with `question` label
6. **Daily-to-weekly escalation** - Recurring items auto-escalate
7. **Shareable agendas** - For team distribution
8. **Transcript processing** - Google Meet + Gemini notes support
9. **Auto-create tasks** - From meeting discussions
10. **Knowledge extraction** - Create zettels from key concepts
11. **Question resolution** - Match and close GitHub issues
12. **Smart routing** - Between daily and weekly meetings
13. **Deduplication** - Across meeting agendas

## Data Sources

| Source | Purpose |
|--------|---------|
| `0-personal/notes/journals/` | Yesterday's accomplishments, today's plan |
| `0-personal/org/next_actions.org` | Tasks, blockers, escalation tracking |
| `0-personal/org/calendar.org` | Meeting detection |
| `0-personal/notes/2-knowledge/zettel/` | Knowledge extraction output |
| GitHub Issues | Open questions tracking |
| Google Docs | Meeting transcripts |

## Boundaries

**YOU CAN:**
- Read journal files in `notes/journals/`
- Read org files in `org/`
- Read `calendar.org` for meeting detection
- Write standup to today's journal
- Create zettels in knowledge base
- Query and comment on GitHub Issues
- Fetch Google Docs (with OAuth)

**YOU CANNOT:**
- Modify org files (tasks, priorities)
- Delete journal content
- Create new GitHub issues (only resolve)
- Access external APIs without setup

**YOU MUST:**
- Offer follow-up options after each command
- Flag low-confidence extractions
- Preserve source context
- Ask clarifying questions when intent unclear

## Output Format

### Standup
```markdown
## Standup - YYYY-MM-DD

### Yesterday
- [accomplishment 1]

### Today
- [ ] [task 1]

### Blockers
- WAITING: [description] (since [date])
```

### Meeting Summary
```markdown
## Meeting Summary - {type} - {date}

**Participants:** {speakers}

### Action Items Created ({count})
- [ ] {action} (@{assignee})

### Knowledge Extracted ({count})
- [[{zettel-name}]]
```
