from __future__ import annotations

import re


TOKEN_RE = re.compile(r"[a-z0-9_]+")


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
