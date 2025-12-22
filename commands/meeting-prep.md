# /meeting-prep

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Preparing 2-3 days before important meetings
- Need to research open questions before discussions
- Want to identify what prep work is needed from you or stakeholders
- Reviewing escalated items before weekly meetings

**Key decisions the module informs:**
- Which questions need AI research before the meeting
- What preparation tasks require your input
- Whether stakeholders have prepared adequately
- What context from past meetings is relevant

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | 2-3 days before meeting (allows time for research) |
| What does it check? | Open questions, escalated items, stakeholder prep status |
| Does it trigger research? | Yes, with --research flag |
| What's the output? | Personal preparation report with action items |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| question-researcher | Research open questions (with --research flag) |
| agenda-generator | Gather candidate agenda items |
| meeting-router | Determine which items belong in this meeting |

### Integration Points

- **GitHub Issues** - Open questions data source
- **next_actions.org** - Your tasks needing discussion, escalated items
- **calendar.org** - Meeting details (date, time, attendees)
- **/meeting-agenda** - Next step after prep is generating shareable agenda

---

Prepare for a specific meeting with full context and pre-research.

## Workflow

### Step 1: Understand Intent

If invoked as just `/meeting-prep` with no meeting type, ask:

"Which meeting would you like to prepare for?"

1. **Daily** - Quick standup prep
2. **Weekly Exec** - Strategic review preparation
3. **Comms Weekly** - Content and campaigns focus
4. **Product** - Technical deep-dive (Verity, Santorio)

If context is clear (e.g., "prepare for tomorrow's weekly"), proceed directly.

### Step 2: Gather Context

**Ask if not provided:**
- "Which date?" (default: next occurrence)
- "Should I research open questions?" (triggers AI research)

**Auto-detect:**
- From calendar.org, find next occurrence of meeting type
- Extract date, time, duration, attendees

### Step 3: Gather Preparation Data

**Open Questions (GitHub):**
```bash
gh issue list --label question --state open --json number,title,body,labels,assignees
```

Filter by:
- `meeting:weekly` label for weekly meetings
- Product repo for product meetings

**Your Tasks Needing Discussion (org-mode):**

Scan `next_actions.org` for items that should be on the agenda:

| Tag/Condition | Include In |
|---------------|------------|
| `:decision:` | Decisions section |
| `:discuss:` or `:@team:` | Discussion items |
| `:blocked:` with team dependency | Blockers section |
| `[#A]` + deadline in 7 days | Strategic items |
| `:investor:` or `:roadmap:` | Strategic items |

**Escalated Items:**
Query `next_actions.org` for `:DAILY_COUNT:` >= 3

**Past Meeting Context:**
- Search journals for previous meeting notes
- Look for unresolved action items

### Step 4: Trigger AI Research (if requested)

For each open question without `researched` label:
1. Invoke `question-researcher` agent
2. Add research summary to GitHub issue
3. Add `researched` label

### Step 5: Check Stakeholder Preparation

For each question with stakeholders:
- Check if they've commented on the issue
- Check if assigned tasks are complete
- Flag items with missing input

### Step 6: Generate Preparation Report

**Sections:**

1. **Meeting Overview** - Type, date, duration, attendees
2. **Your Preparation Tasks** - Questions needing your input
3. **Open Questions Status** - Ready, needs research, waiting
4. **Escalated Items** - Items appearing 3+ times in dailies
5. **Context from Past Meetings** - Relevant decisions
6. **Stakeholder Status** - Who has/hasn't prepared

### Step 7: Follow-up

After generating prep report, offer next steps:

"Preparation report ready. Would you like to:"
- "Trigger AI research on open questions?" → Run with research
- "Generate the shareable agenda?" → `/meeting-agenda`
- "See all open questions?" → `/my-questions`

## Output Example

```
MEETING PREPARATION
===================
Weekly Exec - Thu Dec 19, 14:00
Days until meeting: 2

Your Preparation Tasks
----------------------
1. [ ] Provide input on pricing tiers (#45)
      Deadline: Dec 18 (tomorrow)
2. [ ] Review database comparison doc
      Needed for: #42 discussion

Your Tasks for Agenda
---------------------
Decisions Needed:
  - [#A] Finalize investor pitch approach :decision:
  - Choose between Next.js vs Remix :decision:@team:

Discussion Items:
  - Review Verity pricing model :discuss:
  - Sprint velocity concerns :@team:

Open Questions (4)
------------------
Ready for Discussion:
  - [#42] Database selection (AI researched)
  - [#38] API rate limiting (AI researched)

Needs Research:
  - [#47] OAuth provider comparison

Stakeholder Status
------------------
@crt: Ready (commented on 2/3 questions)
@tadej: Needs prep (no comments yet)
@gregor: Action needed (1 question waiting)

---
Run '/meeting-prep weekly-exec --research' to trigger AI research
```

## Difference from /meeting-agenda

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/meeting-prep` | Personal preparation with full context | 2-3 days before, for research |
| `/meeting-agenda` | Generate shareable agenda document | 1 day before, for distribution |

## Error Handling

| Error | Response |
|-------|----------|
| Meeting not in calendar | Show next scheduled or offer to use defaults |
| No questions found | Note "No open questions", focus on escalations |
| GitHub unavailable | Show cached data, note limitation |
| Research fails | List failed items, suggest retry |

## Configuration

Settings in `settings.local.yaml`:

```yaml
meetings:
  questions:
    github_label: "question"
    auto_research: true
    research_model: haiku
```

## Your Boundaries

**YOU CAN:**
- Read calendar.org
- Query GitHub Issues
- Read org files and journals
- Invoke question-researcher agent (with research)
- Add comments and labels to GitHub issues

**YOU CANNOT:**
- Modify org files directly
- Send reminders to stakeholders
- Access external calendar APIs

**YOU MUST:**
- Highlight items requiring user action
- Show clear deadlines
- Provide context for informed preparation
- Offer follow-up options after generation
