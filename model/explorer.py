from pydantic import BaseModel, Field


class Explorer(BaseModel):
    name: str = Field(min_length=1, max_length=50, examples=["Claude Hande"])
    country: str = Field(pattern=r"^[A-Z]{2}$", examples=["FR"])
    description: str = Field(default="", max_length=500)


class ExplorerUpdate(BaseModel):
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    description: str | None = Field(default=None, max_length=500)
