from __future__ import annotations

import re
from typing import Any

from app.services.kb_pipeline import embed_chunks


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[A-Za-z0-9]+", (text or "").lower()) if len(t) > 1}


def _lexical_overlap_score(query: str, content: str) -> float:
    q = _tokenize(query)
    if not q:
        return 0.0
    c = _tokenize(content)
    if not c:
        return 0.0
    return len(q.intersection(c)) / len(q)


async def retrieve_kb_context(
    *,
    conn: Any,
    kb_id: int,
    query: str,
    top_k: int = 4,
) -> list[dict[str, Any]]:
    query_embedding = (await embed_chunks([query]))[0]
    rows = await conn.fetch(
        """
        SELECT c.id, c.document_id, c.chunk_index, c.content,
               d.filename, d.file_type,
               (c.embedding <=> $2::vector) AS distance
        FROM kb_chunks c
        JOIN kb_documents d ON d.id = c.document_id
        WHERE c.kb_id = $1
        ORDER BY c.embedding <=> $2::vector ASC
        LIMIT $3
        """,
        kb_id,
        _vector_literal(query_embedding),
        max(1, top_k) * 3,
    )

    scored: list[dict[str, Any]] = []
    for row in rows:
        lexical = _lexical_overlap_score(query, row["content"] or "")
        distance = float(row["distance"] or 1.0)
        semantic = max(0.0, 1.0 - distance)
        final_score = semantic * 0.8 + lexical * 0.2
        scored.append(
            {
                "chunk_id": row["id"],
                "document_id": row["document_id"],
                "chunk_index": row["chunk_index"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "content": row["content"],
                "distance": distance,
                "semantic_score": semantic,
                "lexical_score": lexical,
                "score": final_score,
                "citation": f"{row['filename']}#chunk-{row['chunk_index']}",
            }
        )

    return sorted(scored, key=lambda item: float(item["score"]), reverse=True)[: max(1, top_k)]

