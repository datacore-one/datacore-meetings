## Standup - {{DATE}}

### Yesterday
{{#each ACCOMPLISHMENTS}}
- {{this}}
{{/each}}
{{#unless ACCOMPLISHMENTS}}
- (no logged accomplishments)
{{/unless}}

### Today
{{#each TASKS}}
- [ ] {{this}}
{{/each}}
{{#unless TASKS}}
- Review priorities in next_actions.org
{{/unless}}

{{#if BLOCKERS}}
### Blockers
{{#each BLOCKERS}}
- WAITING: {{description}} (since {{since}})
{{/each}}
{{/if}}
