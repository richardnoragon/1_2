# **Constitution §9 — Hub Menu Integration Specification**  
### *Defines how the Hub and all tools integrate with the Global Menu Bar*

---

# **§9.1 Purpose**
This section establishes the mandatory rules for how the **Hub** and all **Hub‑launched tools** integrate with the Global Menu Bar defined in Constitution §7.  
It ensures:

- Predictable navigation  
- Consistent menu behavior  
- Deterministic fallback paths  
- Cross‑tool discoverability  
- A unified product identity  

The Hub is the **root of truth** for menu structure, menu registration, and menu behavior.

---

# **§9.2 Scope**
This specification applies to:

- The Hub window  
- All tool windows launched from the Hub  
- All tool GUIs that expose their own menu bar  
- All menu items registered by tools  

This specification supersedes any tool‑specific menu definitions.

---

# **§9.3 Hub as the Menu Authority**
The Hub is the **canonical owner** of:

- Top‑level menu structure  
- Menu taxonomy  
- Reserved menu items  
- Global accelerators  
- Global wording and nomenclature  

Tools MAY register menu items, but MAY NOT modify:

- Top‑level menu names  
- Top‑level menu ordering  
- Reserved menu items  
- Global accelerators  

Tools MUST register all menu items through the **Hub Menu Registry**.

---

# **§9.4 Hub Menu Registry**
The Hub exposes a **Menu Registry API** that all tools MUST use.

### **§9.4.1 Registration Rules**
Tools MUST register:

- Their menu items  
- Their accelerators  
- Their tooltips  
- Their enable/disable conditions  
- Their visibility conditions  

Tools MUST NOT directly manipulate Qt menu objects.

### **§9.4.2 Deregistration**
When a tool window closes:

- All tool‑specific menu items MUST be automatically removed  
- Global menu items MUST remain unaffected  

### **§9.4.3 Conflicts**
If two tools attempt to register the same accelerator:

- The Hub MUST reject the second registration  
- The Hub MUST surface a Guardian warning  
- CI MUST fail if this occurs in automated tests  

---

# **§9.5 Hub Menu Structure**
The Hub MUST expose the Global Menu Bar exactly as defined in Constitution §7:

1. File  
2. Edit  
3. View  
4. Tools  
5. Reports  
6. Window  
7. Help  

The Hub MUST populate:

- Global items  
- Hub‑specific items  
- Tool‑registered items  

in that order.

---

# **§9.6 Hub‑Specific Menu Items**
The Hub MUST expose the following items, in addition to the global reserved items:

### **File**
- **Return to Hub** (visible only in tool windows)  
- **Exit**

### **View**
- **Show Hub Tabs**  
- **Show Tool List**  
- **Reset Layout**

### **Tools**
- **Open Preferences…**  
- **Reload Tool Registry**  
- **Run Diagnostics…**

### **Window**
- **Hub Home**  
- **Open Tool Window…**  
- **Switch to Previous Tool**

### **Help**
- **Hub Documentation**  
- **Keyboard Shortcuts**  
- **About Hub**

These items MUST always be present and MUST NOT be overridden by tools.

---

# **§9.7 Tool Menu Integration Rules**

## **§9.7.1 Allowed Menu Categories**
Tools MAY add items only under:

- **Tools**  
- **Reports**  
- **View**  

Tools MUST NOT add items under:

- File  
- Edit  
- Window  
- Help  

unless explicitly granted an exemption.

## **§9.7.2 Tool Menu Naming**
Tools MUST prefix their menu items with their tool name when ambiguity is possible.

Example:

- **Validate Budget** (if unique)  
- **Budgetinator: Validate Budget** (if not unique)

## **§9.7.3 Tool Menu Visibility**
Tool menu items MUST:

- Appear only when the tool window is active  
- Disappear when the tool window closes  
- Respect enable/disable conditions defined by the tool  

## **§9.7.4 Tool Menu Ordering**
Within each allowed menu:

1. Tool‑specific actions  
2. Tool‑specific advanced actions  
3. Tool‑specific diagnostics  
4. Separator  
5. Hub‑provided items (always last)

---

# **§9.8 Hub–Tool Navigation Integration**

## **§9.8.1 Return to Hub**
Every tool window MUST expose:

- **File → Return to Hub**  
- A keyboard shortcut (default: Ctrl+H)  
- A Guardian fallback if the Hub is unavailable  

## **§9.8.2 Relaunch Tool Window**
Tools MUST register a relaunch action:

- **Window → Reopen <ToolName>**  
- This MUST call `relaunch_tool_window()`  

## **§9.8.3 Cross‑Tool Navigation**
The Hub MUST maintain a list of open tool windows and expose them under:

- **Window → Open Windows**  

Tools MUST NOT manage this list themselves.

---

# **§9.9 Accessibility Requirements**
All Hub and tool menu items MUST:

- Support keyboard navigation  
- Expose accelerators  
- Respect zoom scaling  
- Respect high‑contrast mode  
- Provide accessible names and descriptions  

Tools MUST NOT override accessibility metadata provided by the Hub.

---

# **§9.10 Telemetry Requirements**
The Hub MUST emit telemetry for:

- Menu item activation  
- Menu item visibility changes  
- Accelerator usage  
- Tool menu registration events  
- Tool menu deregistration events  

Tools MUST NOT emit telemetry for menu events directly.

---

# **§9.11 Guardian Integration**
If a tool fails to register its menu items:

- The Hub MUST surface a Guardian warning  
- The tool MUST enter degraded mode  
- The Hub MUST expose a fallback “Tool Unavailable” item under Tools  

---

# **§9.12 CI Enforcement**
CI MUST reject merges if:

- A tool attempts to add a top‑level menu  
- A tool registers items under prohibited menus  
- A tool uses raw Qt menu APIs  
- A tool registers a menu item without a ui_strings token  
- A tool registers a menu item without an accelerator  
- A tool registers a menu item with a conflicting accelerator  
- A tool fails to deregister its menu items on close  

---

# **§9.13 Future Extensibility**
The Hub MUST support:

- Dynamic menu injection  
- Dynamic menu removal  
- Menu versioning  
- Menu schema validation  
- Localization of all menu items  

Tools MUST NOT implement their own localization logic.