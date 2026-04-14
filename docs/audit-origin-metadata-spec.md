# Audit Log Origin Metadata — Canonical Specification

**Constitutional authority**: §16.X.1–§16.X.7  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.27.0)  
**Last updated**: 2026-04-05  

---

## 1. Purpose

Every audit event in RFU MUST carry "origin metadata" — the contextual
fields that attribute the event to a specific actor, session, device, and
(where applicable) network origin. This specification defines the minimum
required field set, additional requirements for network-originating events,
privacy constraints, and CI enforcement expectations.

**Resolves**: TODO(AUDIT_ORIGIN_METADATA) — open since constitution v1.11.0,
closed in v1.27.0 via §16.X.

**See also**:  
- [.specify/memory/checklist-audit-origin-metadata-compliance.md](../.specify/memory/checklist-audit-origin-metadata-compliance.md) — reviewer checklist  
- [.specify/memory/constitution.md](../.specify/memory/constitution.md) — §16, §16.X  

---

## 2. Minimum Origin Metadata (All Events)

The following four fields MUST be present in **every** audit event,
regardless of event type:

| Field | Type | Description |
|-------|------|-------------|
| `actor_username` | string | Username of the actor performing the action (aligns with `actor` field in §16 base audit schema) |
| `session_id` | string (UUID or opaque token) | The authenticated session that produced the event; use a synthetic `"system"` session ID for background tasks |
| `device_id` | string (pseudonymized hash) | Logical device identifier; MUST be hashed or pseudonymized — raw hardware identifiers MUST NOT be stored |
| `app_instance_id` | string | Identifier of the application instance that generated the event; required for multi-node deployments |

These fields MUST be present for:
- `login_success`, `login_failure`, `logout`
- `reset`, `unblock`
- Account lifecycle events (creation, role change, suspension)
- MFA enrollment/removal events
- Headless HMAC token issuance and redemption (§II.5.5)
- Break-glass login and rotation events (§18)
- All `is_protected` blocked-operation events (§DW17.X.5)
- Any other auditable event defined in the constitution

---

## 3. Additional Metadata for Network-Originating Events

For events triggered by an incoming network request, the following three
fields MUST also be included:

| Field | Type | Description |
|-------|------|-------------|
| `client_ip_hash` | string (one-way hash) | Pseudonymized network origin; raw IP MUST NOT be stored (see §4) |
| `user_agent` | string | Raw user-agent string as received; not PII when stored as a string without linkage |
| `protocol` | string | Transport protocol (e.g., `"https"`, `"ssh"`, `"http"`) |

**Network-originating events** include but are not limited to:
- Any event generated in response to a client HTTP/HTTPS request
- SSH-based management operations
- API calls from external clients

**Non-network events** (background tasks, scheduled jobs, local system
actions) MAY omit these three fields.

---

## 4. Privacy Constraints

### 4.1 Prohibited Fields

Implementations MUST NOT store any of the following in audit logs:

- **Raw IP addresses** — these are PII under GDPR in most EU jurisdictions
- **Hostnames** — may contain personal data (e.g., user-named machines)
- **OS-level usernames** — personal data in most contexts
- **Hardware serial numbers** — unique device fingerprints constitute PII
- **Any unique device identifier** beyond a pseudonymized `device_id`

### 4.2 Pseudonymization Requirement

`client_ip_hash` and `device_id` MUST be produced by a **stable, one-way
hashing mechanism** that satisfies all of:

1. **Deterministic** — the same input always produces the same hash within
   a deployment, allowing correlation across events.
2. **One-way** — the original value cannot be reconstructed from the hash
   without the key.
3. **Keyed** — use HMAC-SHA-256 with a deployment-specific key stored in a
   secret store (not in source code or version control).
4. **Consistent** — the same hash function and key MUST be used for all
   events of the same type across all application modules.

### 4.3 GDPR Considerations

Hashed/pseudonymized IP addresses are considered pseudonymous data under
GDPR Article 4(5) and may still be subject to data-subject rights if
re-identification is possible with additional data. Implementations in
regulated EU environments SHOULD document their pseudonymization key
management and data retention policies in a Data Protection Impact
Assessment (DPIA).

---

## 5. Field Consistency Requirements

All audit events across all RFU modules MUST:

- Use **identical field names** for origin metadata (no module-by-module
  variation, e.g., `actor_user` vs `actor_username`)
- Use **consistent types** (all UUIDs formatted as UUID v4 strings, all
  timestamps as ISO 8601 UTC)
- Include origin metadata at the **same structural level** in the log entry
  (not nested inconsistently)

### 5.1 Canonical Audit Event Shape

```json
{
  "timestamp": "2026-04-05T12:34:56.789Z",
  "action": "login_failure",
  "username": "<subject account>",
  "actor": "<actor account or attempted username>",
  "correlation_id": "<uuid>",
  "origin": {
    "actor_username": "<actor>",
    "session_id": "<uuid or 'system'>",
    "device_id": "<hmac-sha256-hash>",
    "app_instance_id": "<instance-id>",
    "client_ip_hash": "<hmac-sha256-hash>",
    "user_agent": "<raw UA string>",
    "protocol": "https"
  }
}
```

> **Note**: `client_ip_hash`, `user_agent`, and `protocol` are included only
> for network-originating events. Non-network events omit those three fields.

---

## 6. Reference Implementation

### 6.1 Pseudonymization Helper

```python
import hmac
import hashlib
import os

# Load from secret store; never hard-code
_PSEUDONYMIZATION_KEY = os.environ["RFU_AUDIT_PSEUDONYMIZATION_KEY"].encode()


def pseudonymize(value: str) -> str:
    """Return a stable HMAC-SHA256 hex digest for an arbitrary input string."""
    return hmac.new(
        _PSEUDONYMIZATION_KEY,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
```

### 6.2 Origin Metadata Factory

```python
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class OriginMetadata:
    actor_username: str
    session_id: str
    device_id: str          # pre-pseudonymized by caller
    app_instance_id: str
    client_ip_hash: Optional[str] = None   # network events only
    user_agent: Optional[str] = None       # network events only
    protocol: Optional[str] = None         # network events only

    def to_dict(self) -> dict:
        d = asdict(self)
        # Omit None fields for non-network events
        return {k: v for k, v in d.items() if v is not None}


def build_origin_metadata(
    actor_username: str,
    session_id: str,
    raw_device_id: str,
    app_instance_id: str,
    raw_client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    protocol: Optional[str] = None,
) -> OriginMetadata:
    return OriginMetadata(
        actor_username=actor_username,
        session_id=session_id,
        device_id=pseudonymize(raw_device_id),
        app_instance_id=app_instance_id,
        client_ip_hash=pseudonymize(raw_client_ip) if raw_client_ip else None,
        user_agent=user_agent,
        protocol=protocol,
    )
```

---

## 7. CI Tests

### T1 — All events include minimum metadata (non-network)

```python
def test_all_events_include_minimum_origin_metadata():
    """Every audit event type must contain the four core origin fields."""
    event_types = [
        "login_success", "login_failure", "logout", "reset", "unblock",
        "account_creation", "role_change", "mfa_enrollment", "mfa_removal",
        "hmac_token_issuance", "hmac_token_redemption",
        "breakglass_login", "protected_account_violation",
    ]
    required_fields = {"actor_username", "session_id", "device_id", "app_instance_id"}
    for event_type in event_types:
        event = generate_audit_event(event_type)
        origin = event.get("origin", {})
        missing = required_fields - set(origin.keys())
        assert not missing, f"Event '{event_type}' missing fields: {missing}"
```

### T2 — Network events include network metadata

```python
def test_network_events_include_network_origin_metadata():
    """Network-originating events must include client_ip_hash, user_agent, protocol."""
    network_events = ["login_success", "login_failure", "logout"]
    network_fields = {"client_ip_hash", "user_agent", "protocol"}
    for event_type in network_events:
        event = generate_audit_event(event_type, is_network=True)
        origin = event.get("origin", {})
        missing = network_fields - set(origin.keys())
        assert not missing, f"Network event '{event_type}' missing fields: {missing}"
```

### T3 — Pseudonymization applied to IP and device_id

```python
def test_pseudonymization_applied():
    """client_ip_hash and device_id must not equal their raw inputs."""
    raw_ip = "192.168.1.42"
    raw_device = "DEVICE-SERIAL-001"
    event = generate_audit_event("login_success", is_network=True,
                                  raw_ip=raw_ip, raw_device=raw_device)
    origin = event["origin"]
    assert origin["client_ip_hash"] != raw_ip
    assert origin["device_id"] != raw_device
```

### T4 — Raw IP not in logs

```python
def test_raw_ip_not_in_audit_log():
    """Raw IP addresses must never appear in audit log output."""
    raw_ip = "203.0.113.99"
    event = generate_audit_event("login_failure", is_network=True, raw_ip=raw_ip)
    log_str = json.dumps(event)
    assert raw_ip not in log_str, "Raw IP address found in audit log"
```

### T5 — Prohibited fields not in logs

```python
def test_prohibited_fields_absent():
    """hostname, OS username, and hardware serial must not appear."""
    prohibited_patterns = ["hostname", "os_username", "serial_number"]
    event = generate_audit_event("login_success", is_network=True)
    for field in prohibited_patterns:
        assert field not in event.get("origin", {}), \
            f"Prohibited field '{field}' present in audit event origin"
```

### T6 — Non-network events omit network fields

```python
def test_non_network_events_omit_network_fields():
    """Background/local events must not include network-only fields."""
    event = generate_audit_event("mfa_enrollment", is_network=False)
    origin = event.get("origin", {})
    for field in ("client_ip_hash", "user_agent", "protocol"):
        assert field not in origin, \
            f"Non-network event unexpectedly contains '{field}'"
```

### T7 — Field consistency across event types

```python
def test_origin_field_names_consistent():
    """Field names must be identical across all event types."""
    events = [generate_audit_event(t) for t in ALL_EVENT_TYPES]
    base_keys = set(events[0]["origin"].keys())
    for event in events[1:]:
        event_keys = {k for k, v in event["origin"].items() if v is not None}
        # Core four must always be present
        assert {"actor_username", "session_id", "device_id", "app_instance_id"
                }.issubset(event_keys)
```

### T8 — Background task uses synthetic session_id

```python
def test_background_task_uses_system_session_id():
    """Background tasks that have no real session must use 'system' session_id."""
    event = generate_audit_event("scheduled_scan", is_network=False,
                                  is_background=True)
    assert event["origin"]["session_id"] == "system"
```

### T9 — Pseudonymization is stable (same input → same hash)

```python
def test_pseudonymization_is_stable():
    """Same raw value must always produce the same hash."""
    raw_ip = "10.0.0.1"
    hash_a = pseudonymize(raw_ip)
    hash_b = pseudonymize(raw_ip)
    assert hash_a == hash_b, "Pseudonymization is not deterministic"
```

---

## 8. Migration Steps

### Step 1 — Add origin metadata fields to the audit log schema

Add an `origin` JSON column (or sub-table) to the existing audit log table.
Required fields: `actor_username`, `session_id`, `device_id`,
`app_instance_id`. Network fields: `client_ip_hash`, `user_agent`,
`protocol`.

```sql
ALTER TABLE audit_log
  ADD COLUMN origin JSONB NOT NULL DEFAULT '{}'::jsonb;
```

### Step 2 — Deploy pseudonymization key to secret store

Generate a 256-bit key and store under `RFU_AUDIT_PSEUDONYMIZATION_KEY` in
the deployment secret store. This key MUST NOT be stored in source control
or application config files.

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Store output in your secret manager
```

### Step 3 — Backfill existing audit records

Existing records are exempt from the new fields per §16.X.7 (backward
compatibility). No migration of historical data is required. New writes
after deployment MUST comply with §16.X.

---

## 9. Cross-References

| Reference | Location |
|-----------|----------|
| Constitutional authority | §16.X.1–§16.X.7 |
| Session Management & Auditing base schema | §16 (constitution §16) |
| HMAC token events | §II.5.5 |
| is_protected blocked-op audit fields | §DW17.X.5, docs/is-protected-spec.md |
| Break-glass audit requirement | §18 (constitution) |
| Glossary: user-visible | §G.1 (constitution) |
| Reviewer checklist | .specify/memory/checklist-audit-origin-metadata-compliance.md |
| Round-8 Q14 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md §Q14 |
