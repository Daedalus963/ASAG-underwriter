from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security.auth import get_current_user

router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.post("", response_model=schemas.ApplicantOut, status_code=201)
def create_applicant(
    payload: schemas.ApplicantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    applicant = models.Applicant(**payload.model_dump(), created_by_id=current_user.id)
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant


@router.get("", response_model=list[schemas.ApplicantOut])
def list_applicants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Applicant).order_by(models.Applicant.created_at.desc()).all()


@router.get("/{applicant_id}", response_model=schemas.ApplicantOut)
def get_applicant(
    applicant_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found.")
    return applicant


@router.get("/{applicant_id}/assessments", response_model=list[schemas.AssessmentOut])
def list_assessments(
    applicant_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found.")
    return applicant.assessments
