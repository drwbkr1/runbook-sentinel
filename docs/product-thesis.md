# Product thesis

Runbook Sentinel tests one thesis: a retrieval-grounded SRE incident agent can remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

The system is useful when it makes the best bounded disposition supported by current evidence: diagnose, request specific missing evidence, propose an allowlisted synthetic action, or abstain. A correct request or abstention is a successful outcome when action would be underdetermined.

The system is repeatable when frozen inputs and configuration produce measured, retained results across repeated trials. The system is policy-compliant when no model output can bypass deterministic authorization, capability, approval, idempotency, replay, precondition, or postcondition controls.

Runbook Sentinel is research-informed. It is not production incident automation, a security guarantee, or an autonomous remediation service.
