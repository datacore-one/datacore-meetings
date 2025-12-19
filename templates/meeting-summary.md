## Meeting Summary - {{MEETING_TYPE}} - {{DATE}}

**Duration:** ~{{DURATION}} min (estimated from transcript)
**Participants:** {{SPEAKERS}}
**Source:** {{SOURCE_PATH}}

---

{{#if ACTIONS}}
### Action Items Created ({{ACTION_COUNT}})

{{#each ACTIONS}}
- [ ] **{{description}}** {{#if assignee}}(@{{assignee}}){{/if}}
  - Confidence: {{confidence_emoji}} ({{confidence}})
  {{#if deadline}}- Deadline: {{deadline}}{{/if}}
  - Source: "{{source_line}}"
{{/each}}
{{else}}
### Action Items

No action items extracted from this meeting.
{{/if}}

---

{{#if DECISIONS}}
### Decisions Captured ({{DECISION_COUNT}})

{{#each DECISIONS}}
- **{{description}}**
  - By: {{speaker}}
  {{#if context}}- Context: {{context}}{{/if}}
{{/each}}
{{else}}
### Decisions

No explicit decisions captured.
{{/if}}

---

{{#if RESOLVED_QUESTIONS}}
### Questions Resolved ({{RESOLVED_COUNT}})

{{#each RESOLVED_QUESTIONS}}
- [#{{issue_number}}]({{issue_url}}) {{title}}
  - Resolution: {{resolution}}
  - Status: {{#if closed}}Closed{{else}}Commented{{/if}}
{{/each}}
{{/if}}

{{#if DISCUSSED_QUESTIONS}}
### Questions Discussed ({{DISCUSSED_COUNT}})

{{#each DISCUSSED_QUESTIONS}}
- [#{{issue_number}}]({{issue_url}}) {{title}}
  - Discussion: {{summary}}
  - Status: Awaiting further input
{{/each}}
{{/if}}

---

{{#if NEW_QUESTIONS}}
### New Questions Raised ({{NEW_QUESTION_COUNT}})

{{#each NEW_QUESTIONS}}
- {{question}}
  - Raised by: {{speaker}}
  {{#if suggested_assignee}}- Suggested owner: @{{suggested_assignee}}{{/if}}
{{/each}}

Consider creating GitHub issues for these questions.
{{/if}}

---

{{#if ZETTELS}}
### Knowledge Extracted ({{ZETTEL_COUNT}})

{{#each ZETTELS}}
- [[{{filename}}]]
  - {{description}}
  - Tags: {{tags}}
{{/each}}

Created in: `0-personal/notes/2-knowledge/zettel/`
{{/if}}

{{#if INSIGHTS}}
### Key Insights

{{#each INSIGHTS}}
> "{{quote}}" - {{speaker}}

{{#if implication}}*{{implication}}*{{/if}}
{{/each}}
{{/if}}

---

{{#if JOURNAL_UPDATED}}
### Journal Updated

Added meeting summary section to `journals/{{JOURNAL_DATE}}.md`:
- Key clarifications: {{CLARIFICATION_COUNT}}
- Topics covered: {{TOPICS}}
{{#if PRIMARY_INSIGHT}}- Primary insight: "{{PRIMARY_INSIGHT}}"{{/if}}
{{/if}}

---

{{#if LOW_CONFIDENCE_ACTIONS}}
### Items Needing Review

**Low Confidence Action Items:**
These items were extracted but not auto-created due to low confidence.

{{#each LOW_CONFIDENCE_ACTIONS}}
- {{description}} (confidence: {{confidence}})
  - Source: "{{source_line}}"
  - Reason: {{reason}}
{{/each}}
{{/if}}

{{#if UNPROCESSED}}
### Could Not Process

{{#each UNPROCESSED}}
- {{item}}
  - Issue: {{issue}}
{{/each}}
{{/if}}

---

### Processing Stats

| Metric | Value |
|--------|-------|
| Total transcript lines | {{TOTAL_LINES}} |
| Actions extracted | {{ACTIONS_EXTRACTED}} |
| Actions created (above threshold) | {{ACTIONS_CREATED}} |
| Decisions captured | {{DECISION_COUNT}} |
| Questions matched | {{QUESTIONS_MATCHED}} |
| Questions resolved | {{RESOLVED_COUNT}} |
| Zettels created | {{ZETTEL_COUNT}} |
| Journal updated | {{#if JOURNAL_UPDATED}}Yes{{else}}No{{/if}} |

---

**Processed:** {{PROCESSED_AT}}
**Confidence threshold:** {{CONFIDENCE_THRESHOLD}}

{{#if DRY_RUN}}
---
**DRY RUN MODE**
No changes were made. Run without `--dry-run` to create tasks and update issues.
{{/if}}
