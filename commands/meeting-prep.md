# /meeting-prep

Prepare for a specific meeting with full context and pre-research.

## Usage

```
/meeting-prep <type> [--date YYYY-MM-DD] [--research]
```

## Options

| Option | Description |
|--------|-------------|
| `type` | Meeting type: `daily`, `weekly-exec`, `comms-weekly`, `verity-product` |
| `--date` | Target date (default: next occurrence) |
| `--research` | Trigger AI research on open questions |

## Difference from /meeting-agenda

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/meeting-agenda` | Generate shareable agenda document | 1 day before, for distribution |
| `/meeting-prep` | Personal preparation with full context | 2-3 days before, for research |

`/meeting-prep` includes:
- AI research on questions
- Your action items for prep
- Context from past meetings
- Stakeholder preparation status

## Algorithm

### Step 1: Identify Meeting

From `calendar.org`, find next occurrence of meeting type:
```org
* Weekly Exec
  <2025-12-19 Thu 14:00-14:45>
  - Attendees: @gregor, @crt, @tadej
```

### Step 2: Gather Preparation Context

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
| Blocking another team member | Blocking Others |

**Escalated Items (org-mode):**
Query `next_actions.org` for `:DAILY_COUNT:` >= 3

**Past Meeting Context:**
- Search journals for previous meeting notes
- Look for unresolved action items

### Step 3: Trigger AI Research (if --research)

For each open question without `researched` label:
1. Invoke `question-researcher` agent
2. Add research summary to GitHub issue
3. Add `researched` label

### Step 4: Check Stakeholder Preparation

For each question with stakeholders:
- Check if they've commented on the issue
- Check if assigned tasks are complete
- Flag items with missing input

### Step 5: Generate Preparation Report

**Sections:**

1. **Meeting Overview**
   - Type, date, duration, attendees
   - Days until meeting

2. **Your Preparation Tasks**
   - Questions needing your input
   - Items you're responsible for
   - Deadlines before meeting

3. **Open Questions Status**
   - Ready for discussion (researched)
   - Needs research (trigger with --research)
   - Waiting for input (blocked on someone)

4. **Escalated Items**
   - Items appearing 3+ times in dailies
   - Context on why they're stuck

5. **Context from Past Meetings**
   - Relevant decisions from recent meetings
   - Unresolved action items

6. **Stakeholder Status**
   - Who has prepared
   - Who needs to prepare
   - Missing inputs

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
    Deadline: Dec 22 (before investor meeting)
  - Choose between Next.js vs Remix :decision:@team:
    Context: Affects Q1 roadmap

Discussion Items:
  - Review Verity pricing model :discuss:
  - Sprint velocity concerns :@team:

Blocking Others:
  - Review PR #42 (blocking @tadej since Dec 15)

Open Questions (4)
------------------
Ready for Discussion:
  - [#42] Database selection (AI researched)
  - [#38] API rate limiting (AI researched)

Needs Research (run with --research):
  - [#47] OAuth provider comparison

Waiting for Input:
  - [#45] Pricing tiers - waiting for @gregor (you)

Escalated from Daily (2)
------------------------
1. API authentication approach
   - 4 appearances since Dec 12
   - Blocker: Needs security review

2. Database migration timing
   - 3 appearances since Dec 14
   - Context: Depends on #42 decision

Stakeholder Status
------------------
@crt: Ready (commented on 2/3 questions)
@tadej: Needs prep (no comments yet)
@gregor: Action needed (1 question waiting, 1 blocking review)

Context from Past Meetings
--------------------------
Dec 12 Weekly:
  - Decided to delay Series A until Q1
  - Action: @gregor to update investor timeline (DONE)

Dec 5 Weekly:
  - Discussed database options, no decision
  - Escalated to this week

---
Run '/meeting-prep weekly-exec --research' to trigger AI research
```

## Integration

### With /today

If meeting is today or tomorrow:
```
📅 Meeting Prep Reminder
   Weekly Exec in 1 day (Thu 14:00)
   - 2 questions need your input
   - Run: /meeting-prep weekly-exec
```

### With /meeting-agenda

After preparation is complete:
```
✓ Preparation complete
  Run: /meeting-agenda weekly-exec --post
  to generate and distribute the agenda
```

## Error Handling

| Error | Response |
|-------|----------|
| Meeting not in calendar | Show next scheduled or use defaults |
| No questions found | Note "No open questions", focus on escalations |
| GitHub unavailable | Show cached data, note limitation |
| --research fails | List failed items, suggest retry |

## Your Boundaries

**YOU CAN:**
- Read calendar.org
- Query GitHub Issues
- Read org files and journals
- Invoke question-researcher agent (with --research)
- Add comments and labels to GitHub issues

**YOU CANNOT:**
- Modify org files directly
- Send reminders to stakeholders
- Access external calendar APIs

**YOU MUST:**
- Highlight items requiring user action
- Show clear deadlines
- Provide context for informed preparation
