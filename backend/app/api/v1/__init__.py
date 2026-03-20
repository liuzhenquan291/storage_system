"""
API V1 module initialization
"""
from app.api.v1 import auth, user, role, menu, warehouse, material, order, device, dashboard

__all__ = [
    "auth",
    "user",
    "role",
    "menu",
    "warehouse",
    "material",
    "order",
    "device",
    "dashboard",
]
