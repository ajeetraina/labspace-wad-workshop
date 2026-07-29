"""
Catalog MCP server.

Exposes the Product Catalog database as tools an AI agent can call.

This is deliberately small. The point of Lab 6 is not the server's cleverness —
it is that this process holds a database credential, is reachable by an agent,
and is software you pulled from somewhere. Everything the workshop taught you
about the catalog API image applies to this file's image too.
"""

import os

import psycopg
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("catalog")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgres://postgres:postgres@postgres:5432/catalog",
)


def _query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a read-only query and return rows as dicts."""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description is None:
                return []
            columns = [c.name for c in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


@mcp.tool()
def list_products(limit: int = 20) -> list[dict]:
    """List products in the catalog, most recently added first."""
    limit = max(1, min(limit, 100))
    return _query(
        "SELECT id, name, price, upc FROM products ORDER BY id DESC LIMIT %s",
        (limit,),
    )


@mcp.tool()
def search_products(term: str, limit: int = 20) -> list[dict]:
    """Search products by name. Case-insensitive substring match."""
    limit = max(1, min(limit, 100))
    return _query(
        "SELECT id, name, price, upc FROM products "
        "WHERE name ILIKE %s ORDER BY name LIMIT %s",
        (f"%{term}%", limit),
    )


@mcp.tool()
def get_product(product_id: int) -> dict | None:
    """Fetch a single product by its numeric id."""
    rows = _query(
        "SELECT id, name, price, upc FROM products WHERE id = %s",
        (product_id,),
    )
    return rows[0] if rows else None


if __name__ == "__main__":
    mcp.run()
