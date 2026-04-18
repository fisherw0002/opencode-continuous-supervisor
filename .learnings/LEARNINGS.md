
## [LRN-20260418-G2A] correction

**Logged**: 2026-04-18T15:38:21.251327+00:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Do not conclude G2A accounts are blocked solely from one 403 upstream response when the user says all G2A accounts are normal.

### Details
Initial diagnosis overfit a single upstream error (`blocked-user`). In a gateway/proxy setup like G2A, that can also mean route-level failure, a bad upstream pool member, model-route mismatch, or provider-side policy on one backend path. User corrected that all accounts are normal, so future diagnosis should verify multiple models/routes before attributing it to account state.

### Suggested Action
Test multiple G2A models/routes and inspect gateway behavior before blaming account status.

### Metadata
- Source: user_feedback
- Related Files: skills/g2a-media/SKILL.md
- Tags: g2a, diagnosis, correction

---
