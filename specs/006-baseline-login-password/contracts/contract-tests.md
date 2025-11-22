# Contract Test Matrix (Failing-first Guidance)

These tests will live under `tests/contracts/identity/` once implemented. For now they describe the required failing scenarios so the `/tasks` phase can produce granular work items.

| Test File                         | Scenario                                                                | Expected Initial State                   | Failure Condition                                                              |
| --------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------ |
| `test_login_success.py`           | Happy-path login returns session + preferences                          | Existing active user with valid password | Test must fail until AuthService returns session payload shaped like contract. |
| `test_login_lockout.py`           | 5 failed attempts block account                                         | User has `login_attempts=4`              | Test fails until lockout + audit logging triggered at 5th failure.             |
| `test_logout_revokes_token.py`    | DELETE /auth/login invalidates session                                  | Valid session token available            | Test fails until SessionStore revokes tokens and respond 204.                  |
| `test_admin_approve_user.py`      | Approving pending account moves status to active and spawns preferences | Pending account exists                   | Test fails until admin endpoint finalizes transitions.                         |
| `test_admin_reset_password.py`    | Reset returns temporary password and audit entry                        | Active user exists                       | Test fails until admin reset flow emits temporary password & logs action.      |
| `test_preferences_share_guard.py` | Sharing disabled unless flag set                                        | `share_preferences=false`                | Test fails until endpoint rejects exports for disabled users.                  |

Create each test as a pytest module performing contract-level HTTP/client simulation (can call service layer directly). Mark them with `@pytest.mark.contract` and do **not** stub missing implementations—let them fail naturally to respect TDD gates.
