# /my-questions

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Checking what questions need your input
- Reviewing which questions are ready for discussion
- Triggering research on unresearched questions
- Understanding question preparation status across projects

**Key decisions the module informs:**
- Which questions need your response before meetings
- What factual questions could benefit from AI research
- Which questions are ready vs need preparation
- How questions map to upcoming meetings

### Quick Reference

| Question | Answer |
|----------|--------|
| When to run? | Before meeting prep, or when checking question status |
| What does it show? | Open GitHub Issues with question label, grouped by status |
| Can it trigger research? | Yes, with --research flag |
| What filters are available? | By project, by meeting type, by your involvement |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| question-researcher | Research unresearched questions (with --research flag) |

### Integration Points

- **GitHub Issues** - Primary data source (question label)
- **/meeting-prep** - Questions feed into preparation workflow
- **/meeting-agenda** - Questions appear in generated agendas
- **/today** - Shows count of questions needing input

---

View open questions requiring your input before meetings.

## Workflow

### Step 1: Understand Intent

If invoked as just `/my-questions` with no filters, ask:

"What would you like to see?"

1. **All questions** - Everything across projects
2. **Specific project** - Just Verity, Datafund, etc.
3. **For a meeting** - Questions tagged for daily/weekly/product
4. **Needing my input** - Where I'm blocking progress

If context is clear (e.g., "questions for weekly"), proceed directly.

### Step 2: Gather Context

**Ask if not provided:**
- "Which project?" (if multiple exist)
- "Should I research unresearched questions?" (triggers AI)

**Auto-detect:**
- Your GitHub username for "needs your input" filtering
- Upcoming meetings for deadline context

### Step 3: Query GitHub Issues

```bash
gh issue list --label question --state open --json number,title,body,labels,assignees,url
```

For specific project:
```bash
gh issue list --repo datacore-one/{project} --label question --state open
```

### Step 4: Parse Question Data

For each issue, extract:
- **Title**: Issue title
- **Number**: Issue number for linking
- **Stakeholders**: Assignees + @mentions in body
- **Target meeting**: From `meeting:daily` or `meeting:weekly` label
- **Research status**: Check for `## AI Research` section in body
- **Your involvement**: Check if current user is mentioned/assigned

### Step 5: Classify by Status

Group questions into:

**Ready for Discussion:**
- Has `## AI Research` section OR `researched` label
- Stakeholders identified
- Not waiting for input

**Needs Your Input:**
- You are assigned or mentioned
- No response from you yet
- May have deadline

**Needs Research:**
- No `researched` label
- Factual question that could benefit from AI research

**Recently Resolved:**
- Closed in last 7 days
- Show decision for context

### Step 6: Apply Filters

If meeting specified:
- `daily` → only `meeting:daily` labeled
- `weekly` → only `meeting:weekly` labeled OR unlabeled
- `product` → filter by product repo

### Step 7: Generate Output

Use `templates/questions-prep.md` template with grouped questions.

### Step 8: Follow-up

After showing questions, offer next steps:

"Here are your open questions. Would you like to:"
- "Trigger AI research on unresearched questions?" → Run with research flag
- "Prepare for a specific meeting?" → `/meeting-prep`
- "Generate meeting agenda?" → `/meeting-agenda`

## Output Example

```
OPEN QUESTIONS - Verity
=======================

Ready for Discussion (2)
------------------------
1. [#42] Database selection for production
   - Stakeholders: @tadej, @gregor
   - AI Research: PostgreSQL recommended (85% confidence)
   - Target: Weekly Exec

2. [#38] API rate limiting approach
   - Stakeholders: @crt
   - AI Research: Token bucket algorithm suggested
   - Target: Product Call

Needs Your Input (1)
--------------------
1. [#45] Pricing tier structure
   - Waiting for: Your input on enterprise tier
   - Requested: Dec 15
   - Deadline: Before investor meeting (Dec 22)

Needs Research (1)
------------------
1. [#47] OAuth provider selection
   - Type: Technical comparison
   - Run with --research to trigger AI research

Recently Resolved (1)
---------------------
1. [#40] Frontend framework choice (Resolved Dec 17)
   - Decision: Next.js with App Router
```

## Integration

### With /today

If questions need your input before a meeting today:
```
Meeting Prep Needed
   2 questions need your input before Weekly Exec (14:00)
   Run: /my-questions --meeting weekly
```

### With /meeting-prep

Questions feed into meeting preparation:
- Ready for discussion → agenda items
- Needs your input → preparation reminders

## Error Handling

| Error | Response |
|-------|----------|
| GitHub API unavailable | Show cached questions if available, note stale data |
| No questions found | "No open questions for {project}" - offer to check other projects |
| Project not found | List available projects and ask which one |
| Not authenticated | Prompt to run `gh auth login` |

## Configuration

Settings in `settings.local.yaml`:

```yaml
meetings:
  questions:
    github_label: "question"
    auto_research: true
  github_repos:
    verity: "datacore-one/verity"
    datafund: "datacore-one/datafund-space"
```

## Your Boundaries

**YOU CAN:**
- Query GitHub Issues via `gh` CLI
- Read issue bodies and comments
- Filter by labels and assignees
- Trigger research with flag

**YOU CANNOT:**
- Create or modify issues directly
- Access private repos without auth
- Make decisions on questions

**YOU MUST:**
- Show all questions the user is involved in
- Highlight deadline-sensitive items
- Link to GitHub issues for full context
- Offer follow-up options after showing questions
