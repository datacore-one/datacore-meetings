## Weekly Exec - {{DATE}}

**Time:** {{TIME}} | **Duration:** 45 min
**Attendees:** {{ATTENDEES}}

---

### Standing Items

- [ ] Review last week's decisions
- [ ] Key metrics review
- [ ] Escalated items from dailies

{{#if ESCALATED}}
### Escalated from Daily

Items that appeared 3+ times in daily standups:

{{#each ESCALATED}}
- [ ] **{{title}}**
  - Appearances: {{count}}x (since {{first_date}})
  - Last discussed: {{last_date}}
  {{#if context}}- Context: {{context}}{{/if}}
{{/each}}
{{/if}}

{{#if QUESTIONS}}
### Open Questions

{{#each QUESTIONS}}
- [ ] **{{title}}**
  - Status: {{status}}
  - Stakeholders: {{stakeholders}}
  {{#if research}}
  - AI Research: {{research.summary}}
  - Confidence: {{research.confidence}}
  {{/if}}
  {{#if recommendation}}- Recommendation: {{recommendation}}{{/if}}
{{/each}}
{{/if}}

{{#if TASK_DECISIONS}}
### Decisions Needed (from Tasks)

Items tagged :decision: or needing team input:

{{#each TASK_DECISIONS}}
- [ ] **{{title}}** {{#if priority}}[#{{priority}}]{{/if}}
  {{#if context}}- Context: {{context}}{{/if}}
  {{#if deadline}}- Deadline: {{deadline}}{{/if}}
  {{#if stakeholders}}- Stakeholders: {{stakeholders}}{{/if}}
{{/each}}
{{/if}}

{{#if TASK_DISCUSSIONS}}
### Discussion Items (from Tasks)

Items tagged :discuss: or :@team::

{{#each TASK_DISCUSSIONS}}
- [ ] **{{title}}**
  {{#if tags}}- Tags: {{tags}}{{/if}}
  {{#if background}}- Background: {{background}}{{/if}}
{{/each}}
{{/if}}

{{#if BLOCKING_OTHERS}}
### Blocking Team Members

Your tasks blocking others' work:

{{#each BLOCKING_OTHERS}}
- [ ] **{{title}}** - blocking @{{blocking}}
  - Since: {{since}}
  - Action needed: {{action}}
{{/each}}
{{/if}}

{{#if STRATEGIC}}
### Strategic Items

{{#each STRATEGIC}}
- [ ] {{title}}
  {{#if owner}}- Owner: {{owner}}{{/if}}
  {{#if deadline}}- Deadline: {{deadline}}{{/if}}
{{/each}}
{{/if}}

{{#if DECISIONS}}
### Other Decisions Needed

{{#each DECISIONS}}
- [ ] **{{title}}**
  {{#if options}}
  - Options:
    {{#each options}}
    - {{this}}
    {{/each}}
  {{/if}}
  {{#if stakeholders}}- Decision makers: {{stakeholders}}{{/if}}
{{/each}}
{{/if}}

{{#if METRICS}}
### Key Metrics

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
{{#each METRICS}}
| {{name}} | {{current}} | {{previous}} | {{trend}} |
{{/each}}
{{/if}}

---

### Action Items (capture during meeting)

- [ ]

---

**Next Weekly:** {{NEXT_DATE}}
