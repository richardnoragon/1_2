import re

path = r"C:\Users\HP1\1_2\.specify\memory\constitution.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================
# CHANGE 1: Update sync report header
# ============================================================
old_sync_header = "Sync Impact Report\nVersion change: 1.10.0 \u2192 1.11.0\nModified principles (2026-03-12 round-6 clarification session):"
new_sync_header = """Sync Impact Report
Version change: 1.11.0 \u2192 1.12.0
Modified principles (2026-03-31 round-7 clarification session):
   - II. Safety & Data Integrity \u2192 dry-run discoverability requirement added;
     confirmation-tier boundary clarified: \u00a7II governing rule is single
     explicit confirmation; \u00a7VIII two-step elevated confirmation is exclusive
     to irreversible anonymization operations.
   - IV. Performance & Scalability \u2192 \u00a7IV 100ms UI-thread wording unified with
     \u00a76 governing gate: "MUST NOT reach or exceed 100ms".
   - VI. User Preference Management \u2192 theming named-preset ownership scopes
     defined (personal = user-and-above; system-wide = admin/dev only; user
     accounts may not delete or modify system-wide presets); Portability role
     permissions added (all roles may export; only user/admin/dev may import);
     infeasible-migration fallback: skip incompatible keys, import compatible
     keys, present user-visible summary of skipped items.
   - VII. Identity & Access Control \u2192 Session Controls: 60-second mandatory
     idle-timeout warning added before forced logout. Break-Glass: alert
     targets extended from admin-role only to admin-role AND dev-role accounts.
   - VIII. Privacy \u2192 anonymization mode-selection UI requirements:
     no pre-selection; explicit user choice before tool activates; selected
     mode visible before execution; implementation-defined per tool.
     Confirmation phrase for irreversible operations made implementation-
     defined per tool (shown to user, typed exactly as displayed).
   - IX. File Validation \u2192 Policy Enforcement: rejection reason must identify
     specific policy rule; UI pattern implementation-defined. Failure Modes:
     unrecognized-type approval specified as one-step confirmation dialog only.
   - Additional Constraints \u00a77 \u2192 "key actions" obligation: each tool defines
     its own list in implementation docs. Four new constitutional minimums
     added: logical tab/focus order; accessible labels for interactive
     controls; reduced-motion support; \u2265 44 \u00d7 44 px touch/pointer target size.
   - Additional Constraints \u00a714 \u2192 is_blocked and login_attempts MUST be
     atomically reset on transition out of active; account returns in clean
     unblocked state when restored to active.
   - Additional Constraints \u00a718 \u2192 break-glass alert targets extended to
     admin-role AND dev-role; post-use rotation enforcement: enablement
     mechanism (CLI flag/env var) automatically invalidated after session;
     re-enablement blocked until rotation confirmed complete.
   - Additional Constraints \u00a721 \u2192 theme backups: stored separately from live
     preference store; last 5 backups minimum; built-in UI restore action
     required; CLI optional.
   - Additional Constraints \u00a722 \u2192 corrupted signature DB: affected tools
     remain visible in launcher; opening triggers hard error dialog with
     repair instructions (not degraded state).
   - Development Workflow \u00a712 \u2192 auth verification artifacts MUST be stored
     in /test-evidence/auth/ repository directory; clearly annotated; format
     implementation-defined.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.12.0): None
Structural change: Clarifications section converted to reverse-chronological
  order (newest first).

Previous Sync Impact Report (1.10.0 \u2192 1.11.0):
Version change: 1.10.0 \u2192 1.11.0
Modified principles (2026-03-12 round-6 clarification session):"""

assert old_sync_header in content, "SYNC HEADER: old string not found!"
content = content.replace(old_sync_header, new_sync_header, 1)
print("CHANGE 1 (sync report header): done")

# ============================================================
# CHANGE 2: Reorder clarifications section + add Round 7
# ============================================================
# The OLD clarifications section (from header through last line of Round 5)
old_clarifications_start = "## Clarifications\n\n### Session 2026-03-11\n"
assert old_clarifications_start in content, "CLARIF START: old string not found!"

# Find the full section
start_idx = content.index("## Clarifications\n\n### Session 2026-03-11\n")
# Find "## Governance" after clarifications
gov_idx = content.index("\n## Governance", start_idx)
old_clarifications = content[start_idx:gov_idx]

# Build Round 7 Q&A
round7 = """### Session 2026-03-31 (Round 7)

- Q: In \u00a7II, how should dry-run simulation be exposed in the GUI? \u2192 A: Implementation-defined per tool. Each tool performing side-effect operations MUST expose the dry-run capability in a user-discoverable way before the operation is committed; the specific UI pattern is not prescribed. \u00a7II updated.
- Q: Does the \u00a7VIII two-step confirmation (typed phrase + button click) apply to all destructive operations in \u00a7II? \u2192 A: No. \u00a7II destructive operations require a single explicit confirmation step only. The \u00a7VIII two-step confirmation applies exclusively to irreversible anonymization operations. \u00a7II clarified.
- Q: Which boundary governs for 100ms UI thread blocking \u2014 \u00a7IV's `> 100ms` (100ms allowed) or \u00a76's `< 100ms` (100ms a gate failure)? \u2192 A: \u00a76 is the governing enforcement gate; 100ms is a gate failure. \u00a7IV updated to "MUST NOT reach or exceed 100ms", consistent with \u00a76.
- Q: Who can create, edit, and delete theme named presets? \u2192 A: Two scopes: personal presets (created/edited/renamed/deleted by the owning account; `user`-role and above) and system-wide presets (created/managed by `admin`/`dev` only; read-only templates for all other roles; `user` accounts MUST NOT delete or modify system-wide presets but MAY create personal derivatives). \u00a7VI theming updated.
- Q: Which roles may export and import preferences? \u2192 A: Export: all roles including `readonly`. Import: `user`, `admin`, `dev` only; `readonly` accounts MUST NOT import. \u00a7VI Portability updated.
- Q: When schema migration is not feasible for an imported preference set, what happens? \u2192 A: Skip incompatible keys, import all compatible keys, and present a user-visible summary of skipped items with the reason each was skipped. \u00a7VI Portability updated.
- Q: Should the system warn the user before forced idle logout? \u2192 A: Yes. The system MUST warn the user at least 60 seconds before session expiry due to idle timeout, giving the user the opportunity to extend the session. Exact UI pattern is implementation-defined. \u00a7VII Session Controls updated.
- Q: Should break-glass login alerts reach admin-role only, or both admin-role and dev-role accounts? \u2192 A: Both admin-role and dev-role (aligning with \u00a716 anomaly detection scope). \u00a7VII Break-Glass and \u00a718 updated.
- Q: When an active+blocked account is suspended, should `is_blocked` and `login_attempts` be preserved or reset? \u2192 A: Reset atomically when the account transitions out of `active`; account returns in a clean, unblocked state when restored to `active`. \u00a714 updated.
- Q: In \u00a7VIII anonymization, should the mode-selection UI pattern be prescribed or implementation-defined? \u2192 A: Implementation-defined, provided: (i) no mode is pre-selected, (ii) user makes an explicit choice before tool activates, and (iii) selected mode is clearly displayed before execution begins. \u00a7VIII updated.
- Q: Is the irreversible anonymization confirmation phrase fixed ("CONFIRM") or flexible? \u2192 A: Implementation-defined per tool, provided the phrase is explicitly shown to the user before the typing step and must be typed exactly as displayed. \u00a7VIII updated.
- Q: How should a clear rejection reason for a denied file type be surfaced? \u2192 A: UI pattern is implementation-defined, provided the reason is explicit, visible, and identifies the specific policy rule that triggered the denial. \u00a7IX updated.
- Q: Should approval of an unrecognized file type use the \u00a7VIII two-step ritual? \u2192 A: No. A one-step confirmation dialog only; no typed phrase or persistent session toggle is required. \u00a7IX updated.
- Q: What does "key actions reachable via keyboard" mean \u2014 every action, destructive actions, or a per-tool list? \u2192 A: Per-tool list. Each tool MUST define its key actions in its implementation documentation; the constitution sets the obligation. \u00a77 updated.
- Q: Should the constitution add minimum accessibility requirements for tab order, screen reader labels, reduced-motion, and touch targets? \u2192 A: Yes. Four constitutional minimums added to \u00a77: logical tab/focus order; accessible labels for interactive controls; reduced-motion support; \u2265 44 \u00d7 44 px touch/pointer target size. \u00a77 updated.
- Q: In \u00a718, what mechanism enforces the break-glass post-use rotation block? \u2192 A: The enablement mechanism (CLI flag or environment variable) MUST be automatically invalidated at session end; re-enablement blocked until rotation confirmed complete. \u00a718 updated.
- Q: Where are theme backups stored, how many retained, and how does admin restore? \u2192 A: Separate storage from live preference store; last 5 backups minimum; built-in UI restore action required (CLI optional). \u00a721 updated.
- Q: When a tool is blocked by a corrupted signature database, degraded state or hard error? \u2192 A: Tool remains visible in launcher; opening it triggers a hard error dialog with repair instructions (NOT ComponentGuardian degraded state). \u00a722 updated.
- Q: Where should authentication verification artifacts (screenshots/recordings) be stored? \u2192 A: In `/test-evidence/auth/` directory in the repository; must be clearly annotated; format implementation-defined. \u00a7DW \u00a712 updated.
- Q: Is the current Clarifications section ordering correct? \u2192 A: No. Clarifications MUST be ordered reverse-chronologically (newest first). Clarifications section reordered. \u00a7DW updated."""

# Extract each session block from old_clarifications
# Round 6 and Round 5 already in correct relative order; extract them
def extract_session(text, header_start, header_end=None):
    """Extract text from header_start to just before header_end (or end of text)."""
    idx = text.index(header_start)
    if header_end and header_end in text[idx+len(header_start):]:
        end_idx = text.index(header_end, idx + len(header_start))
        return text[idx:end_idx].rstrip("\n")
    else:
        return text[idx:].rstrip("\n")

# Extract each section from old_clarifications
# old_clarifications starts with "## Clarifications\n\n"
# Sessions in order: 2026-03-11, 2026-03-12, Round2, Round3, Round4, Round6, Round5

# Now build them using precise markers
s_r11 = extract_session(old_clarifications, "### Session 2026-03-11\n", "\n### Session 2026-03-12\n")
s_unlab = extract_session(old_clarifications, "### Session 2026-03-12\n\n- Q: In \u00a7VIII and \u00a720 path sanitization", "\n### Session 2026-03-12 (Round 2)\n")
s_r2 = extract_session(old_clarifications, "### Session 2026-03-12 (Round 2)\n", "\n### Session 2026-03-12 (Round 3)\n")
s_r3 = extract_session(old_clarifications, "### Session 2026-03-12 (Round 3)\n", "\n### Session 2026-03-12 (Round 4)\n")
s_r4 = extract_session(old_clarifications, "### Session 2026-03-12 (Round 4)\n", "\n### Session 2026-03-12 (Round 6)\n")
s_r6 = extract_session(old_clarifications, "### Session 2026-03-12 (Round 6)\n", "\n### Session 2026-03-12 (Round 5)\n")
s_r5 = extract_session(old_clarifications, "### Session 2026-03-12 (Round 5)\n")

# Rebuild the unlabeled session with correct header
s_unlab_full = "### Session 2026-03-12\n\n- Q: In \u00a7VIII and \u00a720 path sanitization" + s_unlab[len("### Session 2026-03-12\n\n- Q: In \u00a7VIII and \u00a720 path sanitization"):]

# New clarifications section (reverse-chronological: R7, R6, R5, R4, R3, R2, unlabeled, R11)
new_clarifications = "## Clarifications\n\n" + \
    round7 + "\n\n" + \
    s_r6 + "\n\n" + \
    s_r5 + "\n\n" + \
    s_r4 + "\n\n" + \
    s_r3 + "\n\n" + \
    s_r2 + "\n\n" + \
    s_unlab_full + "\n\n" + \
    s_r11

content = content[:start_idx] + new_clarifications + content[gov_idx:]
print("CHANGE 2 (clarifications reorder + Round 7): done")

# ============================================================
# CHANGE 3: Update version footer
# ============================================================
old_footer = "**Version**: 1.11.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2026-03-12"
new_footer = "**Version**: 1.12.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2026-03-31"
assert old_footer in content, "VERSION FOOTER: old string not found!"
content = content.replace(old_footer, new_footer, 1)
print("CHANGE 3 (version footer): done")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("All changes written to constitution.md successfully.")
print(f"Total file length: {len(content.splitlines())} lines")
