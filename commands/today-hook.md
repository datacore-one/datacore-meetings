---
name: today-hook
description: today-hook command
recall:
  # DIP-0029 default — engrams scoped to this command + tag-matched.
  scopes:
    - command:today-hook
  tags:
    - today-hook
---

# Meetings Hook: /today Integration

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Running /today command with Daily meeting scheduled
- Auto-generating standup for team meetings
- Need standup preview in daily briefing
- Calendar.org contains meeting matching standup_meeting_match setting

**Key decisions the module informs:**
- Whether to auto-generate standup based on calendar
- What data sources to use for standup content
- How to format standup for inline display in briefing
- When to skip generation (already exists, disabled, no meeting)

### Quick Reference

| Question | Answer |
|----------|--------|
| When is this hook triggered? | By /today command, after priority tasks generated |
| What activates it? | Daily meeting in calendar + auto_generate_standup: true |
| What does it add? | Standup Preview section to daily briefing |
| Where is it inserted? | After Priority Tasks, before Today's Meetings |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| standup-generator | Generate standup from yesterday's journal and today's tasks |

### Integration Points

- **/today command** - Primary integration point
- **calendar.org** - Meeting detection and attendee info
- **standup-generator** - Core standup generation
- **journals/** - Yesterday's accomplishments and today's briefing
- **settings.yaml** - auto_generate_standup configuration

---

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
Attendees: alice@organization.example.com, bob@organization.example.com, user@organization.example.com
```

**Detection algorithm:**
1. Read calendar.org
2. Find level-2 headings (`** `) matching title pattern
3. Check if timestamp contains today's date
4. Extract meeting time and attendees

## Section to Add

When triggered, this hook sets a flag that standup generation is needed.
The **actual standup generation** is handled by **Step 11-bis** in the main
`/today` command, which runs after team spaces are updated and is always
interactive (never skipped).

The hook adds a brief notice to the Daily Briefing after Priority Tasks:

```markdown
### Standup Preview

**Daily at 10:00** | Attendees: Alice, Bob

*Standup draft will be generated interactively in Step 11-bis.*
*Run `/standup` now if you want to generate it immediately.*
```

The full standup content is generated via `standup_sync.py carryover` and
written to `[space]/journal/YYYY-MM-DD.md` under `## Standup` after user
review and approval.

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
- `alice@organization.example.com` -> `Alice`
- `bob@organization.example.com` -> `Bob`
- `user@organization.example.com` -> `User`

**Rule:** Use first part of email, capitalize first letter.

## Example Output

```markdown
### Standup Preview

**Daily at 10:00** | Attendees: Alice, Bob, User

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
