// Meetings Module — MCP Tool Definitions
// Generates standups from journal entries and lists upcoming meetings.
// Plain JS (ESM) for direct dynamic import by the MCP server.

import { z } from 'zod'
import * as fs from 'fs'
import * as path from 'path'

// --- Helpers ---

function getRecentJournals(basePath, days = 3) {
  const journals = []
  const now = new Date()

  try {
    for (const entry of fs.readdirSync(basePath)) {
      if (!/^\d+-/.test(entry)) continue
      const journalDir = path.join(basePath, entry, 'journal')
      if (!fs.existsSync(journalDir)) continue

      for (const jf of fs.readdirSync(journalDir).sort().reverse()) {
        if (!jf.endsWith('.md')) continue
        const dateStr = jf.replace('.md', '')
        const diffDays = (now - new Date(dateStr)) / (1000 * 60 * 60 * 24)
        if (diffDays > days) break

        journals.push({
          space: entry,
          date: dateStr,
          path: path.join(journalDir, jf),
          content: fs.readFileSync(path.join(journalDir, jf), 'utf-8'),
        })
      }
    }
  } catch { /* ignore */ }

  return journals.sort((a, b) => b.date.localeCompare(a.date))
}

function extractAccomplishments(content) {
  const items = []
  const lines = content.split('\n')

  for (let i = 0; i < lines.length; i++) {
    // Look for bullet points under accomplishment-like headings
    if (/^#{1,3}\s*(Accomplishments|Completed|Done|Session Work|Progress)/i.test(lines[i])) {
      for (let j = i + 1; j < lines.length; j++) {
        if (/^#{1,3}\s/.test(lines[j])) break
        const bullet = lines[j].match(/^[-*]\s+(.+)/)
        if (bullet) items.push(bullet[1].trim())
      }
    }
  }
  return items
}

function extractBlockers(basePath) {
  const blockers = []
  try {
    for (const entry of fs.readdirSync(basePath)) {
      if (!/^\d+-/.test(entry)) continue
      const orgPath = path.join(basePath, entry, 'org', 'next_actions.org')
      if (!fs.existsSync(orgPath)) continue

      const content = fs.readFileSync(orgPath, 'utf-8')
      for (const line of content.split('\n')) {
        const m = line.match(/^\*+\s+WAITING\s+(.+?)(\s+:[:\w]+:)?\s*$/)
        if (m) {
          blockers.push({
            title: m[1].trim(),
            tags: (m[2] || '').trim(),
            space: entry,
          })
        }
      }
    }
  } catch { /* ignore */ }
  return blockers
}

// --- Tools ---

export const tools = [
  {
    name: 'standup',
    description: 'Generate standup summary from recent journal entries and blockers',
    inputSchema: z.object({
      days: z.number().optional().describe('Lookback period in days (default: 2)'),
      space: z.string().optional().describe('Filter by space'),
      team_mode: z.boolean().optional().describe('Filter personal items for team standup (default: true)'),
    }),
    handler: async (args, ctx) => {
      const days = args.days || 2
      let journals = getRecentJournals(ctx.storage.basePath, days)

      if (args.space) {
        journals = journals.filter(j => j.space === args.space)
      }

      const accomplishments = []
      for (const j of journals) {
        const items = extractAccomplishments(j.content)
        for (const item of items) {
          accomplishments.push({ text: item, date: j.date, space: j.space })
        }
      }

      const blockers = extractBlockers(ctx.storage.basePath)

      return {
        period_days: days,
        journals_found: journals.length,
        accomplishments: accomplishments.slice(0, 20),
        blockers: blockers.slice(0, 10),
        generated_at: new Date().toISOString(),
      }
    },
  },

  {
    name: 'upcoming',
    description: 'List upcoming meetings from calendar.org with prep status',
    inputSchema: z.object({
      days: z.number().optional().describe('Lookahead period in days (default: 7)'),
    }),
    handler: async (args, ctx) => {
      const days = args.days || 7
      const meetings = []

      // Check calendar.org files across spaces
      try {
        for (const entry of fs.readdirSync(ctx.storage.basePath)) {
          if (!/^\d+-/.test(entry)) continue
          const calPath = path.join(ctx.storage.basePath, entry, 'org', 'calendar.org')
          if (!fs.existsSync(calPath)) continue

          const content = fs.readFileSync(calPath, 'utf-8')
          const lines = content.split('\n')

          for (let i = 0; i < lines.length; i++) {
            const m = lines[i].match(/^\*+\s+(TODO|NEXT)?\s*(.+?)(\s+:[:\w]+:)?\s*$/)
            if (!m) continue

            // Check for timestamp on next lines
            for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
              const ts = lines[j].match(/<(\d{4}-\d{2}-\d{2})\s+\w+(\s+\d{2}:\d{2}(-\d{2}:\d{2})?)?>/)
              if (ts) {
                const meetDate = new Date(ts[1])
                const now = new Date()
                const diffDays = (meetDate - now) / (1000 * 60 * 60 * 24)
                if (diffDays >= 0 && diffDays <= days) {
                  meetings.push({
                    title: m[2].trim(),
                    date: ts[1],
                    time: ts[2]?.trim() || null,
                    tags: (m[3] || '').trim(),
                    space: entry,
                  })
                }
                break
              }
            }
          }
        }
      } catch { /* ignore */ }

      return {
        days_ahead: days,
        count: meetings.length,
        meetings: meetings.sort((a, b) => a.date.localeCompare(b.date)),
      }
    },
  },
]
