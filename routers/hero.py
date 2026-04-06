
from fastapi import APIRouter, Depends, Query
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from typing import Annotated

from decorators.pointcut import role
from models.hero import Hero
from services.hero import HeroService


router = APIRouter(prefix="/hero", tags=["hero"])



@router.get("/", response_model=list[Hero])
@cache(expire=600)
async def get_heroes(
    service: HeroService = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    #
    response = service.read_heros(offset, limit)
    return response


@router.get("/{id}", response_model=Hero)
@cache(expire=600)
def get_hero(id: int, service: HeroService = Depends()):
    #
    response = service.read_hero(id)
    return response


@router.post("/add", response_model=Hero)
def add_hero(hero: Hero, service: HeroService = Depends()):
    #
    FastAPICache.clear()
    response = service.create_hero(hero)
    return response


@router.patch("/{id}", response_model=Hero)
@cache(expire=600)
def update_hero(id: int, hero: Hero, service: HeroService = Depends()):
    #
    response = service.update_hero(id, hero)
    return response


@router.delete("/{id}")
def delete_hero(id: int, service: HeroService = Depends()):
    #
    FastAPICache.clear()
    response = service.delete_hero(id)
    return response

