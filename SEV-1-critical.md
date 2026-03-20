# SEV-1: Critical Incident Response

**Definition:** Service unavailable, active security breach, or imminent data loss.

**Response Time:** 5 minutes to acknowledge, 15 minutes to initial mitigation.

**Communication:** War room within 10 minutes, customer notice within 1 hour.

## Immediate Actions (First 5 Minutes)

### 1. Page On-Call

```bash
# Automated via PagerDuty/Opsgenie
# Manual override:
aegis-incident page --severity 1 --component all \
  --message "SEV-1: [brief description]"
```

### 2. Establish War Room

```bash
# Create dedicated Slack channel + Zoom
aegis-incident war-room --incident INC-YYYY-MM-DD-NNN
# Outputs: #incident-2024-03-19-001, zoom link, bridge number
```

### 3. Assess Scope

Run diagnostic script:
```bash
./scripts/incident-assess.sh
```

Outputs:
- Affected regions
- Customer impact count
- Last known good commit
- Recent deployments

## Decision Tree

```
Is there evidence of unauthorized access?
├── YES → Execute suspected-breach playbook
│         AND activate kill switch
│
└── NO → Is service down?
          ├── YES → Check: Recent deploy? Infrastructure failure?
          │         ├── Deploy → Rollback immediately
          │         └── Infra → Failover to standby region
          │
          └── NO → Performance degradation?
                    ├── YES → Enable circuit breakers, shed load
                    └── NO → False positive? Downgrade to SEV-2
```

## Kill Switch Activation

**When to activate:**
- Confirmed or suspected key compromise
- Model poisoning detected
- Supply chain compromise
- Ransomware in production

**Procedure:**

```bash
# Requires 2-of-3 on-call approval
aegis-killswitch activate \
  --reason "Suspected key compromise: anomalous HSM access from unknown IP" \
  --approvers oncall-primary,oncall-secondary
```

Effects:
- All relays reject new connections (drain in-flight)
- HSM keys locked (require physical ceremony to unlock)
- Global mode: MAINTENANCE
- Customer notification: "Scheduled security maintenance"

## Communication Templates

### Internal (Slack #incident-XXX)

```
[SEV-1] INC-2024-03-19-001: [One-line summary]
Impact: [regions] | [X] customers | [Y]% message failure rate
Status: [INVESTIGATING/MITIGATING/MONITORING/RESOLVED]
Lead: @engineer-name

Timeline:
- 16:42 UTC: Alert fired ([link])
- 16:45 UTC: War room established
- 16:50 UTC: [Action taken]

Updates every 15 minutes or on status change.
```

### External (status page + email)

```
AegisBloom Security Maintenance

We are performing unscheduled security maintenance.
Message sending and receiving may be unavailable.

ETA: 2 hours
Updates: https://status.aegisbloom.io/incidents/XXX

We apologize for the inconvenience.
```

## Recovery Verification

Before resolving:
- [ ] All health checks passing for 10 minutes
- [ ] Test message roundtrip verified in each region
- [ ] No anomalous metrics (error rate, latency)
- [ ] Post-mortem scheduled within 24 hours
- [ ] Customer all-clear notification sent

```bash
aegis-incident resolve INC-2024-03-19-001 \
  --resolution "Rolled back to v1.2.2, root cause: memory leak in v1.2.3" \
  --postmortem-scheduled "2024-03-20 14:00 UTC"
```
