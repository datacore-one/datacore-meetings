# Meetings Module Context

This module automates meeting lifecycle management.

## Commands

### /standup

Generate a standup report from yesterday's journal and today's schedule.

**Algorithm:**
1. Parse yesterday's journal for accomplishments
2. Get today's tasks from Priority Tasks or next_actions.org
3. Find blockers from WAITING tasks > 3 days old
4. Generate formatted output
5. Post to today's journal (unless --no-post)

**Data sources:**
- `0-personal/notes/journals/YYYY-MM-DD.md` - Yesterday's accomplishments
- `0-personal/org/next_actions.org` - Today's tasks, blockers
- `0-personal/org/calendar.org` - Meeting detection

**Journal sections to parse:**
- `### Yesterday's Wins` - Explicit accomplishments
- `### Session Work` - Work session details
- `### Stats` - Quantitative metrics

## /today Hook

When meetings module is installed, `/today` checks for Daily meetings:
- Parse `calendar.org` for meetings matching `standup_meeting_match` setting
- If found and standup not already generated, add `### Standup Preview` section

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_generate_standup` | true | Generate standup in /today |
| `standup_meeting_match` | "Daily" | Calendar title pattern |
| `blockers_threshold_days` | 3 | Days before WAITING is blocker |
| `post_to_journal` | true | Auto-post standup |

## Boundaries

**YOU CAN:**
- Read journal files in `notes/journals/`
- Read org files in `org/`
- Read `calendar.org` for meeting detection
- Write standup to today's journal

**YOU CANNOT:**
- Modify org files (tasks, priorities)
- Delete journal content
- Access external APIs directly

## Output Format

```markdown
## Standup - YYYY-MM-DD

### Yesterday
- [accomplishment 1]
- [accomplishment 2]

### Today
- [ ] [task 1]
- [ ] [task 2]

### Blockers
- WAITING: [description] (since [date])
```
