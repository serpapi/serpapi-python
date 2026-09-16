# HTTP client benchmark

This benchmark compares the previous `requests.Session` transport, the
synchronous HTTPX-backed `serpapi.Client`, and concurrent
`serpapi.AsyncClient` calls.

It runs against a local threaded server with a configurable response delay, so
it does not need an API key, consume searches, or mix client behavior with
internet and SerpApi server variance.

From the repository root, run:

```bash
uv run --with requests python benchmarks/http_clients.py
```

Or install the development package and benchmark-only dependency with pip:

```bash
pip3 install -e . requests
python benchmarks/http_clients.py
```

Each result is the median of three runs and includes the observed range. Client
construction and shutdown are excluded consistently. Change the workload with
`--count`, `--delay`, and `--repeats`. For example:

```bash
uv run --with requests python benchmarks/http_clients.py --count 50 --delay 0.1 --repeats 5
```

The sequential `requests` and HTTPX results show transport overhead under the
same workload. The async result demonstrates throughput when independent
I/O-bound calls overlap; it does not claim that one SerpApi search becomes
faster.
