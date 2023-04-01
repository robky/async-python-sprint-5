from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class File(Base):
    __tablename__ = "file"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    created_ad = Column(DateTime, index=True, default=datetime.utcnow)
    path = Column(String, unique=True, nullable=False)
    size = Column(Integer, nullable=False)
    # is_downloadable = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("user.id"))
    author = relationship(
        "User",
        cascade="all, delete",
        back_populates="file",
    )
