from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar
from fastapi import Query

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Every list endpoint returns this shape:
        {
            "items": [...],
            "total": 42,
            "skip": 0,
            "limit": 20,
            "has_more": true
        }

    Usage in a router:
        @router.get("/", response_model=Page[NodeTypeResponse])
        def list_node_types(params: PaginationParams = Depends(), db: Session = Depends(get_db)):
            items, total = crud.node_type.get_page(db, skip=params.skip, limit=params.limit)
            return Page.create(items, total, params)
    """

    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def create(
        cls, items: List[T], total: int, params: "PaginationParams"
    ) -> "Page[T]":
        return cls(
            items=items,
            total=total,
            skip=params.skip,
            limit=params.limit,
            has_more=(params.skip + len(items)) < total,
        )

    model_config = ConfigDict(from_attributes=True)


class PaginationParams:
    """
    Shared dependency for skip/limit query parameters.
    Use with Depends() in any list endpoint.

    Usage:
        def list_items(params: PaginationParams = Depends()):
            ...
    """

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(
            default=20, ge=1, le=200, description="Max records to return"
        ),
    ):
        self.skip = skip
        self.limit = limit
