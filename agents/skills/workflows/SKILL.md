# ⚙️ SKILL: Workflow Architect

> **System Skill for the Agent**: Teaches the agent how to generate new automation workflows.

## 🎯 Purpose
When the operator asks you to "create a new workflow for X" or "automate this procedure," you will use this skill to write a structured `.md` procedure file in the `agents/workflows/` directory.

## 🧠 Trigger Phrases
- "Create a new workflow"
- "Write a workflow for..."
- "Add a new procedure"

## 📋 The Generation Process

When instructed to create a workflow, you must dynamically write a markdown file that acts as a blueprint for your future self. 

Follow these exact steps:

1. **Determine the Name**: Choose a short, uppercase name for the workflow (e.g., `MORNING-ROUTINE`, `SERVER-AUDIT`).
2. **Create the File**: Use your filesystem tools to write a new file precisely at `agents/workflows/<NAME>/WORKFLOW.md`.
3. **Draft the Blueprint**: The generated `WORKFLOW.md` MUST follow this exact structure:

```markdown
# [Icon] WORKFLOW: [Name]

> Brief description of what this workflow accomplishes.

## 🧠 Trigger Phrases
- "Trigger phrase 1"
- "Trigger phrase 2"

## 📋 The Autonomous Workflow
When the operator triggers this workflow, execute the following steps exactly as written:

### Phase 1: [Phase Name]
1. [Action step using specific CLI tool]
2. [Action step]

### Phase 2: [Phase Name]
1. [Action step]

## 🛡️ Critical Guidelines
- List any constraints, things NOT to do, or safety checks required.
```

4. **Verify**: Ensure the file was saved correctly.
5. **Inform the Operator**: Let the operator know the workflow has been registered. The Python backend will automatically discover the new `WORKFLOW.md` file and inject it into your context on the next message cycle.
