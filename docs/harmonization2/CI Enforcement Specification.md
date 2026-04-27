PROMPT: 

please create a A CI rule specification for enforcing the matrix

RESPONSE: 

Absolutely, Richard — here is a **full CI Rule Specification for enforcing the Tool Capability Matrix**, written in the same constitutional, deterministic style as your other governance artifacts. It is self‑contained, reviewer‑proof, and ready to drop into your governance repo as **Constitution §11 — CI Enforcement Specification**.

No templates are appropriate here (this is not a credentialing timeline), and no web search is needed — this is pure governance architecture.

Let’s get to work.

---

# **Constitution §11 — CI Enforcement Specification**  
### *Defines how CI validates harmonization, interaction rules, and cross‑tool compliance*

---

# **§11.1 Purpose**
This specification defines the mandatory CI rules, automated checks, failure conditions, and reporting requirements that enforce the **Tool Capability Matrix** and all associated constitutional sections.

Its purpose is to ensure:

- Deterministic enforcement of governance  
- Prevention of regressions  
- Uniform behavior across all 22 tools  
- Zero reliance on human memory or reviewer intuition  
- Auditability and traceability of compliance  

CI is the **final authority** on whether a tool is allowed to merge.

---

# **§11.2 Scope**
CI MUST enforce:

- All harmonization domains (TH, DR, CP, A11Y, PERF, ERR, GRD, TEL, STR, CE, HUB)  
- All interaction rules (INT)  
- All operational guarantees (OPS)  
- All menu, nomenclature, typography, and layout rules (MEN, NOM, FNT, LYT, WRD)  
- All localization readiness rules (L10N, when enabled)  

CI MUST reject merges that violate any rule in this section.

---

# **§11.3 CI Architecture Overview**
CI MUST consist of the following enforcement layers:

1. **Static Analysis Layer**  
   Detects violations in code, strings, menus, fonts, and layout.

2. **Schema Validation Layer**  
   Validates tool metadata, menu registrations, telemetry schemas, and preference schemas.

3. **Runtime Test Layer**  
   Executes automated UI tests, Guardian tests, CE tests, and performance tests.

4. **Matrix Compliance Layer**  
   Ensures each tool satisfies all required capabilities.

5. **Reporting Layer**  
   Produces machine‑readable compliance reports and human‑readable summaries.

Each layer MUST run on every PR.

---

# **§11.4 Static Analysis Rules**
CI MUST fail if any of the following are detected:

### **§11.4.1 Theming (TH)**
- Raw color values (hex, rgb, rgba)  
- Raw font declarations  
- Missing theme token usage  
- Missing `_on_theme_changed` handlers  

### **§11.4.2 Dry‑Run (DR)**
- Destructive actions without dry‑run branching  
- Missing dry‑run toggle wiring  

### **§11.4.3 Shared Components (CP)**
- Raw Qt widgets where shared components exist  
- Custom button classes duplicating Primary/SecondaryButton  
- Custom modal implementations  

### **§11.4.4 Accessibility (A11Y)**
- Missing accessible names  
- Missing accessible descriptions  
- Color‑only indicators  
- Touch targets < minimum size  

### **§11.4.5 Error Handling (ERR)**
- `str(e)` surfaced directly to UI  
- Missing `logger.error`  
- Missing error codes  
- Missing ModalError usage  

### **§11.4.6 Strings (STR)**
- Raw user‑visible strings not in `ui_strings.py`  
- Hardcoded English text  
- Missing string tokens  

### **§11.4.7 Menu Architecture (MEN)**
- Tools adding top‑level menus  
- Tools registering items under prohibited menus  
- Missing accelerators  
- Violations of nomenclature rules  

### **§11.4.8 Typography (FNT)**
- Raw font families  
- Raw pixel sizes  
- Missing font tokens  

### **§11.4.9 Layout (LYT)**
- Missing safe‑area margins  
- Hardcoded spacing not using layout tokens  
- Inconsistent padding  

### **§11.4.10 Wording (WRD)**
- Non‑imperative verbs in action labels  
- Incorrect ellipsis usage  
- Inconsistent capitalization  

---

# **§11.5 Schema Validation Rules**
CI MUST validate:

### **§11.5.1 Menu Registry Schema**
- All menu items registered via Hub Menu Registry  
- No direct Qt menu manipulation  
- No accelerator conflicts  
- Correct menu category usage  

### **§11.5.2 Telemetry Schema**
- All events follow naming conventions  
- Required fields present  
- No unregistered event types  

### **§11.5.3 Preference Schema**
- All preferences follow naming conventions  
- Versioning rules respected  
- Migration scripts present when needed  

### **§11.5.4 Tool Metadata Schema**
- Tool name  
- Tool classification (Standard / CE)  
- Tool capabilities  
- Tool owner  

---

# **§11.6 Runtime Test Rules**
CI MUST execute:

### **§11.6.1 UI Interaction Tests (INT)**
- Primary actions use PrimaryButton  
- Destructive actions trigger confirmation modals  
- LoadingIndicator appears for long‑running operations  
- No UI thread blocking > 100 ms  

### **§11.6.2 Guardian Tests (GRD)**
- `register_gui_component()` called  
- `health_check()` returns valid state  
- `degraded_fallback()` functional  

### **§11.6.3 Critical Engine Tests (CE)**
For CE‑classified tools:

- Property‑based tests  
- Scenario tests  
- Irreversibility tests  
- Security‑sensitive behavior tests  

### **§11.6.4 Performance Tests (PERF)**
- Worker offloading verified  
- No synchronous I/O on UI thread  
- Perf markers emitted  

---

# **§11.7 Matrix Compliance Rules**
CI MUST:

- Load the Tool Capability Matrix  
- Evaluate each capability for the tool under test  
- Fail if any required capability is missing  
- Fail if any capability is marked “Partial”  
- Fail if any capability is marked “Unknown”  

Tools MUST be **fully compliant** to merge.

---

# **§11.8 Reporting Requirements**
CI MUST produce:

### **§11.8.1 Machine‑Readable Report**
- JSON file  
- One entry per capability  
- Pass/Fail/Not Applicable  
- Error messages  
- Line numbers for violations  

### **§11.8.2 Human‑Readable Summary**
- Markdown summary  
- Capability table  
- Violations grouped by category  
- Suggested fixes  

### **§11.8.3 Hub Dashboard Integration**
CI MUST update the Hub’s governance dashboard with:

- Tool compliance status  
- Last reviewed date  
- Reviewer  
- Phase gate status  

---

# **§11.9 Failure Conditions**
CI MUST fail the PR if:

- Any rule in §11.4–§11.7 is violated  
- Any test fails  
- Any schema validation fails  
- Any capability is missing  
- Any reserved name is violated  
- Any accelerator conflict exists  
- Any raw string is detected  

CI MUST NOT allow overrides except by constitutional amendment.

---

# **§11.10 Future Extensibility**
CI MUST support:

- Localization checks (L10N)  
- Plugin tool validation  
- Multi‑tool scenario validation  
- Cross‑tool consistency checks  

Tools MUST NOT implement their own CI logic.

---

# **If you want, I can now generate:**
- **The Reviewer Checklist** (human‑facing, 1 page, deterministic)  
- **The Migration Plan** (how to bring all 22 tools into compliance)  
- **The Governance Dashboard Spec** (how to visualize compliance)  
- **The CI Implementation Blueprint** (GitHub Actions / Azure DevOps pipelines)  

Just tell me which one you want next.