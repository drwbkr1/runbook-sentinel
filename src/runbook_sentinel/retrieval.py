from __future__ import annotations

import re


TOKEN_RE = re.compile(r"[a-z0-9_]+")
FULL_RETRIEVED_CONTEXT = "full-retrieved-context-v1"
EVIDENCE_ONLY_CONTEXT = "evidence-only-context-v2"
DEFAULT_DECISION_CONTEXT = EVIDENCE_ONLY_CONTEXT
DECISION_CONTEXT_CONFIGURATIONS = (FULL_RETRIEVED_CONTEXT, EVIDENCE_ONLY_CONTEXT)


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


class LexicalRetriever:
    """Deterministic lexical control retriever retained for baseline-0002."""

    name = "lexical-token-overlap-v1"

    def retrieve(self, query: str, documents: list[dict], limit: int = 4) -> list[dict]:
        query_tokens = _tokens(query)
        ranked: list[tuple[float, str, dict]] = []
        for document in documents:
            document_tokens = _tokens(document.get("content", "")) | _tokens(document.get("title", ""))
            overlap = len(query_tokens & document_tokens)
            coverage = overlap / max(1, len(query_tokens))
            kind_bonus = 0.05 if document.get("kind") == "telemetry" else 0.0
            ranked.append((coverage + kind_bonus, document["id"], document))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [document for score, _, document in ranked[:limit] if score > 0]


def select_decision_documents(configuration: str, retrieved_documents: list[dict]) -> list[dict]:
    if configuration == FULL_RETRIEVED_CONTEXT:
        return list(retrieved_documents)
    if configuration == EVIDENCE_ONLY_CONTEXT:
        return [
            document
            for document in retrieved_documents
            if document.get("kind") in {"telemetry", "status"}
        ]
    raise ValueError(f"Unknown decision context configuration: {configuration}")
