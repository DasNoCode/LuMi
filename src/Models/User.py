from __future__ import annotations
from pymodm import MongoModel, fields
from datetime import datetime


class User(MongoModel):
    user_id: int = fields.CharField(required=True)

    afk: dict = fields.DictField(
        required=False,
        default=lambda: {"status": False},
    )

    xp: int = fields.IntegerField(
        required=True,
        min_value=0,
        default=0,
    )

    level: int = fields.IntegerField(
        required=True,
        min_value=1,
        default=1,
    )

    ban: dict = fields.DictField(
        required=True,
        default=lambda: {"status": False},
    )

    profile_photo_url: str | None = fields.CharField(
        required=False,
        blank=True,
        default=None,
    )
    
    github: str | None = fields.CharField(
        required=False,
        blank=True,
        default=None,
    )

    created_at: datetime = fields.DateTimeField(
        required=True,
        default=lambda: datetime.now().date(),
    )
