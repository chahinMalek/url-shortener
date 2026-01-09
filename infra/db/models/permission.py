from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.user import UserModel


class UserPermissionModel(Base):
    __tablename__ = "user_permissions"

    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    permission: Mapped[str] = mapped_column(String(50), primary_key=True)

    user: Mapped["UserModel"] = relationship(back_populates="permissions")
