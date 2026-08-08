# ADR 0013: Durable live trace endpoint anchors

- Status: Accepted for frozen BASELINE-0017 evaluation
- Date: 2026-08-08

## Context

Public v0.0.16 gives every JSONL event canonical sequence and digest continuity, and completed evaluation reports bind their exact companion endpoint. Live API, MCP, and direct CLI trace files have no separately persisted endpoint after the process exits. A valid suffix deletion therefore remains a valid unanchored chain.

## Decision

Live runtime surfaces pass an explicit sibling path ending `.anchor.json` to `TraceWriter`. After each event append, the writer flushes and fsyncs the trace descriptor, builds a canonical `trace-anchor/v1` document containing only the trace schema, trace filename, event count, final event digest, and its own unkeyed digest, writes it through a securely created temporary file in the same directory, flushes and fsyncs that descriptor, closes it, and replaces the endpoint with `os.replace`.

Before resume, a nonempty live trace and its anchor must both exist and verify exactly. Missing, orphaned, malformed, mutated, wrong-file, stale, truncated, or extra-suffix states raise `TraceIntegrityError` before append. A trace-ahead-of-anchor failure is retained and blocked rather than silently repaired. Completed evaluations continue to use the report-held endpoint as their authoritative anchor.

## Consequences

This detects uncoordinated endpoint loss or mismatch and makes live resume fail closed. It can reduce availability after a crash between durable trace append and anchor replacement. The design claims only file flush/fsync and successful same-directory replacement semantics; it does not claim directory-entry durability.

The anchor is unkeyed and stored beside the trace. A writer with authority to replace both files can recompute both. This is not writer authentication, hostile-writer resistance, immutable storage, non-repudiation, a digital signature, or RFC conformance. No key, credential, dependency, service, collector, model, or real-infrastructure connection is added.
