# /meeting-agenda (DEPRECATED)

> **DEPRECATED**: This command has been superseded by meeting-type commands:
> - Use `/weekly [team]` for weekly team meetings
> - Use `/standup` for daily standups
>
> The agenda generation logic is now in the `agenda-generator` agent, which is
> invoked by the meeting-type commands. This file is kept for reference only.
>
> See: `commands/weekly.md` for the new workflow.

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Creating shareable agenda 1 day before meeting
- Need to distribute agenda to team members
- Want to ensure all relevant items are included
- Creating GitHub issue for meeting tracking

**Key decisions the module informs:**
- Which items belong in this meeting vs others
- What research is ready for discussion
- Which escalated items need team attention
- How to structure agenda for meeting duration

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | 1 day before meeting (for distribution) |
| What meeting types? | daily, weekly-exec, comms-weekly, product |
| Where is output posted? | Team space, GitHub issue, or stdout |
| What sources does it use? | GitHub Issues, org-mode tasks, escalations, calendar |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| agenda-generator | Compile items from all sources, apply templates |
| meeting-router | Ensure items are in correct meeting, detect escalations |
| question-researcher | (indirectly) Research summaries appear in agenda |

### Integration Points

- **/meeting-prep** - Run prep first, then generate agenda
- **GitHub Issues** - Questions and product issues
- **next_actions.org** - Tasks, escalations, decisions needed
- **templates/** - Meeting-specific agenda formats
- **calendar.org** - Meeting metadata

---

Generate a structured agenda for a specific meeting type.

## Workflow

### Step 1: Understand Intent

If invoked as just `/meeting-agenda` with no meeting type, ask:

"Which meeting's agenda would you like to generate?"

1. **Daily** - Quick 15-min standup agenda
2. **Weekly Exec** - Strategic review (45 min)
3. **Comms Weekly** - Content and campaigns (45 min)
4. **Product** - Technical deep-dive (60 min)

If context is clear (e.g., "create weekly exec agenda"), proceed directly.

### Step 2: Gather Context

**Ask if not provided:**
- "Which date?" (default: next occurrence)
- "Should I post it to the team space?" (--post)
- "Create a GitHub issue for it?" (--github)

**Auto-detect from calendar.org:**
- Date, time, duration
- Attendees

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

Use appropriate template with gathered data:
- `templates/agenda-daily.md` for daily
- `templates/agenda-weekly.md` for weekly
- `templates/agenda-product.md` for product

### Step 6: Post (if requested)

**Post to team space:**
- Daily: Append to today's journal
- Weekly: Create in `1-datafund/today/`
- Product: Create in product docs

**Create GitHub issue:**
- Create/update issue with agenda
- Add `agenda` label
- Assign to meeting organizer

### Step 7: Follow-up

After generating agenda, offer next steps:

"Agenda generated. Would you like to:"
- "Post it to the team space?" → Add --post flag
- "Create a GitHub issue?" → Add --github flag
- "Do more preparation?" → `/meeting-prep`
- "Process a past meeting's transcript?" → `/meeting-process`

## Meeting Types

| Type | Duration | Template | Sources |
|------|----------|----------|---------|
| `daily` | 15 min | agenda-daily.md | standups, blockers |
| `weekly-exec` | 45 min | agenda-weekly.md | escalations, questions, metrics |
| `comms-weekly` | 45 min | agenda-weekly.md | content pipeline, campaigns |
| `verity-product` | 60 min | agenda-product.md | GitHub issues, PRs, tech decisions |

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

## Difference from /meeting-prep

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/meeting-prep` | Personal preparation with full context | 2-3 days before |
| `/meeting-agenda` | Generate shareable agenda document | 1 day before |

## Error Handling

| Error | Response |
|-------|----------|
| Meeting type unknown | List available types and ask which one |
| No calendar entry | Use defaults, note missing calendar |
| No items found | Generate minimal agenda with standing items |
| GitHub API error | Skip GitHub items, note in output |

## Your Boundaries

**YOU CAN:**
- Read calendar.org
- Query GitHub via `gh` CLI
- Read org files for tasks
- Write to journal/team spaces (with post)
- Create GitHub issues (with github flag)

**YOU CANNOT:**
- Modify existing tasks
- Send calendar invites
- Access external calendars directly

**YOU MUST:**
- Include source links for all items
- Respect meeting duration limits
- Flag items needing pre-meeting prep
- Offer follow-up options after generation
