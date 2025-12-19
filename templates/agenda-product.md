## {{PRODUCT}} Product Call - {{DATE}}

**Time:** {{TIME}} | **Duration:** 60 min
**Attendees:** {{ATTENDEES}}
**GitHub Repo:** {{REPO}}

---

{{#if ISSUES}}
### GitHub Issues to Discuss

{{#each ISSUES}}
- [ ] [#{{number}}]({{url}}) **{{title}}**
  - Labels: {{labels}}
  - Assignee: {{assignee}}
  {{#if priority}}- Priority: {{priority}}{{/if}}
{{/each}}
{{/if}}

{{#if PRS}}
### PRs Needing Review

{{#each PRS}}
- [ ] [#{{number}}]({{url}}) {{title}}
  - Author: @{{author}}
  - Status: {{status}}
  - Changed files: {{files_changed}}
{{/each}}
{{/if}}

{{#if TECH_QUESTIONS}}
### Technical Questions

{{#each TECH_QUESTIONS}}
- [ ] **{{title}}**
  {{#if context}}- Context: {{context}}{{/if}}
  {{#if research}}
  - AI Research: {{research.summary}}
  - Sources: {{research.sources}}
  {{/if}}
  {{#if stakeholders}}- Needs input from: {{stakeholders}}{{/if}}
{{/each}}
{{/if}}

{{#if ARCHITECTURE}}
### Architecture Decisions

{{#each ARCHITECTURE}}
- [ ] **{{title}}**
  {{#if description}}- {{description}}{{/if}}
  {{#if options}}
  - Options:
    {{#each options}}
    - {{name}}: {{description}}
    {{/each}}
  {{/if}}
  {{#if recommendation}}- Recommendation: {{recommendation}}{{/if}}
{{/each}}
{{/if}}

{{#if SPRINT}}
### Sprint Status

**Sprint:** {{SPRINT.name}} ({{SPRINT.start}} - {{SPRINT.end}})
**Progress:** {{SPRINT.completed}}/{{SPRINT.total}} items ({{SPRINT.percentage}}%)

{{#if SPRINT.at_risk}}
**At Risk:**
{{#each SPRINT.at_risk}}
- {{title}} - {{reason}}
{{/each}}
{{/if}}
{{/if}}

{{#if BLOCKED}}
### Blocked Items

{{#each BLOCKED}}
- **{{title}}**
  - Blocked by: {{blocker}}
  - Since: {{since}}
  - Needed: {{action_needed}}
{{/each}}
{{/if}}

---

### Decisions Made (capture during meeting)

| Decision | Owner | Deadline |
|----------|-------|----------|
| | | |

### Action Items

- [ ]

---

**Next {{PRODUCT}} Call:** {{NEXT_DATE}}
