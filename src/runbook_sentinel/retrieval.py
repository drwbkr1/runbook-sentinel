from __future__ import annotations

import re


TOKEN_RE = re.compile(r"[a-z0-9_]+")
FULL_RETRIEVED_CONTEXT = "full-retrieved-context-v1"
EVIDENCE_ONLY_CONTEXT = "evidence-only-context-v2"
DEFAULT_DECISION_CONTEXT = EVIDENCE_ONLY_CONTEXT
DECISION_CONTEXT_CONFIGURATIONS = (FULL_RETRIEVED_CONTEXT, EVIDENCE_ONLY_CONTEXT)
LEXICAL_RETRIEVER_V1 = "lexical-token-overlap-v1"
EVIDENCE_PRIORITY_RETRIEVER_V2 = "evidence-priority-lexical-v2"
DEFAULT_RETRIEVAL_CONFIGURATION = EVIDENCE_PRIORITY_RETRIEVER_V2
RETRIEVAL_CONFIGURATIONS = (LEXICAL_RETRIEVER_V1, EVIDENCE_PRIORITY_RETRIEVER_V2)
PROJECT_EVIDENCE_KINDS = {"telemetry", "status"}


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


class LexicalRetriever:
    """Deterministic lexical retriever with a retained v1 comparison mode."""

    def __init__(self, configuration: str = DEFAULT_RETRIEVAL_CONFIGURATION):
        if configuration not in RETRIEVAL_CONFIGURATIONS:
            raise ValueError(f"Unknown retrieval configuration: {configuration}")
        self.name = configuration

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
        eligible = [item for item in ranked if item[0] > 0]
        if self.name == LEXICAL_RETRIEVER_V1:
            return [document for _, _, document in eligible[:limit]]
        project_evidence = [
            item for item in eligible if item[2].get("kind") in PROJECT_EVIDENCE_KINDS
        ]
        untrusted_guidance = [
            item for item in eligible if item[2].get("kind") not in PROJECT_EVIDENCE_KINDS
        ]
        prioritized = project_evidence + untrusted_guidance
        return [document for _, _, document in prioritized[:limit]]


def select_decision_documents(configuration: str, retrieved_documents: list[dict]) -> list[dict]:
    if configuration == FULL_RETRIEVED_CONTEXT:
        return list(retrieved_documents)
    if configuration == EVIDENCE_ONLY_CONTEXT:
        return [
            document
            for document in retrieved_documents
            if document.get("kind") in PROJECT_EVIDENCE_KINDS
        ]
    raise ValueError(f"Unknown decision context configuration: {configuration}")
