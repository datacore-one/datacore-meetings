# /standup

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Preparing for daily team sync meetings
- Need to share progress updates with team
- Generating chat-friendly standup for Slack/Discord
- Tracking blockers that appear repeatedly

**Key decisions the module informs:**
- What accomplishments are team-relevant vs personal
- Which blockers need escalation to weekly meetings
- How to frame progress for different audiences (team, investor, product)

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | Morning of daily meeting, or via /today auto-generation |
| What does it parse? | Team journal [space]/journal/, carryover from standup_sync.py, next_actions.org |
| What filters apply? | Team relevance, outcome framing, anti-anxiety patterns |
| Where is output posted? | Today's team journal [space]/journal/, optionally exported for chat |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| standup-generator | Parse journals, extract accomplishments, apply filters, track escalations |
| agenda-generator | Generate daily agenda with outcomes (if --agenda flag) |
| meeting-router | Report routing changes (items escalated to weekly) |

### Integration Points

- **/today command** - Auto-invokes standup when Daily meeting detected
- **/weekly command** - Sibling command for weekly meetings
- **calendar.org** - Provides meeting time and attendee context
- **journals/** - Source for yesterday's accomplishments
- **next_actions.org** - Source for tasks and blockers

---

Generate a standup report from yesterday's journal and today's schedule.

## Workflow

### Step 1: Understand Intent

If invoked as just `/standup` with no clear context, ask:

"What type of standup would you like?"

1. **Team** - Filtered for sharing in team meeting (default)
2. **Personal** - Full detail including personal tasks
3. **Investor** - Polished for external stakeholders
4. **Product** - Technical focus for product team

If context is clear (e.g., "generate standup for weekly exec"), proceed directly.

### Step 2: Gather Context

**Ask if not provided:**
- "Which team/space?" (if team mode and multiple spaces exist)
- "For which date?" (default: today)

**Auto-detect from context:**
- If triggered via `/today` hook → Use meeting type from calendar
- If recent meeting detected → Suggest relevant preset

### Step 3: Parse Yesterday's Team Journal and Carryover

**Run carryover sync:**

```bash
python3 .datacore/lib/standup_sync.py carryover \
  --space [space_path] \
  --contributor [contributor_name]
```

This returns carried-over and completed items from yesterday's standup checkboxes,
cross-referenced against current org task state.

**Read team journal** at `[space]/journal/YYYY-MM-DD.md` for yesterday's date.
Look back up to 3 days if no yesterday journal exists.

**Extract accomplishments from new schema sections:**
- `## @{contributor}` → contributor's own work entries
- `### Done` or `### Progress` sub-sections within contributor block

**Parsing rules:**
1. Find `## @{contributor}` section in team journal
2. Extract all bullet points (`- `) under that section
3. Stop at next `##` heading
4. Filter out empty lines and sub-bullet formatting
5. Condense verbose items to single-line summaries

**Space attribution:**
Detect which space an accomplishment belongs to:
- Explicit tags: `[Team]`, `[Datacore]`, `(project-alpha)`
- Wiki-links: `[[Project Alpha]]`, `[[Team]]`
- Keywords: project names, product names
- File paths mentioned: `/1-teamspace/`, `/2-projectspace/`
- Default: current team space if no explicit attribution

**Team Project Detection:**

| Project/Product | Keywords | Space |
|-----------------|----------|-------|
| Project Alpha | project alpha, data marketplace, data RWA | teamspace |
| Project Beta | project beta, health data, longevity | teamspace |
| Datacore | datacore, module, agent, GTD system | projectspace |
| PartnerOrg | partnerorg, partner org, infrastructure | teamspace |

**Quality Validation:**

| Condition | Action |
|-----------|--------|
| <3 accomplishments found | Show confidence warning |
| All accomplishments generic | Suggest reviewing session work |
| No actionable tasks for today | Flag as incomplete |
| Weekend gap (Fri→Mon) | Look back to Friday, note gap |

### Step 4: Get Today's Plan

**Source 1: Today's journal (if `/today` already ran)**
- Read today's journal `## Daily Briefing` section
- Extract tasks under `### Priority Tasks`

**Source 2: Fallback to org files**
- Read `0-personal/org/next_actions.org`
- Find SCHEDULED items for today: `SCHEDULED: <YYYY-MM-DD>`
- Find DEADLINE items for today
- Sort by priority (A > B > C)
- Limit to top 5 items

### Step 5: Identify Blockers

**Query `next_actions.org` for:**
- Tasks with `WAITING` state
- Tasks with `:blocked:` tag
- Filter by age > `blockers_threshold_days` setting (default: 3)

**Extract blocker context:**
- Task title
- Since date (from SCHEDULED or :CREATED: property)
- Waiting reason (if `:WAITING_REASON:` property exists)

### Step 6: Apply Content Filters

**Meeting Type Presets:**

| Meeting Type | Filter Level | Focus | Blockers | Format |
|--------------|--------------|-------|----------|--------|
| `daily` | Team | Operational progress | Team-actionable | Brief |
| `weekly` | Team | Strategic progress | All team blockers | Full |
| `investor` | External | Milestones, metrics | Critical only | Polished |
| `product` | Product team | Feature progress | Technical blockers | Technical |

**A. Relevance Filter (Team Audience)**

Include only items that:
- Relate to shared projects/products
- Affect team members' work
- Are in team space (1-teamspace, etc.)

Exclude:
- Personal finance tasks
- Personal health/family items
- Individual productivity metrics
- Internal process work not visible to team

**B. Outcome Framing Filter**

Transform activity reports into outcomes:

| Activity (Don't Use) | Outcome (Use) |
|---------------------|---------------|
| "Processed 213 emails" | "Inbox zero achieved" (or omit) |
| "Created 22 tasks from triage" | (omit - internal process) |
| "Read 5 documents" | "Reviewed X proposal" (if decision-relevant) |
| "Spent 3 hours on X" | "Completed X" or "Advanced X to [state]" |

**C. Anti-Anxiety Filter**

Remove items that create worry without actionability:

| Anxiety-Inducing | Why | Action |
|------------------|-----|--------|
| "Created N tasks" | Implies more work for team | Omit |
| "Found N issues" | Implies problems | Rephrase or omit |
| "Backlog of N items" | Implies falling behind | Omit unless asking for help |

### Step 7: Generate Standup

**Output format:**
```markdown
## Standup - YYYY-MM-DD

### Yesterday
- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

### Today
- [ ] [Scheduled task 1]
- [ ] [Scheduled task 2]
- [ ] [Scheduled task 3]

### Blockers
- WAITING: [Team-relevant blocker] (since [date])
```

**Confidence Indicator:**

| Confidence | Criteria | Display |
|------------|----------|---------|
| HIGH | 4+ accomplishments, today's tasks scheduled, journal fresh | ✓ |
| MEDIUM | 2-3 accomplishments OR tasks from fallback source | ⚡ |
| LOW | <2 accomplishments OR stale journal (>2 days) | ⚠️ |

### Step 8: Post to Journal

Unless user specified not to post:
1. Write standup to today's **team journal** at `[space]/journal/YYYY-MM-DD.md`
   - If `## Standup` section exists, replace it
   - If no `## Standup` section, append after `## Daily Briefing`
   - If no `## Daily Briefing`, append at end of file
2. **Update yesterday's checkboxes**: for each item in today's standup marked `[x]`,
   find the corresponding line in yesterday's journal (by `<!-- :ID: ... -->` comment)
   and update `- [ ]` → `- [x]`
3. **Sync org tasks** via `standup_sync.py`:
   - For new today items without org IDs, call `standup_sync.py create`
   - For completed items, call `standup_sync.py check-off --id [task-id]`

### Step 9: Follow-up

After generating standup, offer next steps:

"Standup generated. Would you like to:"
- "Copy chat-friendly format for Slack?" → Generate `--format chat` version
- "Prepare for your meeting?" → `/meeting-prep`
- "See open questions for the team?" → `/my-questions`
- "Process a meeting transcript?" → `/meeting-process`

## Output Examples

### Team Standup (Daily meeting)

```
STANDUP GENERATED (Team: Team)
----------------------------------

Yesterday:
- Shipped mail module v1.1.0 (automation improvement)
- Completed DSAlliance competitive analysis
- Reviewed investor pitch deck feedback

Today:
- [ ] Review POC_SPRINT_PLAN_PROPOSAL.md
- [ ] Sprint planning meeting (10:00)
- [ ] Comms Weekly (14:00)

Blockers:
- WAITING: ERC-3643 evaluation - need legal input (since Dec 3)

[Posted to journal: 0-personal/notes/journals/2025-12-18.md]
```

### Chat Export Format

Compact format for Slack/Discord posting:

```
📋 *Standup - Dec 19*

*Yesterday:*
• Shipped mail module v1.1.0
• Completed DSAlliance competitive analysis
• Reviewed investor pitch deck

*Today:*
• POC sprint planning
• Comms Weekly

*Blockers:* ERC-3643 eval (need legal)
```

## Error Handling

| Error | Response |
|-------|----------|
| Yesterday's journal not found | Look back up to 3 days for last journal |
| No accomplishments found | Include: "(no logged accomplishments)" and suggest reviewing session work |
| No scheduled tasks | Include: "Review priorities in next_actions.org" |
| No blockers | Omit Blockers section entirely |

## Configuration

Settings in `settings.local.yaml`:

```yaml
meetings:
  auto_generate_standup: true      # Auto-generate on /today
  standup_meeting_match: "Daily"   # Calendar title to match
  blockers_threshold_days: 3       # Days before WAITING becomes blocker
  post_to_journal: true            # Auto-post to journal
  default_team_mode: true          # Default to team filtering
```

## Your Boundaries

**YOU CAN:**
- Read team journal files in `[space]/journal/`
- Read org files in `[space]/org/`
- Read calendar.org for meeting context
- Write standup to today's team journal
- Update yesterday's journal checkboxes (checked state only)
- Run `standup_sync.py carryover`, `standup_sync.py create`, `standup_sync.py check-off`
- Generate chat-formatted output

**YOU CANNOT:**
- Read personal journals in `0-personal/notes/journals/`
- Modify org files directly (use standup_sync.py instead)
- Delete existing journal content (beyond checkbox updates)
- Access external calendar APIs
- Post directly to Slack/Discord

**YOU MUST:**
- Preserve existing journal content when appending
- Use wiki-links `[[YYYY-MM-DD]]` for date references
- Format output for both terminal and markdown readability
- Offer follow-up options after generation
