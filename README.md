## Network Route Optimizer 

This is a small Django + DRF service that models a directed, weighted network graph (nodes + edges), computes the shortest route between two nodes (Dijkstra), and stores a query history.

I kept the code intentionally straightforward and test-first

### Quick start

#### 1) Setup

```bash
python -m pip install -r requirements.txt
python manage.py migrate
```

#### 2) Run locally

```bash
python manage.py runserver
```

Useful links:
- `GET /health/`
- `GET /api/docs/` (Swagger UI)
- `GET /api/schema/` (OpenAPI schema)

#### 3) Run tests

```bash
python manage.py test apps.network
```

### API (as per the exercise spec)

All endpoints are mounted at the root to match the spec exactly.

#### 1) Add node

- **POST** `/nodes`

Request body:

```json
{ "name": "ServerA" }
```

Response (201):

```json
{ "id": 1, "name": "ServerA" }
```

Errors:
- `400`: name missing or duplicate

Also available:
- **GET** `/nodes` → list all nodes (returns `{ "nodes": [...] }`)
- **DELETE** `/nodes/{id}` → delete node (`204`, or `404` if not found)

#### 2) Add edge

- **POST** `/edges`

Request body:

```json
{ "source": "ServerA", "destination": "ServerB", "latency": 12.5 }
```

Response (201):

```json
{ "id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5 }
```

Errors:
- `400`: source/destination missing
- `400`: latency ≤ 0
- `400`: duplicate edge
- `400`: nodes not found

Also available:
- **GET** `/edges` → list all edges (returns `{ "edges": [...] }`)
- **DELETE** `/edges/{id}` → delete edge (`204`, or `404` if not found)

#### 3) Get shortest route

- **POST** `/routes/shortest`

Request body:

```json
{ "source": "ServerA", "destination": "ServerD" }
```

Response (200, path exists):

```json
{ "total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"] }
```

Response (404, no path):

```json
{ "error": "No path exists between ServerA and ServerD" }
```

Errors:
- `400`: invalid or non-existent nodes

#### 4) Get route query history

- **GET** `/routes/history`

Query params (optional):
- `source`
- `destination`
- `limit`
- `date_from` / `date_to` (ISO timestamps)

Response (200):

```json
[
  {
    "id": 1,
    "source": "ServerA",
    "destination": "ServerD",
    "total_latency": 23.4,
    "path": ["ServerA", "ServerB", "ServerD"],
    "created_at": "2026-02-20T14:32:00Z"
  }
]
```

### Notes / design choices

- **Shortest path**: Dijkstra with a min-heap (`heapq`). If multiple shortest paths have the same total latency, the implementation returns a deterministic result by picking the lexicographically smallest path.
- **History**: every successful `/routes/shortest` call is persisted as a `RouteQuery` row and returned via `/routes/history`.
- **Error responses**: DRF exception handler normalizes errors into `{ "error": ... }`.

### Additional implementation notes

- **Swagger/OpenAPI** at `GET /api/docs/` and `GET /api/schema/`
- **Test coverage** for models, APIs, and shortest-path behavior
- **Maintainable structure**: serializers + service layer

