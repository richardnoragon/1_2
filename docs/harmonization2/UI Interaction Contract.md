# **2) UI Interaction Contract (Constitutional Section)**  
### *Constitution §10 — UI Interaction Contract*  
Defines how every tool must behave, regardless of platform or internal implementation.

---

## **§10.1 Purpose**
This contract establishes the mandatory interaction patterns, behavioral guarantees, and user‑experience invariants that all tools MUST follow.  
Its purpose is to ensure predictability, accessibility, and cognitive consistency across the entire suite.

---

## **§10.2 Scope**
This contract applies to:

- All tool windows  
- All dialogs, modals, and toasts  
- All interactive controls  
- All destructive or irreversible actions  
- All long‑running operations  
- All Hub‑launched workflows  

Issue #81 modernizes the shared styling layer behind this contract with refreshed tokens, contrast checks, and accessibility defaults on the common base windows and dialogs.

---

## **§10.3 Interaction Principles**
All tools MUST adhere to the following principles:

1. **Predictability** — identical actions behave identically across tools  
2. **Reversibility** — destructive actions require explicit confirmation  
3. **Visibility** — system state and progress MUST be visible  
4. **Non‑blocking UI** — no UI thread blocking beyond 100 ms  
5. **Accessibility** — all interactions MUST be keyboard‑navigable and zoom‑safe  
6. **Determinism** — no hidden side effects  

---

## **§10.4 Action Classification**
All actions MUST be classified as:

- **Primary Action** — the main operation (e.g., Apply, Run, Validate)  
- **Secondary Action** — supportive operations (e.g., Preview, Export)  
- **Destructive Action** — irreversible or high‑impact operations  
- **Advanced Action** — expert‑level or rarely used operations  

Tools MUST expose these classes consistently.

---

## **§10.5 Primary Action Rules**
Primary actions MUST:

- Use a **PrimaryButton**  
- Be placed in the **bottom‑right** of dialogs  
- Use imperative verbs  
- Emit telemetry (`ui_user_action`)  
- Respect dry‑run mode  

---

## **§10.6 Destructive Action Rules**
Destructive actions MUST:

- Use a **SecondaryButton** with danger styling  
- Trigger a **confirmation modal**  
- Support dry‑run mode  
- Emit telemetry (`ui_error_event` if failed)  
- Provide a clear description of consequences  

---

## **§10.7 Long‑Running Operations**
All long‑running operations MUST:

- Move work off the UI thread  
- Display a **LoadingIndicator**  
- Disable conflicting controls  
- Emit telemetry (`perf_start` / `perf_end`)  
- Support cancellation if feasible  

---

## **§10.8 Error Handling**
All tools MUST:

- Surface errors using the shared **ModalError** component  
- Provide actionable messages  
- Avoid raw exception strings  
- Emit telemetry (`ui_error_event`)  
- Provide Guardian fallback if the tool becomes degraded  

---

## **§10.9 Navigation Rules**
Tools MUST:

- Provide **Return to Hub**  
- Register with the Hub Window Manager  
- Respect the global menu structure  
- Expose consistent keyboard shortcuts  

---

## **§10.10 Accessibility Rules**
All tools MUST:

- Provide accessible names and descriptions  
- Support full keyboard navigation  
- Respect zoom scaling  
- Avoid color‑only indicators  
- Maintain minimum touch targets  

---

## **§10.11 CI Enforcement**
CI MUST reject merges if:

- A tool violates any interaction rule  
- A destructive action lacks confirmation  
- A long‑running action blocks the UI thread  
- A tool uses raw Qt widgets instead of shared components  
- A tool omits telemetry for primary actions  