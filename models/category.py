from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Category(Base):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )