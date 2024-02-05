from typing import Annotated

from fastapi import Query, Depends, APIRouter
from sqlalchemy import select, update, insert, delete  # noqa
from sqlalchemy.ext.asyncio import AsyncSession

from db import async_session
from models import Trees
from pagination import Page, Pagination
from response import OK, R, ApiException, ERROR
from schemas import TreeSchema, Item

data_api = APIRouter(prefix="/tree", tags=["管理树木实体"])


@data_api.get("/q", response_model=Page[TreeSchema], summary="条件查询树木")
async def query_trees(
    energy: Annotated[int, Query(ge=0)],
    s: Annotated[AsyncSession, Depends(async_session)],
    pagination: Annotated[Pagination, Depends()],
):
    if energy == 0:
        raise ApiException(ERROR.excinfo("demo error"))
    qs = select(Trees).where(Trees.energy >= energy).order_by("id")
    return await Page.create(s, qs, pagination)


@data_api.get("/{id}", response_model=R[TreeSchema], response_model_by_alias=False, summary="查询单个树木")
async def query_tree(
    id: int,
    s: Annotated[AsyncSession, Depends(async_session)],
):
    qs = select(Trees).where(Trees.id == id)
    return OK(await s.scalar(qs))


@data_api.post("/update", summary="更新单个树木信息")
async def update_tree(
    item: Item,
    s: Annotated[AsyncSession, Depends(async_session)],
):
    qs = update(Trees).where(Trees.id == item.id).values(energy=item.energy)
    await s.execute(qs)
    await s.commit()
    return OK({"id": item.id})

    # return OK(obj)
    # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)
