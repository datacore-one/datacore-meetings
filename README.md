# Meetings Module

> Your journal remembers. AI prepares.

Automates the full meeting lifecycle: standup generation, weekly prep with GitHub Issues and calendar integration, transcription processing, knowledge extraction, and smart routing between daily/weekly meetings.


## Install

```bash
datacore module install https://github.com/datacore-one/datacore-meetings
python3 -m pip install -r ~/Data/.datacore/modules/meetings/requirements.txt   # if present
```

Requires a working [Datacore](https://datacore.one) installation.

## Quick Start

```bash
# Morning: Generate standup for daily meeting
/standup

# 1-2 days before weekly: Full prep workflow
/weekly teamspace
# → Aggregates sources → Creates GitHub Issue → Updates calendar → Sends invites

# Personal prep for any meeting (no issue/calendar)
/meeting-prep alpha-product

# After meeting: Process transcript, extract knowledge
/meeting-process https://docs.google.com/document/d/...

# View open questions across projects
/my-questions
```

## Ad-hoc Meeting Management

Beyond the structured commands below, individual meetings can be created,
updated and cancelled through natural-language conversation. The calendar
adapter (`sync/adapters/google_calendar.py`) exposes create and update
operations, so the AI can act on instructions like:

- "Schedule a meeting with someone tomorrow at 2pm about Q1 planning"
- "Add Maria to the product sync on Friday"
- "Move the design review to 3pm and update the invite"
- "Cancel the test meeting and notify attendees"

There is no dedicated `/create-meeting` command; the capability is the
adapter's, and the conversation is the interface. Changes that reach other
people (invites, cancellations) are confirmed before they are sent.

## Commands

### Meeting-Type Commands (Primary Entry Points)

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `/weekly [team]` | Full weekly prep: aggregate sources → GitHub Issue → calendar + invites | 1-2 days before weekly |
| `/standup` | Generate standup from journal + schedule | Morning of daily meeting |

### Support Commands

| Command | Purpose |
|---------|---------|
| `/meeting-prep <type>` | Personal prep with context (no issue/calendar) |
| `/my-questions` | List open questions across projects |
| `/meeting-process <source>` | Process transcript, extract actions/decisions/knowledge |

### Deprecated

- `/meeting-agenda` - Now internal; called automatically by `/weekly` and `/standup`

## Agents

| Agent | Purpose | Invoked By |
|-------|---------|------------|
| `standup-generator` | Parse journal, extract accomplishments, apply filters | `/standup` |
| `agenda-generator` | Generate agendas with outcomes + pre-meeting prep | `/weekly`, `/standup` |
| `question-researcher` | Pre-research open questions via GitHub | `/weekly --research` |
| `transcription-processor` | Extract actions/decisions from transcripts | `/meeting-process` |
| `meeting-router` | Smart routing between daily/weekly meetings | `/weekly`, `/standup` |

## Workflows

### Daily Standup Workflow

```
Morning → /standup (or auto-triggered by /today)
         ↓
    Parse yesterday's journal
         ↓
    Extract accomplishments (filtered for team relevance)
         ↓
    Get today's tasks from org files
         ↓
    Identify blockers (WAITING > 3 days)
         ↓
    Generate standup → Post to journal
         ↓
    Optional: Export for Slack/chat
```

**What gets filtered:**
- Personal items (finance, health, family)
- Anxiety-inducing metrics ("created 22 tasks", "found 15 issues")
- Activity reports transformed to outcomes

### Weekly Prep Workflow

```
1-2 days before → /weekly teamspace
                    ↓
    Find existing calendar entry
                    ↓
    Aggregate sources (parallel):
    - Personal org (next_actions.org)
    - Team org tasks
    - GitHub Issues (labeled: weekly, decision, discuss)
    - Open PRs (flag stale ones)
    - Previous meeting's unclosed action items
    - Items escalated from daily (3+ mentions)
                    ↓
    Generate draft agenda (grouped by theme)
                    ↓
    Present for refinement → User feedback
                    ↓
    Identify pre-meeting preparation per attendee
                    ↓
    Add outcome goals per agenda item
                    ↓
    Create GitHub Issue (--create-issue)
                    ↓
    Update calendar + send invites (--calendar)
                    ↓
    Summary with follow-up options
```

### Post-Meeting Workflow

```
After meeting → /meeting-process <source>
                    ↓
    Fetch transcript (Google Docs, local file, or --recent)
                    ↓
    Parse and detect format (Meet, Gemini, plain)
                    ↓
    Extract with confidence scoring:
    - Action items → next_actions.org
    - Decisions → journal
    - Knowledge → zettels
                    ↓
    Match against open GitHub questions
                    ↓
    Generate summary report
```

## Features by Phase

### Phase 1: Standup Generation
- Zero-input standups from yesterday's journal
- Auto-standup on `/today` when Daily meeting detected
- Team vs personal filtering modes
- Blocker detection from WAITING tasks
- Chat-friendly export (Slack/Discord)

### Phase 2: Meeting Preparation
- `/weekly` - Full workflow with GitHub Issue + calendar integration
- `/meeting-prep` - Personal prep for any meeting
- Question pre-research via GitHub Issues
- Daily-to-weekly escalation detection
- Multi-source aggregation (org, GitHub Issues/PRs, previous meetings)

### Phase 3: Transcription Processing
- Google Docs integration (Meet transcripts, Gemini notes)
- Action item extraction with confidence scoring
- Decision capture and journaling
- Knowledge extraction → auto-create zettels
- GitHub question resolution

### Phase 4: Smart Routing
- Automatic routing between daily/weekly meetings
- Escalation detection (3+ daily mentions → weekly)
- Human-in-the-loop reporting
- Deduplication across meeting types

## Configuration

In `settings.local.yaml`:

```yaml
meetings:
  # Standup settings
  auto_generate_standup: true
  standup_meeting_match: "Daily"
  blockers_threshold_days: 3
  post_to_journal: true
  default_team_mode: true

  # Questions and escalation
  questions:
    github_label: "question"
    auto_research: true

  # Transcription processing
  transcription:
    google_docs:
      enabled: true
      auto_discover: true
    action_confidence_threshold: 0.7
    decision_confidence_threshold: 0.8

  # Smart routing
  routing:
    enabled: true
    auto_apply: false  # Require --apply flag
    escalation_threshold: 3
    report_in_standup: true
```

### Team Configuration

Define meeting types in `module.yaml` → `meeting_types`:

```yaml
weekly-teamspace:
  name: "Team Weekly"
  duration: 90
  calendar_match: "Weekly Team"
  github_repo: "org-name/project-alpha"
  attendees:
    - email: "user@organization.example.com"
      role: organizer
    - email: "alice@organization.example.com"
      role: attendee
  standing_items:
    - "Business Update"
    - "Coming Up"
  escalate_from_daily: true
```

## Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| `/today` | Daily meeting detected in calendar | Auto-generate standup |
| `/gtd-weekly-review` | Weekly review completion | Prompt for weekly prep |

## Google Docs Setup

First-time OAuth setup:

```bash
python .datacore/modules/meetings/lib/google_docs.py setup
```

Required Google Cloud APIs:
- Google Docs API (readonly)
- Google Drive API (readonly)

## Dependencies

- `core@>=1.0.0` (required)
- `nightshift` (optional) - Show nightshift results in standup
- `crm` (optional) - Include CRM context for meetings
- `calendar` (optional) - Calendar sync for meeting detection

## Related DIPs

- [DIP-0013](../../dips/DIP-0013-meetings-module.md) - Meetings Module specification
- [DIP-0010](../../dips/DIP-0010-external-sync-architecture.md) - Calendar sync
- [DIP-0009](../../dips/DIP-0009-gtd-specification.md) - GTD integration
- [DIP-0014](../../dips/DIP-0014-tag-taxonomy.md) - Tag taxonomy (meeting routing tags)
- [DIP-0016](../../dips/DIP-0016-agent-registry.md) - Agent/command context patterns

## Version History

- **v0.3.0** - Phase 3-4: Transcription processing, knowledge extraction, smart routing
- **v0.2.1** - Add `/weekly` command with full workflow (GitHub Issue + calendar + invites)
- **v0.2.0** - Phase 2: Meeting preparation, questions, agendas
- **v0.1.0** - Phase 1: Standup generation
