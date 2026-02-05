from __future__ import annotations
from pymodm import MongoModel, fields
from datetime import datetime

# 👤 User Model
class User(MongoModel):
    user_id: int = fields.CharField(required=True)
    afk: bool = fields.DictField(required=False, default=lambda: {"status": False})
    xp: int = fields.IntegerField(required=True, min_value=0, default=0)
    level: int = fields.IntegerField(required=True, min_value=1, default=1)
    ban: bool = fields.DictField(required=True, default=lambda: {"status": False})
    created_at: datetime = fields.DateTimeField(required=True, default=lambda: datetime.now().date())
