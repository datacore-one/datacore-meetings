# /meeting-process

Process meeting transcription to extract action items, decisions, and resolve questions.

## Usage

```
/meeting-process <source> [options]
```

## Source Types

| Source | Example |
|--------|---------|
| Google Docs URL | `/meeting-process https://docs.google.com/document/d/...` |
| Local file | `/meeting-process ~/Downloads/transcript.md` |
| Recent transcripts | `/meeting-process --recent` |

## Options

| Option | Description |
|--------|-------------|
| `--meeting-type TYPE` | Meeting type hint: daily, weekly, product |
| `--date DATE` | Meeting date (default: today) |
| `--dry-run` | Preview extractions without creating tasks |
| `--no-github` | Skip GitHub question resolution |
| `--output FORMAT` | Output format: org, md, json |

## Algorithm

### Step 1: Fetch Transcript

**If Google Docs URL:**
```python
from meetings.lib.google_docs import GoogleDocsClient

client = GoogleDocsClient()
doc = client.get_document_by_url(url)
content = doc.content
```

**If local file:**
Read file contents directly.

**If --recent:**
```python
transcripts = client.find_meet_transcripts(days=7)
# Present list for selection
```

### Step 2: Parse Transcript

```python
from meetings.lib.transcription_parser import TranscriptionParser

parser = TranscriptionParser()
result = parser.parse(content)

# result.action_items - extracted actions with confidence scores
# result.decisions - captured decisions
# result.questions_raised - questions mentioned
# result.speakers - participant list
```

### Step 3: Extract Action Items

**Confidence scoring:**

| Pattern | Confidence | Example |
|---------|------------|---------|
| "Action item:" prefix | 1.0 | "Action item: schedule review" |
| "@person will" | 0.95 | "@tadej will update the docs" |
| "I'll" + verb | 0.9 | "I'll have it ready by Friday" |
| "We should" | 0.6 | "We should refactor that" |

**Assignee extraction:**
- `@person` mentions → direct assignee
- `"I'll"` → speaker becomes assignee
- `"We should"` → flag as unassigned, needs team decision

### Step 4: Extract Decisions

Pattern matching for explicit decisions:

| Pattern | Example |
|---------|---------|
| "We decided to X" | "We decided to use PostgreSQL" |
| "The plan is X" | "The plan is to launch in Q1" |
| "Going forward, X" | "Going forward, we'll use JWT" |

### Step 5: Match Open Questions (unless --no-github)

Query GitHub for open questions:
```bash
gh issue list --repo {repo} --label question --state open --json number,title,body
```

For each open question:
1. Extract keywords from issue title/body
2. Search transcript for keyword mentions
3. If discussed, mark as potentially resolved
4. Extract resolution context if found

### Step 6: Generate Outputs

**For Action Items:**
Create tasks in `next_actions.org`:

```org
*** TODO {action} :meeting:
:PROPERTIES:
:CREATED: [{date}]
:SOURCE: [[{meeting_type} {date}]]
:ASSIGNEE: @{person}
:CONFIDENCE: {confidence}
:END:
From {meeting_type}: "{source_line}"
```

**For Decisions:**
Append to today's journal (`notes/journals/YYYY-MM-DD.md`):

```markdown
### Decisions from {meeting_type}
- {decision 1}
- {decision 2}
```

**For Resolved Questions:**
Comment on GitHub issue:
```
Discussed in {meeting_type} on {date}.
Resolution: {summary extracted from transcript}
```
Close issue if explicitly resolved.

### Step 7: Extract Knowledge

**Always extract knowledge from meetings:**

1. **Identify Key Concepts**: Look for technical terms, architectural decisions, insights
2. **Create Zettels**: For each significant concept:
   - Create atomic note in `0-personal/notes/2-knowledge/zettel/`
   - Use format: `{Concept-Name}.md`
   - Include: title, tags, source (meeting), related concepts

**Zettel candidates:**
| Type | Example | Action |
|------|---------|--------|
| Architecture decision | "We'll use RFQ not AMM" | Create zettel explaining the choice |
| Insight | "Data is a depreciating asset" | Create zettel exploring implications |
| New mechanism | "Smart contract for disputes" | Create zettel documenting mechanism |
| Integration point | "Portfolio = my assets + my products" | Create zettel on architecture |

**Zettel template:**
```markdown
---
title: {Concept Title}
created: {date}
tags: [{relevant}, {tags}, {meeting-source}]
source: {Meeting Type} Meeting {date}
type: zettel
---

# {Concept Title}

## Core Concept
{One paragraph explanation}

## Key Points
{Bullet points}

## Implications
{Why this matters}

## Related Concepts
- [[Related Note 1]]
- [[Related Note 2]]
```

3. **Update Journal Entry**: Append meeting summary to `journals/YYYY-MM-DD.md`:
   - Participants, duration
   - Key clarifications (decisions in context)
   - Notable insights (quoted)
   - Action items
   - Topics covered
   - Wiki-links to created zettels

### Step 8: Generate Summary

Output using `meeting-summary.md` template with:
- Meeting metadata (type, date, duration)
- Participants
- Action items created (count and list)
- Decisions captured
- Questions resolved
- Questions raised (new)
- Items needing review (low confidence)
- **Knowledge extracted (zettels created)**
- **Journal entry updated**

## Output Example

```
MEETING PROCESSED
=================
Source: Verity Daily (Dec 17, 2025)
Duration: ~45 minutes
Participants: Crt Ahlin, Tadej Fius

Action Items Created (1)
------------------------
1. [0.85] Research SHAP machine learning concept
   -> @tadej
   Created in next_actions.org

Decisions Captured (3)
----------------------
1. Exchange uses RFQ mechanism, not AMM
2. Data products subject to ownership with liquidity tied to token
3. Disputes recorded via smart contract in dataset

Added to journal: 2025-12-17.md

Knowledge Extracted (4)
-----------------------
1. Verity-RFQ-Exchange-Mechanism.md
   - RFQ vs AMM architecture decision
2. Data-as-Depreciating-Asset.md
   - Key insight on data valuation
3. Smart-Contract-Dispute-Recording.md
   - Mechanism for on-chain dispute provenance
4. Data-Ownership-Transfer-Rights.md
   - Rights hierarchy and transfer model

Created in: 0-personal/notes/2-knowledge/zettel/

Journal Updated
---------------
Added meeting summary section to 2025-12-17.md:
- Key clarifications (4 topics)
- Insight quote: "Data is a depreciating asset"
- Action items
- Related concept links

Questions Resolved (0)
----------------------
(No GitHub question matching performed)

---
Run with --dry-run to preview without making changes.
```

## Integration

### With /meeting-prep

After meeting preparation, process the actual meeting:
```
/meeting-prep weekly-exec           # Before meeting
# ... meeting happens ...
/meeting-process <transcript-url>   # After meeting
```

### With /my-questions

Processed meetings can resolve open questions:
```
/my-questions                       # See open questions
# ... meeting discusses them ...
/meeting-process <transcript-url>   # Auto-resolves discussed questions
```

## Error Handling

| Error | Response |
|-------|----------|
| Google Docs auth not configured | Show setup instructions |
| Document not accessible | Check sharing settings message |
| No action items found | Note "No action items extracted - review transcript" |
| GitHub unavailable | Skip question matching, note limitation |
| Low confidence extractions | Flag for manual review, don't auto-create |

## Your Boundaries

**YOU CAN:**
- Fetch Google Docs via API (with OAuth)
- Read local transcript files
- Parse and extract structured data
- Create tasks in next_actions.org
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
- Respect --dry-run flag
- Use confidence threshold from settings

## Configuration

Settings from `module.yaml`:

```yaml
transcription:
  action_confidence_threshold: 0.7  # Don't auto-create below this
  decision_confidence_threshold: 0.8
  google_docs:
    enabled: true
    auto_discover: true
```
