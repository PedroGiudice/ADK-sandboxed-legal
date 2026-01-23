# Session Handover - ADK Sandboxed Legal
**Date:** Friday, January 23, 2026
**Origin:** Migration from `Picture-composer` & `lex-vector` context.

## 1. Project Status
- **Repository:** `ADK-sandboxed-legal` (Cloned & Initialized)
- **Goal:** Create a new Tauri application for Legal Tech (Sandboxed).
- **Current Phase:** Tooling Setup & Migration Complete.

## 2. Tooling Inventory (Migrated)
The following resources have been injected into this repository:

### Tauri Ecosystem (`.claude/skills` & `~/.gemini/skills`)
- `tauri-core.md`: Architecture patterns.
- `tauri-frontend.md`: React/Vite/Tailwind guidelines.
- `tauri-native-apis.md`: Rust/OS integration.
- `skill-rules.json`: MCP Triggers for the CLI.

### Specialized Agents (`.claude/agents`)
- `tauri-frontend-dev`: UI Specialist.
- `tauri-rust-dev`: Backend Specialist.
- `tauri-reviewer`: Security/QA.

### ADK Research Agents (`adk-agents/`)
- `deep_research_sandbox`: Gemini 2.0 Deep Research.
- `jurisprudence_agent`: Legal scrapers (STJ, TJSP).
- `visual_verifier`: UI integrity checker.
- `iterative_research_agent.py`: Loop-based researcher.

## 3. Next Steps
1. **Initialize Project:** Run scaffolding (npm/cargo).
2. **Architecture Definition:** Define the specific legal use case.
3. **Integration:** Connect ADK agents to the Tauri backend.

## 4. MCP Configuration Check
- `skill-rules.json`: **Present**. Defines when to load skills.
- **Action Required:** Verify `.env` variables if agents require specific API keys (Google GenAI, etc).
