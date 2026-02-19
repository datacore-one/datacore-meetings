# /weekly

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Preparing for recurring weekly team calls
- Need to create/update agenda with GitHub Issue + calendar event
- Aggregating items from multiple sources (org, GitHub, PRs)
- Running `/gtd-weekly-review` final step

**Key decisions the module informs:**
- Which items belong in this weekly vs next
- What outcomes/goals are needed per agenda item
- Who needs to prepare what before the meeting
- Which GitHub issues to cross-reference

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | 1-2 days before weekly meeting |
| What does it aggregate? | Org tasks, GitHub Issues/PRs, escalations, previous action items |
| What does it produce? | Draft agenda, GitHub Issue, updated calendar event with invites |
| What's unique? | Full end-to-end: prep → issue → calendar update → invites in one command |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| agenda-generator | Aggregate items from all sources, apply routing |
| meeting-router | Ensure items belong in weekly, detect escalations |
| question-researcher | Pre-research open questions (with --research flag) |

### Integration Points

- **/gtd-weekly-review** - Hook at end prompts for weekly prep
- **/standup** - Daily escalations feed into weekly
- **GitHub Issues** - Source + destination (creates meeting issue)
- **Google Calendar** - Updates existing event with agenda, sends invites
- **next_actions.org** - Task source, escalation tracking

---

Prepare and schedule recurring weekly team meetings with full workflow.

## Design Principles (Learned Patterns)

1. **Multi-Source Aggregation**: Pull from personal org, team org, GitHub Issues, PRs
2. **Iterative Refinement**: Draft → user feedback → refined agenda
3. **Outcome-Driven Design**: Every agenda item has explicit goal
4. **Pre-Meeting Prep Identification**: Clear assignments per attendee
5. **GitHub Issue as Source of Truth**: Meeting lives in issue, calendar links to it
6. **Calendar Update + Invites**: Update existing recurring event, invite participants

## Workflow

### Step 1: Understand Intent

If invoked as just `/weekly` with no team specified:

"Which team's weekly would you like to prepare?"

1. **Team** - Weekly team call
2. **Project** - Weekly project sync
3. **Custom** - Specify meeting name

If team is clear from context (e.g., in `1-teamspace/` directory), proceed directly.

### Step 2: Find Existing Calendar Entry

**Search calendar for existing weekly:**
```python
# Look for recurring weekly matching team
events = calendar_adapter.get_events(
    start=today,
    end=today + timedelta(days=7),
    query="Weekly Team"  # or team pattern
)
```

**If found:**
- Extract: date, time, duration, existing attendees, Zoom link
- Note: "Found existing calendar entry for [date] [time]"

**If not found:**
- Ask: "No weekly found. When should it be? (e.g., Monday 13:00)"
- Offer to create new recurring event

### Step 3: Verify and Update Attendees

**Team attendee configuration:**
```yaml
# From settings or team config
attendees:
  teamspace:
    - user@organization.example.com
    - alice@organization.example.com
    - bob@organization.example.com
  projectspace:
    - user@project.example.com
```

**Check current vs required attendees:**
- Compare existing event attendees with team config
- Identify missing invites
- Note: "@alice and @bob will be invited"

**Allow customization:**
- "Add anyone else to this meeting?"
- "Remove anyone from this meeting?"

### Step 4: Aggregate Sources (Parallel)

**A. Personal Org Tasks (`0-personal/org/next_actions.org`):**
- Items tagged `:@weekly:` or `:discuss:` or `:decision:`
- Priority `[#A]` items with deadline in next 7 days
- Items tagged with team/project keywords

**B. Team Org Tasks (`[team]/org/next_actions.org`):**
- All items in team org file
- Escalated items (`:DAILY_COUNT:` >= 3)
- Items tagged `:team:` or `:@weekly:`

**C. GitHub Issues:**
```bash
gh issue list --repo [team-repo] --label weekly --state open
gh issue list --repo [team-repo] --label decision --state open
gh issue list --repo [team-repo] --label discuss --state open
```

**D. GitHub PRs:**
```bash
gh pr list --repo [team-repo] --state open
```
- Flag PRs older than 7 days
- Flag PRs with requested changes

**E. Previous Meeting Action Items:**
- Search for previous weekly issue
- Extract unclosed action items (checkboxes not checked)

**F. Escalated from Daily:**
- Query items with `:DAILY_COUNT:` >= 3
- These MUST appear in weekly agenda

### Step 5: Generate Draft Agenda

**Group by theme/track (not by source):**

```markdown
## Draft Agenda - [Team] Weekly

### 1. Business Updates (10min) - Updates
**Goal**: Share status updates (no discussion needed)
- Item 1
- Item 2

### 2. [Topic from escalation] (15min) - Decision
**Goal**: [Auto-generated based on issue/task]
- From: #issue or task
**References**: [links]

### 3. [Topic from GitHub] (10min) - Alignment
**Goal**: Agree on approach
- Key points
**References**: #issue

[... more items ...]

### Coming Up
- Items for awareness, not discussion
```

**Time allocation guidelines:**
| Goal Type | Duration |
|-----------|----------|
| Update | 5-10min |
| Decision | 10-15min |
| Alignment | 10-15min |
| Brainstorm | 15-20min |
| Review | varies |

### Step 6: Present Draft for Refinement

Show draft to user with:
- Source attribution per item
- Total time estimate
- Items that could be deferred

"Here's the draft agenda (105min estimated). Would you like to:"
- "Focus on specific topics?"
- "Add items?"
- "Remove or defer items?"
- "Adjust time allocations?"

**Refinement signals:**
| User Says | Action |
|-----------|--------|
| "Focus on X" | Elevate X, reduce others |
| "Not X" / "Skip X" | Remove item |
| "Add Y" | Include new item, ask for goal |
| "Combine A and B" | Merge into single item |
| "X should be 20min" | Adjust time allocation |
| "Looks good" | Proceed to Step 7 |

### Step 7: Identify Pre-Meeting Preparation

For each agenda item, identify prep needed:

**Auto-detect prep requirements:**
| Item Type | Prep Required |
|-----------|---------------|
| GitHub Issue discussion | "Review #issue" |
| PR review needed | "Review PR #N" |
| Decision item | "Prepare position on X" |
| Status update | "Prepare update on X" |
| Document reference | "Read [doc]" |

**Assign to attendees:**
- If item has owner → they prepare
- If item has assignee → they prepare
- Otherwise → ask user to assign

**Output:**
```markdown
## Pre-Meeting Preparation
- [ ] @user: Review DMCC proposal draft, finalize numbers
- [ ] @alice: Prepare Project Alpha sprint status update
- [ ] @bob: Review #220, come with questions
```

### Step 8: Add Outcomes per Item

For items without explicit goals, auto-generate:

| Item Pattern | Auto-Generated Goal |
|--------------|---------------------|
| PR discussion | "Decide: merge, request changes, or close" |
| Blocker item | "Unblock: identify owner and next step" |
| Status update | "Update: share progress, surface blockers" |
| New feature | "Align: agree on approach" |
| Process issue | "Decide: adopt, modify, or reject proposal" |

Present to user: "I've added goals to each item. Review and adjust?"

### Step 9: Create GitHub Issue (--create-issue)

If `--create-issue` flag or user confirms:

**Issue structure:**
```markdown
## Meeting Info
- **Date/Time**: YYYY-MM-DD HH:MM CET
- **Duration**: 90 min
- **Attendees**: @user, @alice, @bob
- **Zoom**: [Join Meeting](link)

## Pre-Meeting Preparation
- [ ] @person: Task (link)

## Agenda

### 1. [Topic] (Xmin) - @owner
**Goal**: [Outcome statement]
- Point 1
- Point 2
**References**: #issue, [doc](link)

### 2. [Topic] (Xmin) - @owner
...

## Decisions Made
(Fill during/after meeting)

## Action Items
(Fill during/after meeting)
- [ ] @person: Task - Due: YYYY-MM-DD
```

**After creation:**
- Add `meeting` label (create if needed)
- Add comments to referenced issues: "Scheduled for discussion in #[meeting-issue]"

### Step 10: Update Calendar Event + Send Invites (--calendar)

If `--calendar` flag or user confirms:

**Update existing event:**
```python
from .datacore.lib.sync.adapters.google_calendar import GoogleCalendarAdapter
import pytz

# Find existing event
event = adapter.find_event(query="Weekly Team", date=meeting_date)

# Update description with agenda
event.description = f"""GitHub Issue: https://github.com/{org}/{repo}/issues/{issue_num}

{full_agenda}
"""

# Ensure all team members are invited
required_attendees = [
    "user@organization.example.com",
    "alice@organization.example.com",
    "bob@organization.example.com"
]
for attendee in required_attendees:
    if attendee not in event.attendees:
        event.attendees.append(attendee)

# Update event (sends invites to new attendees)
adapter.update_event(event, send_updates=True)
```

**If no existing event (create new):**
```python
tz = pytz.timezone('Europe/Ljubljana')
start = tz.localize(datetime(YYYY, MM, DD, HH, MM))
end = start + timedelta(minutes=duration)

entry = OrgCalendarEntry(
    title=f"{team} Weekly - {key_topic}",
    timestamp=start,
    end_time=end,
    description=agenda_with_issue_link,
    location=zoom_link,
    attendees=required_attendees
)
adapter.create_task(entry, send_invites=True)
```

**Invite notification:**
```
Calendar Updated:
- Event: Team Weekly - DMCC Focus
- Date: Mon Jan 5, 13:00-14:30 CET
- Invites sent to: @alice, @bob (new), @user (organizer)
- Description updated with agenda
```

### Step 11: Summary and Follow-up

```
WEEKLY PREPARED
===============
Team: Team
Date: Mon Jan 5, 13:00 CET (90min)
Attendees: @user (organizer), @alice, @bob

GitHub Issue: #222 (created)
Calendar: Updated ✓ (invites sent)

Agenda Items: 7
- Business Update (10min)
- DMCC Proposal (15min) - Decision
- Project Alpha Sprint (15min) - Update
- ...

Pre-Meeting Prep: 4 tasks assigned
- @alice: Review DMCC proposal
- @bob: Review #220
- ...

Next: Team will receive calendar invite with full agenda
```

**Follow-up options:**
- "Open the GitHub issue?" → Open in browser
- "Copy agenda for Slack?" → Generate chat-friendly format
- "Add more items?" → Return to Step 6
- "Process after meeting?" → After meeting, run `/meeting-process #222`

## Flags

| Flag | Purpose |
|------|---------|
| `--create-issue` | Create GitHub Issue for meeting |
| `--calendar` | Update calendar event + send invites |
| `--research` | Trigger AI research on open questions |
| `--dry-run` | Show what would be created/updated, don't execute |
| `--team [name]` | Specify team (teamspace, projectspace) |
| `--date [date]` | Override meeting date |
| `--no-invites` | Update calendar but don't send invite notifications |

## Integration with /gtd-weekly-review

When `/gtd-weekly-review` completes, hook prompts:

```
GTD Weekly Review complete.

Upcoming team meetings detected:
- Team Weekly: Mon Jan 5, 13:00

Would you like to prepare the agenda?
→ Run /weekly teamspace
```

## Error Handling

| Error | Response |
|-------|----------|
| No meeting in calendar | Ask for date/time, offer to create |
| No items found | Generate minimal agenda with standing items |
| GitHub unavailable | Skip GitHub items, note limitation |
| Calendar API fails | Generate agenda without event, provide manual details |
| Team repo not found | Ask for repo, update settings |
| Attendee email invalid | Flag issue, ask for correct email |

## Configuration

Settings in module.yaml `meeting_types`:

```yaml
weekly-teamspace:
  name: "Team Weekly"
  duration: 90
  calendar_match: "Weekly Team"
  github_repo: "org-name/project-alpha"
  attendees:
    - email: "user@organization.example.com"
      role: organizer
    - email: "alice@organization.example.com"
      role: attendee
    - email: "bob@organization.example.com"
      role: attendee
  standing_items:
    - "Business Update"
    - "Coming Up"
  escalate_from_daily: true
```

## Difference from Other Commands

| Command | Purpose | When |
|---------|---------|------|
| `/standup` | Generate standup for daily | Morning of daily |
| `/weekly` | Full weekly prep + GitHub + calendar + invites | 1-2 days before weekly |
| `/meeting-prep` | Personal prep (no issue/calendar) | 2-3 days before any meeting |

## Your Boundaries

**YOU CAN:**
- Read org files and journals
- Query GitHub Issues and PRs via `gh` CLI
- Create GitHub Issues
- Update calendar events via adapter
- Add attendees and send invites via adapter
- Add comments to GitHub Issues
- Write to journal files

**YOU CANNOT:**
- Modify existing org tasks
- Delete GitHub Issues
- Send emails or Slack messages directly
- Access external calendars without adapter

**YOU MUST:**
- Always include GitHub Issue link in calendar description
- Ensure all team members are invited to calendar event
- Cross-reference discussed issues in meeting issue
- Respect time allocations in agenda
- Identify pre-meeting prep for each substantive item
- Confirm before sending invites (unless --no-confirm)
- Offer follow-up options after completion
