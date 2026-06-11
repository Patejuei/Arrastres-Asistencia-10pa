# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| When creating a pull request, opening a PR, or preparing changes for review | branch-pr | C:\Users\seret\.gemini\config\skills\branch-pr\SKILL.md |
| When writing Go tests, using teatest, or adding test coverage | go-testing | C:\Users\seret\.gemini\config\skills\go-testing\SKILL.md |
| When creating a GitHub issue, reporting a bug, or requesting a feature | issue-creation | C:\Users\seret\.gemini\config\skills\issue-creation\SKILL.md |
| When user says "judgment day", "judgment-day", "review adversarial", "dual review", "doble review", "juzgar", "que lo juzguen" | judgment-day | C:\Users\seret\.gemini\config\skills\judgment-day\SKILL.md |
| When user asks to create a new skill, add agent instructions, or document patterns for AI | skill-creator | C:\Users\seret\.gemini\config\skills\skill-creator\SKILL.md |

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### branch-pr
- Follow issue-first enforcement system.
- Always verify an issue exists before creating a PR.
- Use standard branch naming (e.g., `issue-{number}-description`).

### go-testing
- Use standard Go testing package patterns.
- For Bubbletea TUI, use teatest.
- Mock network and external calls.

### issue-creation
- Always create a descriptive issue before implementing.
- Use the issue-creation template.
- Document acceptance criteria.

### judgment-day
- Run two independent judge sub-agents.
- Review implementations against requirements and standards.
- Fail if either judge rejects.

### skill-creator
- Follow the agent skills specification.
- Write a clear SKILL.md.
- Register trigger criteria accurately.

## Project Conventions

| File | Path | Notes |
|------|------|-------|

Read the convention files listed above for project-specific patterns and rules. All referenced paths have been extracted — no need to read index files to discover more.
