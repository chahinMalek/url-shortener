from enum import Enum


class Permission(str, Enum):
    SHORTEN_URL = "shorten_url"
    DELETE_URL = "delete_url"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
