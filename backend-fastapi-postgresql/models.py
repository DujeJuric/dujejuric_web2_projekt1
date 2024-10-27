from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    vatin = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())