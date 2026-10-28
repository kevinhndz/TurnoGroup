from typing import List, Generic, TypeVar

from pydantic import BaseModel

Caja = TypeVar("T")

class RespuestaPaginada(BaseModel, Generic[Caja]):
    
    total: int
    pagina_actual: int
    limite: int
    total_paginas: int
    
    data: List[Caja]