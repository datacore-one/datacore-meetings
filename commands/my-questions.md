# /my-questions

View open questions requiring your input before meetings.

## Usage

```
/my-questions [project] [--meeting TYPE] [--all]
```

## Options

| Option | Description |
|--------|-------------|
| `project` | Filter by project (e.g., `verity`, `datafund`) |
| `--meeting` | Filter by target meeting: `daily`, `weekly`, `product` |
| `--all` | Show all open questions across projects |
| `--research` | Trigger AI research on unresearched questions |

## Algorithm

### Step 1: Query GitHub Issues

```bash
gh issue list --label question --state open --json number,title,body,labels,assignees,url
```

For specific project:
```bash
gh issue list --repo datacore-one/{project} --label question --state open --json number,title,body,labels,assignees,url
```

### Step 2: Parse Question Data

For each issue, extract:
- **Title**: Issue title
- **Number**: Issue number for linking
- **Stakeholders**: Assignees + @mentions in body
- **Target meeting**: From `meeting:daily` or `meeting:weekly` label
- **Research status**: Check for `## AI Research` section in body
- **Your involvement**: Check if current user is mentioned/assigned

### Step 3: Classify by Status

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

### Step 4: Apply Filters

If `--meeting` specified:
- `daily` → only `meeting:daily` labeled
- `weekly` → only `meeting:weekly` labeled OR unlabeled (default to weekly)
- `product` → filter by product repo

### Step 5: Generate Output

Use `templates/questions-prep.md` template with grouped questions.

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
   - Run: /my-questions --research to trigger AI research

Recently Resolved (1)
---------------------
1. [#40] Frontend framework choice (Resolved Dec 17)
   - Decision: Next.js with App Router
```

## Integration

### With /meeting-prep

`/my-questions` output feeds into `/meeting-prep`:
- Questions ready for discussion → agenda items
- Questions needing input → preparation reminders

### With /today

If questions need your input before a meeting today:
```
⚠️ Meeting Prep Needed
   2 questions need your input before Weekly Exec (14:00)
   Run: /my-questions --meeting weekly
```

## Error Handling

| Error | Response |
|-------|----------|
| GitHub API unavailable | Show cached questions if available, note stale data |
| No questions found | "No open questions for {project}" |
| Project not found | List available projects |
| Not authenticated | Prompt to run `gh auth login` |

## Your Boundaries

**YOU CAN:**
- Query GitHub Issues via `gh` CLI
- Read issue bodies and comments
- Filter by labels and assignees

**YOU CANNOT:**
- Create or modify issues (use --research flag for that)
- Access private repos without auth
- Make decisions on questions

**YOU MUST:**
- Show all questions the user is involved in
- Highlight deadline-sensitive items
- Link to GitHub issues for full context
