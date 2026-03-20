# Post-Mortem: [Incident Title]

**Incident:** INC-YYYY-MM-DD-NNN  
**Date:** YYYY-MM-DD  
**Severity:** SEV-1/2/3  
**Duration:** HH:MM (start to full resolution)  
**Authors:** @engineer-lead, @engineer-support  
**Status:** Draft / Review / Final

## Executive Summary

One paragraph for executives: what happened, impact, root cause, resolution.

## Timeline (All Times UTC)

| Time | Event | Source |
|------|-------|--------|
| 16:42 | Alert fired: relay-us-east-1 error rate >50% | PagerDuty |
| 16:45 | On-call acknowledged | Slack |
| 16:50 | War room established | Zoom |
| 17:05 | Identified: memory leak in v1.2.3 stego pipeline | Logs |
| 17:15 | Decision: rollback to v1.2.2 | War room |
| 17:20 | Rollback initiated | kubectl |
| 17:35 | Error rates normalizing | Metrics |
| 18:00 | All health checks passing | Automated |
| 18:30 | Incident declared resolved | On-call |

## Impact Assessment

- **Customers affected:** 1,247 (12% of active base)
- **Messages failed:** 3,421 (0.8% of daily volume)
- **Data loss:** None (messages queued, delivered after recovery)
- **SLA violation:** 47 minutes of 99.9% uptime commitment

## Root Cause Analysis

### What Happened

Detailed technical description.

### Why It Happened

- **Proximate cause:** Buffer overflow in DCT coefficient calculation
- **Contributing factor:** Insufficient fuzzing of edge-case image dimensions
- **Systemic factor:** Pressure to release AI model v3 on schedule

### Five Whys

1. Why did the relay fail? → Memory exhaustion
2. Why did memory exhaust? → Unbounded buffer growth in DCT
3. Why was buffer unbounded? → Missing size check on non-8-aligned images
4. Why was check missing? → Test coverage gap for odd image dimensions
5. Why the gap? → Fuzzing corpus lacked sufficiently diverse sizes

## Lessons Learned

### What Went Well

- Automated rollback completed in 15 minutes
- Cross-region failover prevented total outage
- Customer communication was timely and accurate

### What Went Poorly

- Alert threshold too high (50% errors vs. 10% would have caught earlier)
- Memory leak not detected in staging (different image distribution)
- War room had difficulty accessing production logs (permission issue)

## Action Items

| ID | Action | Owner | Due | Priority |
|----|--------|-------|-----|----------|
| INC-001-1 | Add size check for non-aligned images in DCT | @dev-1 | 3 days | P0 |
| INC-001-2 | Expand fuzzing corpus with odd dimensions | @dev-2 | 1 week | P0 |
| INC-001-3 | Lower alert threshold to 10% error rate | @sre-1 | 2 days | P1 |
| INC-001-4 | Fix log access permissions for on-call | @sre-2 | 1 week | P1 |
| INC-001-5 | Review release criteria for model updates | @pm-1 | 2 weeks | P2 |

## Appendix

- Relevant logs: [link]
- Metrics dashboard: [link]
- Failing test case: [link to regression test]
- Related incidents: INC-2024-02-15-003 (similar memory issue)
