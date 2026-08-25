import datetime
import enum
import uuid

from sqlalchemy import (Column, String, Float, Integer, DateTime, Enum,
                         ForeignKey, JSON, Boolean)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    ADMIN = "underwriter_admin"
    AGENT = "field_agent"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.AGENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    applicants = relationship("Applicant", back_populates="created_by")


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(String, primary_key=True, default=gen_uuid)
    display_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    crop_type = Column(String, nullable=True)
    farm_size_acres = Column(Float, nullable=True)
    loan_amount_inr = Column(Float, nullable=True)
    created_by_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    created_by = relationship("User", back_populates="applicants")
    assessments = relationship("Assessment", back_populates="applicant")


class Assessment(Base):
    """
    A single underwriting assessment run for an applicant. Stores every
    input and every intermediate score so the whole decision is auditable
    end to end (this is what the /audit endpoint reads from).
    """
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=gen_uuid)
    applicant_id = Column(String, ForeignKey("applicants.id"))

    agri_data = Column(JSON, nullable=True)          # raw + derived satellite/weather signal
    emotion_data = Column(JSON, nullable=True)        # raw + derived speech-emotion classifier output
    combined_score = Column(JSON, nullable=True)      # final simulated decision + explanation

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    applicant = relationship("Applicant", back_populates="assessments")
