"""Small BM25 retriever implemented without external dependencies."""

from __future__ import annotations

import math
import re
from collections import Counter

from .documents import RetrievalDocument


TOKEN_RE = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


class BM25Retriever:
    def __init__(self, documents: list[RetrievalDocument], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize(f"{doc.title} {doc.text} {' '.join(doc.tags)}") for doc in documents]
        self.doc_freq: Counter[str] = Counter()
        for tokens in self.doc_tokens:
            self.doc_freq.update(set(tokens))
        self.avg_doc_len = sum(len(tokens) for tokens in self.doc_tokens) / max(len(self.doc_tokens), 1)

    def search(self, query: str, top_k: int = 5) -> list[tuple[RetrievalDocument, float]]:
        query_tokens = tokenize(query)
        scores: list[tuple[RetrievalDocument, float]] = []
        total_docs = len(self.documents)
        for doc, tokens in zip(self.documents, self.doc_tokens, strict=True):
            counts = Counter(tokens)
            score = 0.0
            doc_len = len(tokens) or 1
            for token in query_tokens:
                freq = counts[token]
                if not freq:
                    continue
                df = self.doc_freq[token]
                idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
                denom = freq + self.k1 * (1 - self.b + self.b * doc_len / max(self.avg_doc_len, 1))
                score += idf * (freq * (self.k1 + 1)) / denom
            if score > 0:
                scores.append((doc, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]

