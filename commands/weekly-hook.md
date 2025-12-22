# Weekly Review Hook - Meetings Module

## Command Context

### When to Reference Meetings Module

**Always reference when:**
- Running /gtd-weekly-review
- Reviewing items escalated from daily meetings
- Checking status of open questions before weekly planning
- Assessing meeting preparation health for upcoming week

**Key decisions the module informs:**
- Which daily items need weekly attention (DAILY_COUNT >= 3)
- What open questions are ready vs need research
- How prepared the team is for next week's meetings
- When to reset escalation counters (items resolved)

### Quick Reference

| Question | Answer |
|----------|--------|
| When is this hook triggered? | During /gtd-weekly-review, after inbox processing |
| What does it surface? | Escalated items, open questions status, meeting prep health |
| Does it modify data? | Yes - can reset DAILY_COUNT for resolved items |
| Where is output added? | Weekly review report sections |

### Agents This Command Invokes

| Agent | Purpose |
|-------|---------|
| (None directly) | Hook queries data and formats output, no agent invocation |

### Integration Points

- **/gtd-weekly-review** - Primary integration point
- **next_actions.org** - Escalated items data source
- **GitHub Issues** - Open questions status
- **calendar.org** - Upcoming week's meetings
- **meeting-router** - Escalation logic and thresholds

---

This hook is invoked during `/gtd-weekly-review` to surface meeting-related items.

## Trigger

Called as part of the weekly review workflow.

## Actions

### 1. Escalated Items Summary

Query `next_actions.org` for items with `:DAILY_COUNT:` >= 3:

```
### Escalated from Daily Standups

Items appearing 3+ times without resolution:

| Item | Count | First Mentioned |
|------|-------|-----------------|
{{#each ESCALATED}}
| {{title}} | {{count}}x | {{first_date}} |
{{/each}}

{{#if ESCALATED}}
**Action:** Review in next Weekly Exec or resolve before.
{{else}}
No items escalated this week.
{{/if}}
```

### 2. Open Questions Status

Query GitHub for open questions:

```
### Open Questions Review

| Question | Status | Target Meeting |
|----------|--------|----------------|
{{#each QUESTIONS}}
| [#{{number}}] {{title}} | {{status}} | {{meeting}} |
{{/each}}

**Researched:** {{RESEARCHED_COUNT}}
**Needs Research:** {{NEEDS_RESEARCH_COUNT}}
**Waiting for Input:** {{WAITING_COUNT}}
```

### 3. Meeting Preparation Status

Check preparation for upcoming week's meetings:

```
### Next Week's Meetings

{{#each MEETINGS}}
- **{{name}}** ({{date}})
  - Open items: {{open_items}}
  - Prep status: {{prep_status}}
{{/each}}
```

### 4. Reset Daily Counts

For items that were discussed and resolved during weekly:
- Clear `:DAILY_COUNT:` property
- Add `:RESOLVED_IN:` property with meeting reference

## Output

Append to weekly review output with meeting health summary.
