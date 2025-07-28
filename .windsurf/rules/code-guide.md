---
trigger: always_on
---

Whenver I prompt you, include all docs in @.kiro/steering for implementation.  

If a spec is mentioned, search the @.kiro/specs folder for a related task. 

If no spec is matched, create one. Each spec requires a `requirements.md`, `design.md`, and then `tasks.md`, in that order. See other specs for implementation details.
Create proper subtasks with requirements. Once finished, the user will ask to go through the task list with you, and iplement it with them.

Once a sub-task is completed, mark it done with an `x`. Each task (and sub-task) has a symbol at the beginning, looking like `[ ]`. Make it `[x]`. Once all sub-tasks are completed, mark the parent task done as well, with an `[x]` as well.

Use all availble MCP servers you have access to, including, but not limited to: Context7, Fetch, & Sequential Thinking.