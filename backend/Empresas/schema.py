from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict



class Revisar_Json_Nueva_Empresa (BaseModel):

   nombre : str = Field(min_length= 4, max_length= 45)
   tipo_negocio : str = Field(min_length= 5, max_length=35)
   codigo_pais : str = Field(min_length=2, max_length= 5)
   zona_horaria : str = Field(min_length= 4, max_length= 45)
   codigo_moneda: str = Field(min_length=2, max_length= 5)


class NuevaEmpresaRespuesta (Revisar_Json_Nueva_Empresa):
       
       id: int
       nombre : str = Field(min_length= 4, max_length= 45)
       codigo_moneda: str = Field(min_length=2, max_length= 5)
       estado : str
       fecha_registro: datetime

       # Permite leer los campos del objeto Empresas devuelto por SQLAlchemy.
       model_config = ConfigDict(from_attributes=True)
       

