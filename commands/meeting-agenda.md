# /meeting-agenda

Generate a structured agenda for a specific meeting type.

## Usage

```
/meeting-agenda <type> [--date YYYY-MM-DD] [--post] [--github]
```

## Options

| Option | Description |
|--------|-------------|
| `type` | Meeting type: `daily`, `weekly-exec`, `comms-weekly`, `verity-product` |
| `--date` | Target date (default: next occurrence) |
| `--post` | Post agenda to team space or journal |
| `--github` | Create/update GitHub issue with agenda |

## Meeting Types

| Type | Duration | Template | Sources |
|------|----------|----------|---------|
| `daily` | 15 min | agenda-daily.md | standups, blockers |
| `weekly-exec` | 45 min | agenda-weekly.md | escalations, questions, metrics |
| `comms-weekly` | 45 min | agenda-weekly.md | content pipeline, campaigns |
| `verity-product` | 60 min | agenda-product.md | GitHub issues, PRs, tech decisions |

## Algorithm

### Step 1: Detect Meeting Context

From `calendar.org`, find the meeting entry:
```org
* Weekly Exec
  <2025-12-19 Thu 14:00-14:45>
  - Attendees: @gregor, @crt, @tadej
```

Extract:
- Date and time
- Duration
- Attendees

### Step 2: Invoke Agenda Generator Agent

Pass to `agenda-generator` agent:
- Meeting type and config
- Date
- Attendees
- Sources to query

### Step 3: Gather Items per Meeting Type

**Daily:**
- Individual standups (from `/standup` output)
- Active blockers from WAITING tasks
- Escalation candidates (`:DAILY_COUNT:` >= 2)

**Weekly-exec:**
- Escalated items (`:DAILY_COUNT:` >= 3)
- Open questions with `meeting:weekly` label
- Strategic items from next_actions.org with `[#A]` priority
- Key metrics (if configured)

**Product (verity-product, etc.):**
- GitHub issues from product repo
- Open PRs needing review
- Technical questions
- Architecture decisions pending

### Step 4: Apply Routing Rules

Ensure items are in the right meeting:

| Item Type | Route |
|-----------|-------|
| Urgent blocker | Daily |
| Multi-stakeholder decision | Weekly |
| Technical architecture | Product |
| 3+ daily appearances | Escalate to Weekly |

### Step 5: Render Agenda

Use appropriate template with gathered data.

### Step 6: Post (if requested)

**--post flag:**
- Daily: Append to today's journal
- Weekly: Create in `1-datafund/today/` or team space
- Product: Create in product docs or GitHub

**--github flag:**
- Create/update GitHub issue with agenda
- Add `agenda` label
- Assign to meeting organizer

## Output Example

```
MEETING AGENDA GENERATED
========================
Type: Weekly Exec
Date: 2025-12-19 Thu 14:00
Duration: 45 min
Attendees: @gregor, @crt, @tadej

Escalated from Daily (2)
------------------------
1. API authentication approach (4x since Dec 12)
2. Database migration timing (3x since Dec 14)

Open Questions (3)
------------------
1. [#42] Database selection - AI: PostgreSQL (85%)
2. [#45] Pricing tiers - Needs @gregor input
3. [#38] Rate limiting - Ready for discussion

Strategic Items (1)
-------------------
1. [#A] Finalize Series A timeline

Decisions Needed (2)
--------------------
1. Approve Dubai pilot contract
2. Engineering roadmap priorities

---
[Posted to: 1-datafund/today/2025-12-19-weekly-exec.md]
```

## Error Handling

| Error | Response |
|-------|----------|
| Meeting type unknown | List available types |
| No calendar entry | Use defaults, note missing calendar |
| No items found | Generate minimal agenda with standing items |
| GitHub API error | Skip GitHub items, note in output |

## Your Boundaries

**YOU CAN:**
- Read calendar.org
- Query GitHub via `gh` CLI
- Read org files for tasks
- Write to journal/team spaces (with --post)
- Create GitHub issues (with --github)

**YOU CANNOT:**
- Modify existing tasks
- Send calendar invites
- Access external calendars directly

**YOU MUST:**
- Include source links for all items
- Respect meeting duration limits
- Flag items needing pre-meeting prep
