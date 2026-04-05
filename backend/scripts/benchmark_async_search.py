from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import time
from dataclasses import dataclass
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.search.documents.aio import SearchClient

from backend.app.config import get_settings


@dataclass
class RequestResult:
    latency_ms: float
    ok: bool
    count: int = 0
    returned: int = 0
    answers: int = 0
    error: str | None = None


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * pct
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return values[lower]
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def summarize(results: list[RequestResult], wall_time_s: float) -> dict[str, Any]:
    latencies = sorted(item.latency_ms for item in results if item.ok)
    errors = [item.error for item in results if not item.ok]
    total = len(results)
    success = total - len(errors)

    return {
        "total_requests": total,
        "successful_requests": success,
        "failed_requests": len(errors),
        "wall_time_ms": round(wall_time_s * 1000, 2),
        "throughput_rps": round(success / wall_time_s, 2) if wall_time_s and success else 0.0,
        "latency_ms": {
            "min": round(min(latencies), 2) if latencies else 0.0,
            "avg": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p50": round(percentile(latencies, 0.50), 2) if latencies else 0.0,
            "p95": round(percentile(latencies, 0.95), 2) if latencies else 0.0,
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
        "errors": errors[:5],
    }


async def one_search(
    client: SearchClient,
    semaphore: asyncio.Semaphore,
    *,
    query: str,
    top: int,
    mode: str,
) -> RequestResult:
    async with semaphore:
        start = time.perf_counter()
        try:
            kwargs: dict[str, Any] = {
                "search_text": query or "*",
                "top": top,
                "include_total_count": True,
            }
            if mode == "semantic":
                kwargs.update(
                    {
                        "query_type": "semantic",
                        "semantic_configuration_name": "default",
                        "query_caption": "extractive",
                        "query_answer": "extractive",
                    }
                )

            results = await client.search(**kwargs)
            items = [item async for item in results]
            latency_ms = (time.perf_counter() - start) * 1000
            count = await results.get_count() or 0
            answers = len(await results.get_answers() or []) if mode == "semantic" else 0
            return RequestResult(
                latency_ms=latency_ms,
                ok=True,
                count=count,
                returned=len(items),
                answers=answers,
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return RequestResult(latency_ms=latency_ms, ok=False, error=str(exc))


async def run_benchmark(
    *,
    query: str,
    mode: str,
    top: int,
    concurrency: int,
    requests: int,
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT chua duoc cau hinh.")

    credential: AzureKeyCredential | DefaultAzureCredential
    async_credential: DefaultAzureCredential | None = None
    if settings.api_key:
        credential = AzureKeyCredential(settings.api_key)
    else:
        async_credential = DefaultAzureCredential(
            interactive_browser_tenant_id=settings.tenant_id,
            shared_cache_tenant_id=settings.tenant_id,
        )
        credential = async_credential

    semaphore = asyncio.Semaphore(concurrency)
    async with SearchClient(
        endpoint=settings.search_endpoint,
        index_name=settings.index_name,
        credential=credential,
    ) as client:
        await one_search(client, semaphore, query=query, top=top, mode=mode)

        start = time.perf_counter()
        tasks = [
            asyncio.create_task(
                one_search(client, semaphore, query=query, top=top, mode=mode)
            )
            for _ in range(requests)
        ]
        results = await asyncio.gather(*tasks)
        wall_time_s = time.perf_counter() - start

    if async_credential is not None:
        await async_credential.close()

    sample = next((item for item in results if item.ok), None)
    summary = summarize(results, wall_time_s)
    summary["query"] = query
    summary["mode"] = mode
    summary["top"] = top
    summary["concurrency"] = concurrency
    if sample is not None:
        summary["sample_response"] = {
            "count": sample.count,
            "returned": sample.returned,
            "answers": sample.answers,
        }
    return summary


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Benchmark async Azure AI Search queries.")
    parser.add_argument("--query", default="Azure AI Search")
    parser.add_argument("--mode", choices=["simple", "semantic"], default="semantic")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()

    report = await run_benchmark(
        query=args.query,
        mode=args.mode,
        top=args.top,
        concurrency=args.concurrency,
        requests=args.requests,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main_async())
