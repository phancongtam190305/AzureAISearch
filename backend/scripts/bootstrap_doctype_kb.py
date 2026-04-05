from __future__ import annotations

import json
from pathlib import Path

from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
)

from backend.app.config import get_settings
from backend.app.search_service import SearchService


INDEX_NAME = "doctype-kb-v1"


def build_index(index_name: str) -> SearchIndex:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SimpleField(name="code", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="document_title", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="file_name", type=SearchFieldDataType.String),
        SearchableField(name="group_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(
            name="claim_types",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            searchable=True,
            filterable=True,
            facetable=True,
        ),
        SearchableField(name="purpose_description", type=SearchFieldDataType.String),
        SearchField(
            name="key_sections",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            searchable=True,
            filterable=False,
            facetable=False,
        ),
        SearchableField(name="notes_requirements", type=SearchFieldDataType.String),
        SearchableField(name="search_text", type=SearchFieldDataType.String),
    ]

    semantic = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="default",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="document_title"),
                    content_fields=[
                        SemanticField(field_name="purpose_description"),
                        SemanticField(field_name="search_text"),
                    ],
                    keywords_fields=[
                        SemanticField(field_name="code"),
                        SemanticField(field_name="group_name"),
                        SemanticField(field_name="claim_types"),
                    ],
                ),
            )
        ]
    )

    return SearchIndex(name=index_name, fields=fields, semantic_search=semantic)


def main() -> None:
    settings = get_settings()
    if not settings.search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT chua duoc cau hinh.")

    service = SearchService(settings)
    index_client = service.get_index_client()
    search_client = service.get_search_client(INDEX_NAME)
    index = build_index(INDEX_NAME)

    try:
        index_client.delete_index(INDEX_NAME)
    except ResourceNotFoundError:
        pass

    index_client.create_index(index)

    data_path = settings.project_root / "data" / "doctype-catalog.json"
    documents = json.loads(data_path.read_text(encoding="utf-8"))
    result = search_client.upload_documents(documents=documents)
    succeeded = sum(1 for item in result if item.succeeded)
    print(f"Uploaded {succeeded}/{len(documents)} documents into index '{INDEX_NAME}'.")


if __name__ == "__main__":
    main()
