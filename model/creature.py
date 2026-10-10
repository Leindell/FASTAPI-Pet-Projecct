from pydantic import BaseModel, Field


class Creature(BaseModel):
    """Полная модель существа: так оно хранится и так отдаётся клиенту."""

    name: str = Field(min_length=1, max_length=50, examples=["Yeti"])
    country: str = Field(pattern=r"^[A-Z]{2}$", description="Код страны ISO, например CN", examples=["CN"])
    area: str = Field(default="", max_length=100, examples=["Himalayas"])
    description: str = Field(default="", max_length=500)
    aka: str = Field(default="", max_length=100, description="Другие имена")


class CreatureUpdate(BaseModel):
    """Модель для PATCH: все поля необязательные, имя менять нельзя."""

    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    area: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    aka: str | None = Field(default=None, max_length=100)
