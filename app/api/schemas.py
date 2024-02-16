from pydantic import BaseModel


class IncrInputSchema(BaseModel):
    value: int = 1
