from __future__ import annotations

import json

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


def build_index(index_name: str) -> SearchIndex:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="tags",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            searchable=True,
            filterable=True,
            facetable=True,
        ),
        SimpleField(name="url", type=SearchFieldDataType.String),
    ]

    semantic = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="default",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                    keywords_fields=[SemanticField(field_name="tags"), SemanticField(field_name="category")],
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
    search_client = service.get_search_client()
    index = build_index(settings.index_name)

    try:
        index_client.delete_index(settings.index_name)
    except ResourceNotFoundError:
        pass

    index_client.create_index(index)

    data_path = settings.project_root / "data" / "sample-docs.json"
    documents = json.loads(data_path.read_text(encoding="utf-8"))
    result = search_client.upload_documents(documents=documents)
    succeeded = sum(1 for item in result if item.succeeded)
    print(f"Uploaded {succeeded}/{len(documents)} documents into index '{settings.index_name}'.")


if __name__ == "__main__":
    main()
