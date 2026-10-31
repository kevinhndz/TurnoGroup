from pydantic import BaseModel, ConfigDict


class Revisar_Json_Plan(BaseModel):
    finanzas_habilitadas: bool
    model_config = ConfigDict(extra="forbid")
