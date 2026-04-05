from __future__ import annotations

import argparse
import json

from backend.app.config import get_settings
from backend.app.search_service import SearchService


INDEX_NAME = "doctype-kb-v1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Query doctype knowledge base.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--mode", choices=["simple", "semantic"], default="semantic")
    args = parser.parse_args()

    settings = get_settings()
    client = SearchService(settings).get_search_client(INDEX_NAME)

    kwargs = {
        "search_text": args.query,
        "top": args.top,
        "include_total_count": True,
    }
    if args.mode == "semantic":
        kwargs.update(
            {
                "query_type": "semantic",
                "semantic_configuration_name": "default",
                "query_caption": "extractive",
                "query_answer": "extractive",
            }
        )

    results = client.search(**kwargs)
    payload = []
    for item in results:
        payload.append(
            {
                "code": item.get("code"),
                "document_title": item.get("document_title"),
                "group_name": item.get("group_name"),
                "claim_types": item.get("claim_types", []),
                "score": item.get("@search.score"),
                "reranker_score": item.get("@search.reranker_score"),
            }
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

