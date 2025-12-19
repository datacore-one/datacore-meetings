## Daily Standup - {{DATE}}

**Time:** {{TIME}} | **Duration:** 15 min
**Attendees:** {{ATTENDEES}}

---

### Round Robin

{{#each ATTENDEES}}
- [ ] **{{name}}**: Yesterday / Today / Blockers
{{/each}}
{{#unless ATTENDEES}}
- [ ] Review individual standups
{{/unless}}

{{#if DISCUSSION_ITEMS}}
### Discussion Items

{{#each DISCUSSION_ITEMS}}
- {{title}}{{#if author}} (raised by {{author}}){{/if}}
{{/each}}
{{/if}}

{{#if ESCALATION_CANDIDATES}}
### Escalate to Weekly?

Items appearing 3+ times without resolution:

{{#each ESCALATION_CANDIDATES}}
- [ ] {{title}} ({{count}}x since {{first_date}})
{{/each}}
{{/if}}

{{#if BLOCKERS}}
### Active Blockers

{{#each BLOCKERS}}
- **{{title}}** - {{status}} (since {{since}})
{{/each}}
{{/if}}

---

**Next Daily:** {{NEXT_DATE}}
