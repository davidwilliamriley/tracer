#!/usr/bin/env python3
import requests

# Login
r = requests.post(
    "http://127.0.0.1:8000/auth/token",
    data={"username": "admin", "password": "change-me"},
)
if r.status_code != 200:
    print(f"Auth failed: {r.status_code} {r.text}")
    exit(1)

token = r.json()["access_token"]

# Check node types
r = requests.get(
    "http://127.0.0.1:8000/node-types/?limit=500",
    headers={"Authorization": f"Bearer {token}"},
)
data = r.json()
if isinstance(data, dict) and "items" in data:
    items = data["items"]
    total = data.get("total", len(items))
else:
    items = data if isinstance(data, list) else []
    total = len(items)

print(f"Node types in database: {total}")
for nt in items[:5]:
    print(f"  - {nt['node_type_identifier']}")
