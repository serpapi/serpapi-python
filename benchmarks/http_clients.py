"""Compare sequential requests with concurrent SerpApi AsyncClient calls.

The benchmark uses a local delayed HTTP server. It measures client-side
concurrency without consuming SerpApi searches or introducing internet and API
server variance.
"""

import argparse
import asyncio
import json
import statistics
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

import serpapi


class DelayedJSONHandler(BaseHTTPRequestHandler):
    delay = 0.05

    def do_GET(self):
        time.sleep(self.delay)
        payload = json.dumps({"search_metadata": {"status": "Success"}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass


@contextmanager
def delayed_server(delay):
    DelayedJSONHandler.delay = delay
    server = ThreadingHTTPServer(("127.0.0.1", 0), DelayedJSONHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def measure_requests(base_url, count):
    session = requests.Session()
    session.trust_env = False
    try:
        started = time.perf_counter()
        for _ in range(count):
            response = session.get(f"{base_url}/search", timeout=10)
            response.raise_for_status()
        return time.perf_counter() - started
    finally:
        session.close()


def measure_sync_client(base_url, count):
    client = serpapi.Client(trust_env=False, timeout=10)
    client.BASE_DOMAIN = base_url
    try:
        started = time.perf_counter()
        for index in range(count):
            client.search(q=f"query-{index}")
        return time.perf_counter() - started
    finally:
        client.close()


async def measure_async_client(base_url, count):
    client = serpapi.AsyncClient(trust_env=False, timeout=10)
    async with client:
        client.BASE_DOMAIN = base_url
        started = time.perf_counter()
        await asyncio.gather(
            *(client.search(q=f"query-{index}") for index in range(count))
        )
        return time.perf_counter() - started


def summarize(label, timings):
    median = statistics.median(timings)
    spread = f"{min(timings):.3f}-{max(timings):.3f}s"
    print(f"{label:<29} {median:.3f}s median ({spread})")
    return median


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.delay < 0:
        parser.error("--delay must not be negative")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    with delayed_server(args.delay) as base_url:
        requests_timings = [
            measure_requests(base_url, args.count) for _ in range(args.repeats)
        ]
        sync_timings = [
            measure_sync_client(base_url, args.count) for _ in range(args.repeats)
        ]
        async_timings = [
            asyncio.run(measure_async_client(base_url, args.count))
            for _ in range(args.repeats)
        ]

    summarize("requests.Session sequential:", requests_timings)
    sync_median = summarize("serpapi.Client sequential:", sync_timings)
    async_median = summarize("AsyncClient concurrent:", async_timings)
    print(f"async vs sync speedup:       {sync_median / async_median:.2f}x")


if __name__ == "__main__":
    main()
