# Meetings Hook: /today Integration

This hook adds standup generation to the daily briefing when a Daily meeting is detected.

## Trigger

Called by `/today` command when meetings module is installed.

## Activation Conditions

Generate standup ONLY if ALL conditions are met:
1. `settings.auto_generate_standup` is `true`
2. Today's calendar.org has meeting matching `settings.standup_meeting_match` (default: "Daily")
3. Today's journal does not already have `## Standup` section

## Calendar Detection

**Parse `0-personal/org/calendar.org` for today's date:**

Look for entries matching:
```
** [Title matching standup_meeting_match]
<YYYY-MM-DD [Day] HH:MM-HH:MM>
Attendees: [email list]
```

**Example match:**
```org
** Daily
<2025-12-18 Thu 10:00-10:15>
Attendees: crt.ahlin@datafund.io, tadej.fius@datafund.io, gregor@datafund.io
```

**Detection algorithm:**
1. Read calendar.org
2. Find level-2 headings (`** `) matching title pattern
3. Check if timestamp contains today's date
4. Extract meeting time and attendees

## Section to Add

When standup is generated, add to the Daily Briefing after Priority Tasks:

```markdown
### Standup Preview

**Daily at 10:00** | Attendees: Crt, Tadej

**Yesterday:**
- Processed 213 emails - inbox zero achieved
- Released mail module v1.1.0
- Completed DSAlliance competitive analysis

**Today:**
- [ ] Review POC_SPRINT_PLAN_PROPOSAL.md
- [ ] Sprint planning (10:00)
- [ ] Comms Weekly (14:00)

**Blockers:**
- WAITING: ERC-3643 evaluation (since Dec 3)

*Edit and share in Daily meeting.*
```

## Data Sources

| Data | Source | Method |
|------|--------|--------|
| Yesterday's accomplishments | Previous journal | Section extraction |
| Today's tasks | Priority Tasks (just generated) | Already in briefing |
| Blockers | next_actions.org WAITING items | Org-mode parser |
| Meeting time/attendees | calendar.org | Pattern match |

## Integration Point

Insert `### Standup Preview` after Priority Tasks, before Nightshift Results:

```
## Daily Briefing

### Focus
[...]

### Priority Tasks
[...]

### Standup Preview    <-- INSERT HERE
[...]

### Today's Meetings
[...]

### Nightshift Results
[...]
```

## Conditions

| Condition | Behavior |
|-----------|----------|
| No Daily meeting today | Skip standup generation entirely |
| Standup already exists in journal | Skip (avoid duplicate) |
| `auto_generate_standup: false` | Skip |
| Yesterday's journal missing | Generate with "(no journal found)" placeholder |
| No blockers found | Omit Blockers section |

## Attendee Formatting

Convert email addresses to display names:
- `crt.ahlin@datafund.io` -> `Crt`
- `tadej.fius@datafund.io` -> `Tadej`
- `gregor@datafund.io` -> `Gregor`

**Rule:** Use first part of email, capitalize first letter.

## Example Output

```markdown
### Standup Preview

**Daily at 10:00** | Attendees: Crt, Tadej, Gregor

**Yesterday:**
- Processed 213 emails - inbox zero
- Released mail module v1.1.0
- DSAlliance competitive analysis completed

**Today:**
- [ ] Review PoC sprint plan proposal
- [ ] PoC sprint planning meeting
- [ ] Comms Weekly

**Blockers:**
- ERC-3643 evaluation on hold (Dec 3)

*Ready to share. Edit if needed.*
```
