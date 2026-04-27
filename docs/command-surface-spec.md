# Command Surface Harmonization Specification

**Constitutional reference**: §8  
**Version**: 1.37.0  
**Status**: Phase 2 active — per-tool command taxonomy mappings complete (TODO(COMMAND_TAXONOMY) resolved 2026-04-25)

---

## 1. Purpose

This document is the canonical specification for §8 — Command Surface
Harmonization. It defines how tools classify, name, and surface commands across
all interaction surfaces: toolbars, context menus, keyboard shortcuts, and
action menus.

---

## 2. Action Tiers (§8.2)

Every tool action MUST be assigned to exactly one tier:

| Tier | UI Component | Placement | Confirmation required? |
|------|-------------|-----------|------------------------|
| Primary | PrimaryButton | Bottom-right of dialog / left-most in toolbar | No |
| Secondary | SecondaryButton | Adjacent to Primary | No |
| Advanced | Menu item only | Not in main toolbar | No |
| Destructive | SecondaryButton + danger styling | Separated from Primary/Secondary | Yes — see §II.2 |

---

## 3. Command Taxonomy (§8.3)

> **TODO(COMMAND_TAXONOMY)**: Full per-tool action-to-verb mappings are a
> Phase 2 deliverable. This section provides the taxonomy definitions only.
> Per-tool mapping tables MUST be appended to this document when Phase 2
> implementation begins.

### 3.1 Canonical Verbs

| Verb | Use when the command… | Examples |
|------|----------------------|---------|
| **Inspect** | Performs a read-only analysis without modifying any state | Scan, Analyse, Preview, Check |
| **Transform** | Performs a reversible or lossless content modification | Convert, Resize, Rename, Reformat |
| **Export** | Outputs to a file, clipboard, or external format | Export…, Save As…, Copy to Clipboard |
| **Apply** | Commits a change, writes a result, or performs a side-effect operation | Apply Changes, Run, Execute, Sync |
| **Revert** | Undoes, restores, or rolls back to a previous state | Undo, Restore, Rollback |

### 3.2 Deviation Rule

Where none of the five verbs fits, tools MUST use an imperative verb consistent
with §7.4.1 and MUST note the deviation in the tool's implementation docs.

---

## 4. Toolbar Layout (§8.4)

```
[ Primary Action ] [ Secondary Action ]   ···   [ Destructive Action ]
        ↑                   ↑                           ↑
   PrimaryButton      SecondaryButton     Separated + SecondaryButton(danger)
   (§10.5)            (§10.6)             (§10.6 + danger styling)
```

- Advanced Actions MUST NOT appear in the main toolbar.
- Advanced Actions MUST appear in a menu or overflow panel.
- Destructive Actions MUST be visually separated (separator or spacing) from
  the Primary and Secondary groups.

---

## 5. Keyboard Shortcut Rules (§8.5)

- Each Primary Action MUST have a keyboard shortcut where technically feasible.
- Shortcuts MUST NOT conflict with reserved global accelerators (§7.5).
- All shortcuts MUST be registered through the Hub Menu Registry (§9.4).
- Conflict detection is performed at registration time per §9.4.3.

### 5.1 Recommended Shortcut Assignments

| Action verb | Suggested shortcut | Notes |
|------------|-------------------|-------|
| Apply / Run | Ctrl+Return | Where not overridden by global shortcuts |
| Export | Ctrl+E | |
| Inspect / Scan | Ctrl+Shift+I | |
| Revert / Undo | Ctrl+Z | Reserved globally (§7.4.4) |

---

## 6. String Token Requirement (§8.6)

All command labels MUST use `ui_strings` tokens from `src/rfu/ui_strings.py`.

**Current status**: Skeleton title/loading/error constants exist per tool.
Menu-item and command-label tokens are not yet populated.

**Activation gate**: CI enforcement of this rule is deferred until
TODO(UI_STRINGS_MENU_TOKENS) is resolved (see §8.6 in the constitution).

### 6.1 Naming Convention for Command Tokens

```python
class MyTool:
    # Tier: Primary
    ACTION_APPLY = "Apply Changes"
    ACTION_RUN   = "Run Scan"

    # Tier: Secondary
    ACTION_PREVIEW = "Preview…"
    ACTION_EXPORT  = "Export…"

    # Tier: Destructive
    ACTION_DELETE  = "Delete Files…"
    ACTION_WIPE    = "Secure Wipe…"

    # Tier: Advanced
    ACTION_ADVANCED_SETTINGS = "Advanced Settings…"
```

---

## 7. Context Menu Rules (§8.7)

```
[ Inspect action ]
[ Transform action ]
[ Export action ]
─────────────────── (separator)
[ Destructive action ]
```

- Only actions relevant to the selected item or context MAY appear.
- Destructive Actions MUST be placed at the bottom, after a separator.
- Nomenclature rules from §7.4 apply identically.

---

## 8. CI Test Suite (§8.8)

| Test ID | Description | Gate |
|---------|-------------|------|
| T1 | Every tool action has a tier assignment in its implementation docs | Phase 2 |
| T2 | No Advanced Action appears in any tool's main toolbar | Phase 2 |
| T3 | Every Destructive Action has a preceding separator in context menus | Phase 2 |
| T4 | All command labels use `ui_strings` tokens (deferred — see §8.6) | TODO(UI_STRINGS_MENU_TOKENS) |
| T5 | No shortcut conflicts with global accelerators (§7.5) | Phase 2 |

---

## 9. Per-Tool Command Taxonomy Mappings

> **TODO(COMMAND_TAXONOMY) RESOLVED** — 2026-04-25. Tables below are the
> canonical Phase 2 command taxonomy for all 35 tools.

Column definitions:
- **Primary Action** — the single main operation; must be a PrimaryButton
- **Secondary** — supporting operations; SecondaryButton
- **Destructive** — irreversible; SecondaryButton + danger + confirmation modal
- **Advanced** — expert operations; menu-item or overflow only
- **Taxonomy Verbs** — which of Inspect/Transform/Export/Apply/Revert apply

### 9.1 File Management

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **File Finder** | Search | Export Results… | — | Index Folder… | Inspect, Export |
| **Catalog Files** | Catalog… | Export Catalog… | Remove Catalog | Rebuild Index… | Inspect, Export, Apply |
| **Organize Files** | Organize… | Dry Run | Undo Last Organization | Advanced Rules… | Apply, Revert |
| **Advanced Folders** | Search | New Folder | Delete Folder | Export…, Settings… | Inspect, Apply, Export |
| **Synchronize** | Sync | Dry Run | — | Advanced Options… | Apply, Inspect |

### 9.2 File Operations

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Rename Files** | Apply Changes | Preview | — | Batch Rename Script… | Transform, Apply |
| **Compress/Decompress** | Apply Changes | Dry Run | — | Advanced Compression… | Transform |
| **Split/Join Files** | Apply Changes | Preview | — | Advanced Split… | Transform |
| **Enhanced Editor** | Apply Changes | Export… | — | Find & Replace…, Advanced Formatting… | Transform, Export |
| **Secure Delete** | Delete… | Dry Run | Delete (Destructive) | Verify Deletion… | Apply |

### 9.3 Analysis

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Size Analyzer** | Analyze | Export Report… | — | Advanced Filters… | Inspect, Export |
| **Duplicate Finder** | Scan | Export Report… | Remove Duplicates… | Hash Algorithm… | Inspect, Export |
| **File Checksum** | Verify | Export Report… | — | Algorithm Settings… | Inspect, Export |
| **Empty Folders** | Scan | Export Report… | Remove Empty Folders… | — | Inspect, Export |

### 9.4 Security

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Security Preferences** | Apply Changes | — | Reset to Defaults… | Export Settings… | Apply, Revert |
| **Encrypt/Decrypt** | Apply Changes | Dry Run | — | Algorithm Settings… | Transform |
| **Permissions Editor** | Apply Changes | Preview | Reset Permissions… | Inherit Permissions… | Apply, Revert |

### 9.5 Metadata

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Edit Image Metadata** | Apply Changes | Export… | Remove All Metadata… | Batch Edit… | Transform, Export |
| **Office Metadata Editor** | Apply Changes | Export… | Remove All Metadata… | — | Transform, Export |
| **File Touch** | Apply Changes | Preview | — | Batch Touch… | Apply |

### 9.6 PDF Tools

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **PDF Utilities** | Apply Changes | Dry Run | — | Advanced Options… | Transform, Export |
| **Extract Links** | Extract… | Export Report… | — | Filter Options… | Inspect, Export |
| **Page Administration** | Apply Changes | Dry Run | Remove Pages… | Advanced Layout… | Transform |

### 9.7 Network

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Network Connectivity** | Scan | Export Report… | — | Advanced Diagnostics… | Inspect, Export |
| **Network Scanner** | Scan | Export Report… | — | Port Range… | Inspect, Export |
| **Network Transfer** | Transfer… | Dry Run | — | Advanced Transfer… | Apply |
| **Bookmark Manager** | Save | Export Bookmarks… | Delete Bookmark… | Import Bookmarks… | Apply, Export |

### 9.8 Privacy

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Privacy Cleaner** | Clean… | Dry Run | Clean (Destructive) | Advanced Targets… | Apply |
| **Data Anonymizer** | Apply Changes | Dry Run | — | Anonymization Rules… | Transform |

### 9.9 System

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Process Monitor** | Refresh | Export Report… | Kill Process… | Filter Settings… | Inspect, Export |
| **Enhanced Clipboard** | Paste | Export… | Clear All… | Clipboard History… | Apply, Export |
| **System Diagnostics** | Run Diagnostics… | Export Report… | — | Advanced Checks… | Inspect, Export |
| **System Cleanup** | Clean… | Dry Run | Clean (Destructive) | Advanced Targets… | Apply |
| **Software Maintenance** | Run Check… | Export Report… | Uninstall… | Advanced Settings… | Inspect, Apply |

### 9.10 Preferences

| Tool | Primary Action | Secondary | Destructive | Advanced | Taxonomy Verbs |
|------|----------------|-----------|-------------|----------|----------------|
| **Preference Portability** | Export… | Import… | Reset to Defaults… | Merge Preferences… | Export, Apply, Revert |

### 9.11 Deviation Register

All tools above use one or more canonical verbs from §8.3 (Inspect, Transform,
Export, Apply, Revert). No deviations requiring special notation as of v1.37.0.

---

## 10. Migration Steps

1. For each tool, classify all actions into Primary / Secondary / Advanced /
   Destructive tiers.
2. Map each action to the closest Command Taxonomy verb (Inspect, Transform,
   Export, Apply, Revert) or document the deviation.
3. Populate `ui_strings` command token constants (see §6.1 naming convention).
4. Register all shortcuts through the Hub Menu Registry (§9.4).
5. Update `docs/tool-capability-matrix.json` to mark `MEN`, `NOM`, `INT`
   capabilities as compliant after review.

---

*See also*: [menu-architecture-spec.md](menu-architecture-spec.md),
[hub-menu-integration-spec.md](hub-menu-integration-spec.md),
[ui-interaction-contract-spec.md](ui-interaction-contract-spec.md),
[.specify/memory/checklist-command-surface-compliance.md](../.specify/memory/checklist-command-surface-compliance.md)
