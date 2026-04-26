from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class GridResponse(BaseModel):
    language: str
    rows: int
    cols: int
    grid: list[list[str]]


class TimeResponse(BaseModel):
    language: str
    hours: int
    minutes: int
    sentence: str
    coords: list[tuple[int, int]]
    led_indices: list[int]


class BrightnessResponse(BaseModel):
    brightness: int
