from __future__ import annotations

from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

from .config import Settings


class SearchService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _build_credential(self) -> AzureKeyCredential | DefaultAzureCredential:
        if self.settings.api_key:
            return AzureKeyCredential(self.settings.api_key)

        if not self.settings.use_rbac:
            raise ValueError("Khong tim thay AZURE_SEARCH_API_KEY va AZURE_USE_RBAC dang tat.")

        return DefaultAzureCredential(
            interactive_browser_tenant_id=self.settings.tenant_id,
            shared_cache_tenant_id=self.settings.tenant_id,
        )

    def get_search_client(self, index_name: str | None = None) -> SearchClient:
        return SearchClient(
            endpoint=self.settings.search_endpoint,
            index_name=index_name or self.settings.index_name,
            credential=self._build_credential(),
        )

    def get_index_client(self) -> SearchIndexClient:
        return SearchIndexClient(
            endpoint=self.settings.search_endpoint,
            credential=self._build_credential(),
        )

    def search(
        self,
        query: str,
        *,
        top: int = 5,
        mode: str = "semantic",
    ) -> dict[str, Any]:
        client = self.get_search_client()
        use_semantic = mode == "semantic"
        kwargs: dict[str, Any] = {
            "search_text": query or "*",
            "top": top,
            "include_total_count": True,
        }

        if use_semantic:
            kwargs.update(
                {
                    "query_type": "semantic",
                    "semantic_configuration_name": "default",
                    "query_caption": "extractive",
                    "query_answer": "extractive",
                }
            )

        results = client.search(**kwargs)
        payload = {
            "mode": mode,
            "count": results.get_count(),
            "answers": [],
            "items": [],
        }

        if use_semantic:
            payload["answers"] = [
                {
                    "text": answer.text,
                    "highlights": getattr(answer, "highlights", None),
                    "score": answer.score,
                }
                for answer in results.get_answers() or []
            ]

        for item in results:
            captions = []
            if use_semantic:
                captions = [
                    {
                        "text": caption.text,
                        "highlights": getattr(caption, "highlights", None),
                    }
                    for caption in item.get("@search.captions", [])
                ]

            payload["items"].append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": item.get("category"),
                    "content": item.get("content"),
                    "tags": item.get("tags", []),
                    "url": item.get("url"),
                    "score": item.get("@search.score"),
                    "reranker_score": item.get("@search.reranker_score"),
                    "captions": captions,
                }
            )

        return payload
