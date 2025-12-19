# Meetings Module

> Your journal remembers. AI prepares.

Automates the full meeting lifecycle: standup generation, meeting preparation, transcription processing, knowledge extraction, and smart routing between daily/weekly meetings.

## Features

### Phase 1: Standup Generation
- `/standup` - Generate standup from yesterday's journal + today's schedule
- Auto-standup on `/today` when Daily meeting detected
- Blocker detection from WAITING tasks
- Team vs personal filtering modes

### Phase 2: Meeting Preparation
- `/meeting-prep` - Prepare for specific meetings with context
- `/meeting-agenda` - Generate shareable agenda documents
- `/my-questions` - View open questions requiring input
- Question pre-research via GitHub Issues
- Daily-to-weekly escalation detection

### Phase 3: Transcription Processing
- `/meeting-process` - Process meeting transcripts
- Google Docs integration (Meet transcripts, Gemini notes)
- Action item extraction with confidence scoring
- Decision capture and journaling
- **Knowledge extraction** - Auto-create zettels from key concepts
- GitHub question resolution

### Phase 4: Smart Routing
- Automatic routing between daily/weekly meetings
- Escalation detection (3+ daily mentions → weekly)
- Human-in-the-loop reporting
- Deduplication across meeting types

## Quick Start

```bash
# Generate standup report
/standup

# Prepare for a weekly meeting
/meeting-prep weekly-exec

# Process a meeting transcript
/meeting-process https://docs.google.com/document/d/...

# View open questions
/my-questions
```

## Commands

| Command | Description |
|---------|-------------|
| `/standup` | Generate standup from journal |
| `/meeting-prep <type>` | Prepare for meeting with context |
| `/meeting-agenda <type>` | Generate shareable agenda |
| `/my-questions` | List open questions |
| `/meeting-process <source>` | Process transcript, extract knowledge |

## Agents

| Agent | Purpose |
|-------|---------|
| `standup-generator` | Parse journal, extract accomplishments |
| `agenda-generator` | Generate agendas from multiple sources |
| `question-researcher` | Pre-research open questions |
| `transcription-processor` | Extract actions/decisions from transcripts |
| `meeting-router` | Smart routing between meetings |

## Configuration

In `settings.local.yaml`:

```yaml
meetings:
  # Phase 1: Standup
  auto_generate_standup: true
  standup_meeting_match: "Daily"
  blockers_threshold_days: 3
  post_to_journal: true
  default_team_mode: true

  # Phase 2: Questions
  questions:
    github_label: "question"
    auto_research: true

  # Phase 3: Transcription
  transcription:
    google_docs:
      enabled: true
      auto_discover: true
    action_confidence_threshold: 0.7
    decision_confidence_threshold: 0.8

  # Phase 4: Routing
  routing:
    enabled: true
    auto_apply: false  # Require --apply flag
    escalation_threshold: 3
    report_in_standup: true
```

## Transcription Processing

### Supported Sources

| Source | Format |
|--------|--------|
| Google Docs URL | Meet auto-transcripts, Gemini notes |
| Local file | Markdown, text transcripts |
| `--recent` | List recent transcripts from Drive |

### What Gets Extracted

1. **Action Items** - With confidence scoring and assignee
2. **Decisions** - Captured and added to journal
3. **Knowledge** - Key concepts become zettels
4. **Questions** - Matched against GitHub Issues

### Confidence Scoring

| Pattern | Confidence |
|---------|------------|
| "Action item:" prefix | 1.0 |
| "@person will" | 0.95 |
| "I'll" + verb | 0.9 |
| "We should" | 0.6 |

### Knowledge Extraction

Every meeting processes creates:
- **Journal entry** - Meeting summary with key clarifications
- **Zettels** - Atomic notes for key concepts (architecture decisions, insights, mechanisms)
- **Action items** - Tasks in next_actions.org

Example output:
```
Knowledge Extracted (4)
-----------------------
1. Verity-RFQ-Exchange-Mechanism.md
2. Data-as-Depreciating-Asset.md
3. Smart-Contract-Dispute-Recording.md
4. Data-Ownership-Transfer-Rights.md
```

## Smart Routing

### Routing Rules

| Condition | Route To |
|-----------|----------|
| Blocking TODAY | Daily |
| `:@daily:` tag | Daily |
| `:@weekly:` tag | Weekly |
| Multiple stakeholders | Weekly |
| `:decision:` tag | Weekly |
| 3+ daily mentions | Weekly (escalate) |

### Human-in-the-Loop

Routing is automatic but reported:
- Changes shown in standup output
- Require `--apply` flag to execute
- Manual tags always override

## Google Docs Setup

First-time OAuth setup:

```bash
python .datacore/modules/meetings/lib/google_docs.py setup
```

Required Google Cloud APIs:
- Google Docs API (readonly)
- Google Drive API (readonly)

## How It Works

### Standup Generation

1. **Yesterday's accomplishments** - Parsed from journal sections
2. **Today's plan** - From journal or next_actions.org
3. **Blockers** - WAITING tasks older than threshold
4. **Routing changes** - Items escalated/moved

### Meeting Processing

1. Fetch transcript (Google Docs or local)
2. Parse and detect format (Meet, Gemini, plain)
3. Extract action items with confidence scores
4. Capture decisions
5. **Extract knowledge → create zettels**
6. **Update journal with meeting summary**
7. Match and resolve GitHub questions
8. Generate summary report

## Library

The module provides Python utilities:

```python
from meetings.lib.google_docs import GoogleDocsClient
from meetings.lib.transcription_parser import TranscriptionParser

# Fetch transcript
client = GoogleDocsClient()
doc = client.get_document_by_url(url)

# Parse and extract
parser = TranscriptionParser()
result = parser.parse(doc.content)

print(result.action_items)
print(result.decisions)
print(result.speakers)
```

## Dependencies

- `core@>=1.0.0` (required)
- `nightshift` (optional) - Show results in standup
- `crm` (optional) - Include CRM context
- `calendar` (optional) - Meeting detection

## Related DIPs

- [DIP-0013](../../dips/DIP-0013-meetings-module.md) - Meetings Module specification
- [DIP-0010](../../dips/DIP-0010-external-sync-architecture.md) - Calendar sync
- [DIP-0009](../../dips/DIP-0009-gtd-specification.md) - GTD integration

## Version History

- **v0.3.0** - Phase 3-4: Transcription processing, knowledge extraction, smart routing
- **v0.2.0** - Phase 2: Meeting preparation, questions, agendas
- **v0.1.0** - Phase 1: Standup generation
