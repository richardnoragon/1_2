# Merge Branches Into `master` — Tracking Checklist

Purpose: Track the status of merging all project branches into `master` in this order:

1. `001-refactor-the-multi`
2. `003-use-docs-centralized`
3. `006-baseline-login-password`
4. `007-upgrade-to-login` (must be last)

## Checklist

- [x] 1. Verify clean working tree ✅ (verified 2025-12-14 — working tree is clean)
- [x] 2. Fetch and update local refs ✅ (fetched 2025-12-14 — all 4 branches verified: 001, 003, 006, 007 + master)
- [ ] 3. Checkout and update `master`
- [ ] 4. Merge `001-refactor-the-multi`
- [ ] 5. Merge `003-use-docs-centralized`
- [ ] 6. Merge `006-baseline-login-password`
- [ ] 7. Merge `007-upgrade-to-login` (last)
- [ ] 8. Run tests and quick sanity checks
- [ ] 9. Push updated `master` to `origin`
- [ ] 10. Post-merge cleanup and optional tag

## Notes

- If a merge conflict occurs, resolve it, then run `git add -A` and complete the merge commit.
- After the final merge, verify that `master` reflects all changes from `007-upgrade-to-login` (especially anything under `specs/007-upgrade-to-login`).

## Fleeting Notes

- **2025-12-14**: Git warning — "There are too many unreachable loose objects; run 'git prune' to remove them." Consider running `git gc` or `git prune` after the merge process is complete (non-blocking).
