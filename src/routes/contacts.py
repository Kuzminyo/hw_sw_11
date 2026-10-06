from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact
from src.repository import contacts as repo
from src.schemas import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _get_or_404(db: Session, contact_id: int) -> Contact:
    contact = repo.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/", response_model=list[ContactResponse], summary="List / search contacts")
def read_contacts(
    first_name: str | None = Query(None, description="Search by first name (partial, case-insensitive)"),
    last_name: str | None = Query(None, description="Search by last name (partial, case-insensitive)"),
    email: str | None = Query(None, description="Search by email (partial, case-insensitive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return repo.get_contacts(db, skip, limit, first_name, last_name, email)


@router.get(
    "/birthdays",
    response_model=list[ContactResponse],
    summary="Contacts with birthdays in the next 7 days",
)
def upcoming_birthdays(
    days: int = Query(7, ge=0, le=365, description="How many days ahead to look"),
    db: Session = Depends(get_db),
):
    return repo.get_upcoming_birthdays(db, days)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get contact by id")
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, contact_id)


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create contact",
)
def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    if repo.get_contact_by_email(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    return repo.create_contact(db, body)


@router.put("/{contact_id}", response_model=ContactResponse, summary="Update contact")
def update_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db)):
    contact = _get_or_404(db, contact_id)
    if body.email and body.email != contact.email and repo.get_contact_by_email(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    return repo.update_contact(db, contact, body)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete contact")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    repo.delete_contact(db, _get_or_404(db, contact_id))
