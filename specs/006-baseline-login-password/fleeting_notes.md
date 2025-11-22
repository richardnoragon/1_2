# Fleeting Notes — Login & Password Baseline (006)

## Phase 3.5 Domain Services Snapshot

- Argon2id helper `src/core/auth/security/password_hasher.py` now backs AuthService, RegistrationService, and admin workflows; the legacy shim simply proxies to the new implementation. Lockout policy wiring in `AuthService` emits warnings after 3+ failures and resets state on success, satisfying FR-002 alerts.
- Session/admin orchestration services (`session_service.py`, `admin_approval_service.py`, `admin_account_service.py`) remain stable after a light audit—no new issues surfaced while integrating the new security helpers.
- Preference recovery handling landed in `src/core/preferences/services/preference_recovery_service.py`; it bootstraps defaults when a profile is missing, files a `PendingPreferenceAlert`, and records `AdminActionType.PREFERENCE_RECOVERY` audit metadata for operators.
- MFA placeholder service now logs every attempted operation with structured context before raising the `501` scaffold error so ops can measure pre-launch curiosity per `mfa-readiness.md`.
- Pending registration dispatcher `src/core/auth/services/pending_registration_dispatcher.py` now records JSONL telemetry for queue depth + previews, and `RegistrationService` wires it as the default notification hook when no custom dispatcher is supplied.
- Identity fixtures expose `seed_mfa_enabled_user` and `mfa_recovery_code_record`, covering the MFA columns and the new `user_mfa_recovery_codes` table for upcoming FR-013 validation.

## Follow-ups / Open Items

1. **Testing debt**: implement T073–T075 once the new services settle (password hasher + lockout policy + preference recovery unit coverage).
2. **Controller/CLI wiring**: ensure upcoming T058–T072 tasks inject `db_path` + dependency container hooks so controllers/CLI reuse the new services without bespoke SQL.
3. **Alert routing**: Preference recovery hooks currently log + audit; decide during T063/T085 whether to fan out notifications (email/Teams) once admin panel wiring is live.
4. **Secure secret dispatcher**: Admin reset flow still prints secrets directly; defer to T080 for dispatcher integration so MFA storage/enrollment can share the delivery path.
5. **Telemetry surfacing**: Pending registration telemetry lives under `reports/telemetry/`; add admin panel surfacing or ops alerts once T080 finalizes dispatcher hardening.
