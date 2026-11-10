"""Small, inspectable TF-IDF vector-based policy retrieval, with provenance.

This is an illustrative in-memory vector index, not a distributed production KB.
"""
from __future__ import annotations
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STOP = {"the", "and", "of", "for", "with", "in", "a", "to", "on", "is", "an", "as", "by", "that", "from", "at", "or", "are", "use", "using"}


def terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[^\W_]+", text.lower(), re.UNICODE) if len(w) >= 2 and w not in STOP]


class PolicyKnowledgeBase:
    def __init__(self, records: list[dict[str, Any]]):
        self.records = records
        self.doc_terms: list[Counter] = []
        for record in records:
            blob = " ".join([record["title"], record["summary"], " ".join(record["tags"]), record["scope"]])
            self.doc_terms.append(Counter(terms(blob)))
        df = Counter(token for count in self.doc_terms for token in count)
        self.idf = {token: math.log((len(records) + 1) / (freq + 1)) + 1 for token, freq in df.items()}
        self.vectors = [self._unit_vector(tf) for tf in self.doc_terms]

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> "PolicyKnowledgeBase":
        source = Path(path) if path else ROOT / "data" / "policies.json"
        return cls(json.loads(source.read_text(encoding="utf-8")))

    def _unit_vector(self, tf: Counter) -> dict[str, float]:
        values = {word: (1 + math.log(count)) * self.idf.get(word, 0) for word, count in tf.items()}
        norm = math.sqrt(sum(v * v for v in values.values())) or 1
        return {k: v / norm for k, v in values.items()}

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query_vector = self._unit_vector(Counter(terms(query)))
        results = []
        for record, vector in zip(self.records, self.vectors):
            score = sum(value * vector.get(word, 0) for word, value in query_vector.items())
            if score > 0:
                results.append({**record, "score": round(score, 4)})
        results.sort(key=lambda item: (-item["score"], item["id"]))
        return results[:max(0, limit)]

    def by_id(self, id_: str) -> dict[str, Any] | None:
        return next((x for x in self.records if x["id"] == id_), None)
