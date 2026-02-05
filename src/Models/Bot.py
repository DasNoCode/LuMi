from __future__ import annotations

from pymodm import MongoModel, fields


class Bot(MongoModel):
    commands: list[dict] = fields.ListField(
        fields.DictField(),
        required=False, 
        blank=True,
        default=list,
    )

    sticker_sets: list[dict] = fields.ListField(
        fields.DictField(),
        required=False,
        blank=True,
        default=list,
    )


