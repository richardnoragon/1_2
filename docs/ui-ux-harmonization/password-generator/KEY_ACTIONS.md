# KEY_ACTIONS — Password Generator

**Tool:** Password Generator  
**Source:** `src/tools/security/password_generator/password_generator.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Set Password Length | `Tab` to length spin box → up/down arrow keys or type value | No — configuration only |
| 2 | Toggle Uppercase Characters (A-Z) | `Tab` to "Include Uppercase" checkbox → `Space` | No — configuration only |
| 3 | Toggle Lowercase Characters (a-z) | `Tab` to "Include Lowercase" checkbox → `Space` | No — configuration only |
| 4 | Toggle Numeric Characters (0-9) | `Tab` to "Include Numbers" checkbox → `Space` | No — configuration only |
| 5 | Toggle Symbol Characters (!@#$%^&*) | `Tab` to "Include Symbols" checkbox → `Space` | No — configuration only |
| 6 | Toggle Exclude Ambiguous Characters (0Ol1I) | `Tab` to "Exclude Ambiguous" checkbox → `Space` | No — configuration only |
| 7 | Set Batch Count | `Tab` to count spin box → up/down arrow keys or type value | No — configuration only |
| 8 | Generate Single Password | `Tab` to "🎲 Generate Password" button → `Enter` | No — generates in-memory string; no file writes |
| 9 | Generate Multiple Passwords | `Tab` to "🎲 Generate Multiple" button → `Enter` | No — generates in-memory list; no file writes |
| 10 | Copy to Clipboard | `Tab` to "📋 Copy to Clipboard" button → `Enter` | No — writes to system clipboard; no file writes |

### Notes

- All Password Generator operations are read-only with respect to the filesystem. No side effects.
- Button labels confirmed from source: "🎲 Generate Password", "📋 Copy to Clipboard", "🎲 Generate Multiple".
