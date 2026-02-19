# /meeting-process

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Processing meeting transcripts after meetings
- Extracting action items from discussions
- Capturing decisions made during meetings
- Resolving questions that were discussed
- Creating knowledge artifacts from meeting insights

**Key decisions the module informs:**
- What action items have sufficient confidence to auto-create
- Which discussed questions can be closed or updated
- What knowledge should be extracted as zettels
- How to map transcript speakers to team members

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | After meetings, when transcript is available |
| What sources? | Google Docs transcripts, local transcript files |
| What does it create? | Tasks, zettels, journal entries, GitHub comments |
| What's the confidence threshold? | Configurable (default 0.7 for tasks, 0.8 for decisions) |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| transcription-processor | Parse transcript, extract items, update GitHub, create artifacts |

### Integration Points

- **Google Docs API** - Fetch Meet transcripts
- **transcription_parser.py** - Core parsing library
- **GitHub Issues** - Update/close questions discussed
- **next_actions.org** - Create tasks from action items
- **notes/journals/** - Record decisions and summary
- **notes/2-knowledge/zettel/** - Extract insights as zettels

---

Process meeting transcription to extract action items, decisions, knowledge, and resolve questions.

## Workflow

### Step 1: Understand Intent

If invoked as just `/meeting-process` with no source, ask:

"How would you like to process a meeting?"

1. **Google Doc** - Paste a Google Docs URL (Meet transcript or Gemini notes)
2. **Local file** - Process a local transcript file
3. **Recent** - Browse recent Meet transcripts from Google Drive

If a URL or path is provided, proceed directly.

### Step 2: Gather Context

**Ask if not clear:**
- "What type of meeting was this?" (daily, weekly, product)
- "What date?" (default: auto-detect from transcript)
- "Should I preview first?" (dry-run mode)

**Auto-detect:**
- Meeting type from transcript title
- Date from document metadata or content
- Participants from speaker labels

### Step 3: Fetch Transcript

**Google Docs URL:**
```python
from meetings.lib.google_docs import GoogleDocsClient

client = GoogleDocsClient()
doc = client.get_document_by_url(url)
```

**Local file:**
Read file contents directly.

**Recent transcripts:**
```python
transcripts = client.find_meet_transcripts(days=7)
# Present list for selection
```

### Step 4: Parse Transcript

```python
from meetings.lib.transcription_parser import TranscriptionParser

parser = TranscriptionParser()
result = parser.parse(content)
```

Extracts:
- `result.action_items` - actions with confidence scores
- `result.decisions` - captured decisions
- `result.questions_raised` - questions mentioned
- `result.speakers` - participant list

### Step 5: Extract Action Items

**Confidence scoring:**

| Pattern | Confidence | Example |
|---------|------------|---------|
| "Action item:" prefix | 1.0 | "Action item: schedule review" |
| "@person will" | 0.95 | "@bob will update the docs" |
| "I'll" + verb | 0.9 | "I'll have it ready by Friday" |
| "We should" | 0.6 | "We should refactor that" |

**Assignee extraction:**
- `@person` mentions → direct assignee
- `"I'll"` → speaker becomes assignee
- `"We should"` → flag as unassigned

### Step 6: Extract Decisions

Pattern matching for explicit decisions:

| Pattern | Example |
|---------|---------|
| "We decided to X" | "We decided to use PostgreSQL" |
| "The plan is X" | "The plan is to launch in Q1" |
| "Going forward, X" | "Going forward, we'll use JWT" |

### Step 7: Match Open Questions

Query GitHub for open questions (unless skipped):
```bash
gh issue list --repo {repo} --label question --state open
```

For each open question:
1. Extract keywords from issue title/body
2. Search transcript for keyword mentions
3. If discussed, mark as potentially resolved
4. Comment with resolution context

### Step 8: Extract Knowledge

**Always extract knowledge from meetings:**

1. **Identify Key Concepts**: Technical terms, architecture decisions, insights
2. **Create Zettels**: For each significant concept in `0-personal/notes/2-knowledge/zettel/`
3. **Update Journal**: Append meeting summary to `journals/YYYY-MM-DD.md`

**Zettel candidates:**

| Type | Example | Action |
|------|---------|--------|
| Architecture decision | "We'll use RFQ not AMM" | Create zettel explaining the choice |
| Insight | "Data is a depreciating asset" | Create zettel exploring implications |
| New mechanism | "Smart contract for disputes" | Document the mechanism |

### Step 9: Generate Outputs

**Action Items** → `next_actions.org`:
```org
*** TODO {action} :meeting:
:PROPERTIES:
:CREATED: [{date}]
:SOURCE: [[{meeting_type} {date}]]
:ASSIGNEE: @{person}
:CONFIDENCE: {confidence}
:END:
```

**Decisions** → Journal:
```markdown
### Decisions from {meeting_type}
- {decision 1}
- {decision 2}
```

**Questions** → GitHub:
```
Discussed in {meeting_type} on {date}.
Resolution: {summary}
```

### Step 10: Generate Summary

Output using `meeting-summary.md` template with:
- Meeting metadata (type, date, duration)
- Participants
- Action items created
- Decisions captured
- Knowledge extracted (zettels)
- Journal updated
- Questions resolved

### Step 11: Follow-up

After processing, offer next steps:

"Meeting processed. Would you like to:"
- "Review the created zettels?" → List and open knowledge notes
- "See the updated journal?" → Open journal entry
- "Process another transcript?" → `/meeting-process --recent`
- "Prepare for next meeting?" → `/meeting-prep`

## Output Example

```
MEETING PROCESSED
=================
Source: Project Alpha Daily (Dec 17, 2025)
Duration: ~45 minutes
Participants: Alice Smith, Bob Jones

Action Items Created (1)
------------------------
1. [0.85] Research SHAP machine learning concept
   -> @bob
   Created in next_actions.org

Decisions Captured (3)
----------------------
1. Exchange uses RFQ mechanism, not AMM
2. Data products subject to ownership
3. Disputes recorded via smart contract

Knowledge Extracted (4)
-----------------------
1. Project-Alpha-RFQ-Exchange-Mechanism.md
2. Data-as-Depreciating-Asset.md
3. Smart-Contract-Dispute-Recording.md
4. Data-Ownership-Transfer-Rights.md

Journal Updated: 2025-12-17.md
```

## Source Types

| Source | Example |
|--------|---------|
| Google Docs URL | `https://docs.google.com/document/d/...` |
| Local file | `~/Downloads/transcript.md` |
| Recent | Browse recent Meet transcripts |

## Error Handling

| Error | Response |
|-------|----------|
| Google Docs auth not configured | Show setup instructions with link |
| Document not accessible | Check sharing settings, offer alternatives |
| No action items found | Note this, suggest manual review |
| GitHub unavailable | Skip question matching, note limitation |
| Low confidence extractions | Flag for manual review |

## Configuration

Settings in `settings.local.yaml`:

```yaml
meetings:
  transcription:
    action_confidence_threshold: 0.7
    decision_confidence_threshold: 0.8
    google_docs:
      enabled: true
      auto_discover: true
```

## Your Boundaries

**YOU CAN:**
- Fetch Google Docs via API (with OAuth)
- Read local transcript files
- Parse and extract structured data
- Create tasks in next_actions.org
- Create zettels in knowledge base
- Append to journal entries
- Comment on GitHub issues
- Close GitHub issues (if explicitly resolved)

**YOU CANNOT:**
- Modify transcript content
- Create new GitHub issues (only resolve existing)
- Delete tasks or journal entries
- Access Google Docs without OAuth setup

**YOU MUST:**
- Flag low-confidence extractions for review
- Preserve source context in created tasks
- Report all actions taken
- Respect dry-run flag
- Always extract knowledge (zettels + journal)
- Offer follow-up options after processing
