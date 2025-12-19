## Open Questions - {{PROJECT}}

**Generated:** {{DATE}}
**Target Meeting:** {{MEETING}}

---

{{#if READY}}
### Ready for Discussion

Questions with research complete and stakeholders identified:

{{#each READY}}
#### {{title}}

- **Issue:** [#{{number}}]({{url}})
- **Stakeholders:** {{stakeholders}}
- **Target Meeting:** {{meeting}}
{{#if research}}
- **AI Research Summary:**
  {{research.summary}}
- **Recommendation:** {{research.recommendation}} ({{research.confidence}} confidence)
- **Sources:** {{research.sources}}
{{/if}}
{{#if context}}
- **Context:** {{context}}
{{/if}}

---
{{/each}}
{{/if}}

{{#if NEEDS_INPUT}}
### Needs More Input

Waiting for stakeholder response before discussion:

{{#each NEEDS_INPUT}}
- [ ] **{{title}}** [#{{number}}]({{url}})
  - Waiting for: {{waiting_for}}
  - Requested: {{requested_date}}
  {{#if deadline}}- Deadline: {{deadline}}{{/if}}
{{/each}}
{{/if}}

{{#if NEEDS_RESEARCH}}
### Needs Research

Questions that would benefit from AI research:

{{#each NEEDS_RESEARCH}}
- [ ] **{{title}}** [#{{number}}]({{url}})
  - Type: {{question_type}}
  {{#if suggested_research}}- Suggested research: {{suggested_research}}{{/if}}
{{/each}}
{{/if}}

{{#if RESOLVED}}
### Recently Resolved

Questions resolved in the last 7 days:

{{#each RESOLVED}}
- ~~{{title}}~~ [#{{number}}]({{url}})
  - Resolved: {{resolved_date}}
  - Decision: {{decision}}
{{/each}}
{{/if}}

---

### Your Preparation Checklist

{{#if MY_QUESTIONS}}
Questions requiring your input:

{{#each MY_QUESTIONS}}
- [ ] Review and prepare thoughts on: **{{title}}**
  {{#if deadline}}- Needed by: {{deadline}}{{/if}}
{{/each}}
{{else}}
No questions currently require your direct input.
{{/if}}

---

**Tip:** Add your thoughts as comments on the GitHub issues before the meeting.
