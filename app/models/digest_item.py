from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DigestItem(Base):
    __tablename__ = "digest_items"

    id = Column(Integer, primary_key=True, index=True)
    digest_id = Column(Integer, ForeignKey("digests.id", ondelete="CASCADE"), index=True, nullable=False)
    source = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=False)

    digest = relationship("Digest", back_populates="items")
