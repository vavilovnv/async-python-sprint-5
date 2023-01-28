from pydantic import BaseModel


class Ping(BaseModel):
    ping_db: float
