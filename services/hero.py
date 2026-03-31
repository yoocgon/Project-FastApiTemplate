
from fastapi import Depends

from models.hero import Hero
from repositories.hero import HeroRepository


class HeroService:


    def __init__(self, hero_repo: HeroRepository = Depends()):
        self.hero_repo = hero_repo


    def create_hero(self, hero: Hero):
        #
        hero = self.hero_repo.create(hero)
        return hero


    def read_hero(self, id: int):
        #
        heros = self.hero_repo.read_id(id)
        return heros


    def read_heros(self, offset: int, limit: int):
        #
        heros = self.hero_repo.read_ragne(offset, limit)
        return heros


    def update_hero(self, id: int, hero: Hero):
        #
        hero = self.hero_repo.update(id, hero)
        return hero
    

    def delete_hero(self, id: int):
        #
        hero = self.hero_repo.delete(id)
        #
        if hero:
             result = "ok"
        else:
             result = "There's no matched Hero"
        #
        return {
            "result": result, 
            "hero": hero
        }
