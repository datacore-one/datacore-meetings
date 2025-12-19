# /standup

Generate a standup report from yesterday's journal and today's schedule.

## Usage

```
/standup [--date YYYY-MM-DD] [--team SPACE] [--meeting TYPE] [--format FORMAT] [--no-post]
```

## Options

| Option | Description |
|--------|-------------|
| `--date` | Generate standup for specific date (default: today) |
| `--team` | Filter for specific team/space (e.g., `datafund`, `datacore`) |
| `--meeting` | Meeting type preset: `daily`, `weekly`, `investor`, `product` |
| `--format` | Output format: `full` (default), `chat` (Slack/Discord), `brief` |
| `--no-post` | Display standup without posting to journal |
| `--personal` | Force personal mode (include all items) |

When triggered via `/today` hook for a Daily meeting, automatically uses `--team` mode based on meeting attendees.

## Algorithm

### Step 1: Parse Yesterday's Journal

Read `0-personal/notes/journals/YYYY-MM-DD.md` for yesterday's date.

**Extract accomplishments from sections:**
- `### Yesterday's Wins` - Bullet points of wins
- `### Session Work` - Work session summaries
- `### Stats` - Metrics and completions

**Parsing rules:**
1. Find section headers matching the configured sections
2. Extract all bullet points (`- `) under those sections
3. Stop at next `##` or `###` heading
4. Filter out empty lines and sub-bullet formatting
5. Condense verbose items to single-line summaries

**Session Work capture:**
- Also check for `## Session Work` or `## Work Log` sections
- These contain real-time session summaries that may not appear in "Yesterday's Wins"
- Session work is often more current than curated wins

**Space attribution:**
Detect which space an accomplishment belongs to:
- Explicit tags: `[Datafund]`, `[Datacore]`, `(verity)`
- Wiki-links: `[[Verity]]`, `[[Datafund]]`
- Keywords: project names, product names
- File paths mentioned: `/1-datafund/`, `/2-datacore/`
- Default: Personal (0-personal) if no team signal

**Team Project Detection:**

| Project/Product | Keywords | Space |
|-----------------|----------|-------|
| Verity | verity, data marketplace, data RWA | datafund |
| Santorio | santorio, health data, longevity | datafund |
| Datacore | datacore, module, agent, GTD system | datacore |
| Fair Data Society | FDS, fair data, swarm | datafund |
| Platform | platform economics, tokenomics | datafund |

Detection rules:
1. Check for explicit wiki-links: `[[Verity]]`, `[[Santorio]]`
2. Check for product keywords (case-insensitive)
3. Check for related technical terms
4. Cross-reference with `team_space_mappings` setting

**Accomplishment Validation:**

Check accomplishment quality before including:

| Condition | Action |
|-----------|--------|
| <3 accomplishments found | Show confidence warning |
| All accomplishments generic | Suggest reviewing session work |
| No actionable tasks for today | Flag as incomplete |
| Weekend gap (Fri→Mon) | Look back to Friday, note gap |

Quality signals:
- Good: Specific outcomes ("Shipped X", "Completed Y review")
- Weak: Generic ("Worked on project", "Made progress")
- Bad: Activities without outcomes ("Spent time on X")

**Confidence Indicator:**

Add confidence level to output based on data quality:

| Confidence | Criteria | Display |
|------------|----------|---------|
| HIGH | 4+ accomplishments, today's tasks scheduled, journal fresh | ✓ |
| MEDIUM | 2-3 accomplishments OR tasks from fallback source | ⚡ |
| LOW | <2 accomplishments OR stale journal (>2 days) | ⚠️ |

Example output with low confidence:
```
⚠️ Data confidence: LOW
   - Yesterday's journal was sparse (1 item found)
   - Consider reviewing session work sections
```

### Step 2: Get Today's Plan

**Source 1: Today's journal (if `/today` already ran)**
- Read today's journal `## Daily Briefing` section
- Extract tasks under `### Priority Tasks`

**Source 2: Fallback to org files**
- Read `0-personal/org/next_actions.org`
- Find SCHEDULED items for today: `SCHEDULED: <YYYY-MM-DD>`
- Find DEADLINE items for today
- Sort by priority (A > B > C)
- Limit to top 5 items

### Step 3: Identify Blockers

**Query `next_actions.org` for:**
- Tasks with `WAITING` state
- Tasks with `:blocked:` tag
- Filter by age > `blockers_threshold_days` setting (default: 3)

**Extract blocker context:**
- Task title
- Since date (from SCHEDULED or :CREATED: property)
- Waiting reason (if `:WAITING_REASON:` property exists)

### Step 4: Determine Audience Context

Before generating, determine the **audience** from the triggering context:

| Trigger | Audience | Scope |
|---------|----------|-------|
| `/standup` (manual) | Personal | All items |
| `/today` hook (Daily meeting) | Team | Team-relevant only |
| `/standup --team datafund` | Team | Datafund space only |

**Team detection:**
- Parse calendar.org meeting for attendees
- If meeting has external participants → Team audience
- If "Daily" or "Weekly" in meeting name → Team audience

### Step 4b: Apply Meeting Type Preset

Different meeting types have different content requirements:

| Meeting Type | Filter Level | Focus | Blockers | Format |
|--------------|--------------|-------|----------|--------|
| `daily` | Team | Operational progress | Team-actionable | Brief |
| `weekly` | Team | Strategic progress | All team blockers | Full |
| `investor` | External | Milestones, metrics | Critical only | Polished |
| `product` | Product team | Feature progress | Technical blockers | Technical |

**Daily Standup Preset:**
- Focus: What shipped, what's in progress
- Exclude: Research, reading, internal process
- Blockers: Only if team can help today
- Length: 3-5 items max (30-second delivery)

**Weekly Standup Preset:**
- Focus: Week's achievements, next week's goals
- Include: Strategic progress, key decisions made
- Blockers: All team blockers, escalations
- Length: 5-7 items (2-minute delivery)

**Investor Update Preset:**
- Focus: Milestones hit, metrics, runway
- Exclude: Internal operations, technical details
- Blockers: Only funding-related or critical path
- Tone: Professional, outcome-focused
- Length: 3-5 high-impact items

**Product Meeting Preset:**
- Focus: Feature completion, sprint progress
- Include: Technical decisions, architecture changes
- Blockers: Technical dependencies, resource needs
- Audience: Product team (Verity, Santorio, etc.)

### Step 5: Apply Content Filters

**A. Relevance Filter (Team Audience)**

Include only items that:
- Relate to shared projects/products
- Affect team members' work
- Are in team space (1-datafund, etc.)
- Relate to infrastructure (datacore modules) that affects team

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
| "Found N issues" | Implies problems | Rephrase to "Identified improvement areas" or omit |
| "Backlog of N items" | Implies falling behind | Omit unless asking for help |
| Overdue counts | Creates pressure | Omit from team standup |

**D. Blocker Relevance Filter (Team Audience)**

Include blockers only if:
- Team can help unblock
- Blocks shared project work
- Requires team awareness

Exclude personal blockers:
- Personal finance (BVI, banking)
- Family scheduling
- Personal admin tasks

### Step 6: Generate Standup

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

### Step 7: Post to Journal (unless --no-post)

1. If today's journal exists and has `## Standup` section, replace it
2. If no `## Standup` section, append after `## Daily Briefing`
3. If no `## Daily Briefing`, append at end of file

## Output Examples

### Team Standup (Daily meeting with Crt, Tadej)

```
STANDUP GENERATED (Team: Datafund)
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

### Personal Standup (full detail)

```
STANDUP GENERATED (Personal)
----------------------------

Yesterday:
- Processed 213 emails across 2 accounts (inbox zero)
- Released mail module v1.1.0
- Completed DSAlliance competitive analysis
- Created 22 research/action tasks from email triage

Today:
- [ ] Review POC_SPRINT_PLAN_PROPOSAL.md
- [ ] Sprint planning meeting (10:00)
- [ ] Comms Weekly (14:00)
- [ ] Follow up on BKS token claim

Blockers:
- WAITING: ERC-3643 evaluation (since Dec 3)
- WAITING: BVI issues - follow-up Dec 23
- WAITING: e-racuni API credentials

[Posted to journal: 0-personal/notes/journals/2025-12-18.md]
```

**Note the differences:**
- Team version omits personal finance (BVI, BKS tokens)
- Team version omits process metrics ("22 tasks created")
- Team version frames outcomes ("Shipped mail module") not activities
- Team version includes only blockers team can help with

### Chat Export Format (--format chat)

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

**Chat format rules:**
- Use bullet points (•) instead of markdown lists
- Bold headers with asterisks for Slack compatibility
- Single line per item (no multi-line)
- Blockers condensed to one line if possible
- Emoji prefix for visual scanning
- Max 280 chars for Discord-friendly length (optional truncation)

**Platform-specific variants:**
- `--format chat:slack` - Slack mrkdwn formatting
- `--format chat:discord` - Discord markdown
- `--format chat:teams` - Microsoft Teams adaptive cards (future)

### Historical Comparison (Future)

Compare current standup with previous periods:

**Week-over-week patterns:**
```
📊 Pattern detected: Similar focus to last Tuesday
   - 3/5 items relate to investor preparation
   - Shipping velocity: 2 items (vs 3 avg)
```

**Streak tracking:**
- "5-day shipping streak" (at least 1 shipped item/day)
- "Blocker aging: ERC-3643 now 16 days old (was 9 last week)"

**Anomaly detection:**
- Unusually light standup (vs personal baseline)
- Unusual topic mix (mostly personal in team standup)
- Missing expected recurring items

*Note: Historical comparison requires 2+ weeks of standup data. Implementation planned for Phase 3.*

## Error Handling

| Error | Response |
|-------|----------|
| Yesterday's journal not found | Look back up to 3 days for last journal |
| No accomplishments found | Include: "(no logged accomplishments)" |
| No scheduled tasks | Include: "Review priorities in next_actions.org" |
| No blockers | Omit Blockers section entirely |

## Your Boundaries

**YOU CAN:**
- Read journal files in `notes/journals/`
- Read org files in `org/`
- Read calendar.org for meeting context
- Write to today's journal file

**YOU CANNOT:**
- Modify org files (tasks, priorities)
- Delete existing journal content
- Access external calendar APIs

**YOU MUST:**
- Preserve existing journal content when appending
- Use wiki-links `[[YYYY-MM-DD]]` for date references
- Format output for both terminal and markdown readability
