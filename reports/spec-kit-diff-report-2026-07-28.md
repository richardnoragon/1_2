# Spec Kit Upgrade Diff Report (2026-07-28)

Scope: Spec Kit-related paths only.

Included path filters:
- `.specify/**`
- `RFU/.specify/**`
- `.github/skills/**`
- `RFU/.github/skills/**`
- `.github/prompts/**`
- `RFU/.github/prompts/**`
- `.github/agents/**`
- `RFU/.github/agents/**`
- `.vscode/settings.json`

## 1) Skills-Mode Switch Verification

Both roots are now in Copilot skills mode with healthy integration state:
- Root: `C:/Users/HP1/1_2` -> `specify integration status: OK`
- Nested root: `C:/Users/HP1/1_2/RFU` -> `specify integration status: OK`

Command availability confirmed through installed skills in both roots:
- `speckit-analyze`
- `speckit-checklist`
- `speckit-clarify`
- `speckit-constitution`
- `speckit-converge`
- `speckit-implement`
- `speckit-plan`
- `speckit-specify`
- `speckit-tasks`
- `speckit-taskstoissues`

## 2) Compact Change Summary (Spec Kit Only)

- Modified: 15
- Deleted: 8
- Added (untracked/new): 15
- Total changed entries: 38

Tracked diffstat (tracked files only):
- 23 files changed
- 2154 insertions
- 2108 deletions

## 3) Modified (M)

- `.specify/scripts/powershell/check-prerequisites.ps1`
- `.specify/scripts/powershell/common.ps1`
- `.specify/scripts/powershell/create-new-feature.ps1`
- `.specify/scripts/powershell/setup-plan.ps1`
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/tasks-template.md`
- `RFU/.specify/scripts/powershell/check-prerequisites.ps1`
- `RFU/.specify/scripts/powershell/common.ps1`
- `RFU/.specify/scripts/powershell/create-new-feature.ps1`
- `RFU/.specify/scripts/powershell/setup-plan.ps1`
- `RFU/.specify/templates/checklist-template.md`
- `RFU/.specify/templates/plan-template.md`
- `RFU/.specify/templates/spec-template.md`
- `RFU/.specify/templates/tasks-template.md`

## 4) Deleted (D)

- `RFU/.github/prompts/speckit.analyze.prompt.md`
- `RFU/.github/prompts/speckit.checklist.prompt.md`
- `RFU/.github/prompts/speckit.clarify.prompt.md`
- `RFU/.github/prompts/speckit.constitution.prompt.md`
- `RFU/.github/prompts/speckit.implement.prompt.md`
- `RFU/.github/prompts/speckit.plan.prompt.md`
- `RFU/.github/prompts/speckit.specify.prompt.md`
- `RFU/.github/prompts/speckit.tasks.prompt.md`

## 5) Added (Untracked/New)

Root:
- `.github/skills/speckit-analyze/SKILL.md`
- `.github/skills/speckit-checklist/SKILL.md`
- `.github/skills/speckit-clarify/SKILL.md`
- `.github/skills/speckit-constitution/SKILL.md`
- `.github/skills/speckit-converge/SKILL.md`
- `.github/skills/speckit-implement/SKILL.md`
- `.github/skills/speckit-plan/SKILL.md`
- `.github/skills/speckit-specify/SKILL.md`
- `.github/skills/speckit-tasks/SKILL.md`
- `.github/skills/speckit-taskstoissues/SKILL.md`
- `.specify/init-options.json`
- `.specify/integration.json`
- `.specify/integrations/copilot.manifest.json`
- `.specify/integrations/speckit.manifest.json`
- `.specify/scripts/powershell/setup-tasks.ps1`
- `.specify/templates/checklist-template.md`
- `.specify/templates/constitution-template.md`
- `.specify/workflows/speckit/workflow.yml`
- `.specify/workflows/workflow-registry.json`

RFU:
- `RFU/.github/skills/speckit-analyze/SKILL.md`
- `RFU/.github/skills/speckit-checklist/SKILL.md`
- `RFU/.github/skills/speckit-clarify/SKILL.md`
- `RFU/.github/skills/speckit-constitution/SKILL.md`
- `RFU/.github/skills/speckit-converge/SKILL.md`
- `RFU/.github/skills/speckit-implement/SKILL.md`
- `RFU/.github/skills/speckit-plan/SKILL.md`
- `RFU/.github/skills/speckit-specify/SKILL.md`
- `RFU/.github/skills/speckit-tasks/SKILL.md`
- `RFU/.github/skills/speckit-taskstoissues/SKILL.md`
- `RFU/.specify/init-options.json`
- `RFU/.specify/integration.json`
- `RFU/.specify/integrations/copilot.manifest.json`
- `RFU/.specify/integrations/speckit.manifest.json`
- `RFU/.specify/scripts/powershell/setup-tasks.ps1`
- `RFU/.specify/templates/constitution-template.md`
- `RFU/.specify/workflows/speckit/workflow.yml`
- `RFU/.specify/workflows/workflow-registry.json`

Notes:
- Added list includes all currently untracked Spec Kit files from both roots.
- Status counts reflect path-filtered git status output only (Spec Kit scope).
