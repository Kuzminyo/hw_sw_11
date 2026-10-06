from calendar import isleap
from datetime import date, timedelta

from sqlalchemy import and_, extract, or_, select
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate


def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> list[Contact]:
    stmt = select(Contact)
    if first_name:
        stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
    stmt = stmt.order_by(Contact.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_contact(db: Session, contact_id: int) -> Contact | None:
    return db.get(Contact, contact_id)


def get_contact_by_email(db: Session, email: str) -> Contact | None:
    return db.scalar(select(Contact).where(Contact.email == email))


def create_contact(db: Session, body: ContactCreate) -> Contact:
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(db: Session, contact: Contact, body: ContactUpdate) -> Contact:
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: Contact) -> None:
    db.delete(contact)
    db.commit()


def _celebration_days(today: date, days: int) -> list[tuple[int, int, int]]:
    """(offset, month, day) for every birthday celebrated in today..today+days.

    Feb 29 birthdays are celebrated on Feb 28 in non-leap years.
    """
    result = []
    for offset in range(days + 1):
        d = today + timedelta(days=offset)
        result.append((offset, d.month, d.day))
        if (d.month, d.day) == (2, 28) and not isleap(d.year):
            result.append((offset, 2, 29))
    return result


def get_upcoming_birthdays(db: Session, days: int = 7) -> list[Contact]:
    """Contacts whose birthday falls within the next `days` days (today included),
    sorted by how soon the birthday is."""
    celebration = _celebration_days(date.today(), days)
    conditions = [
        and_(extract("month", Contact.birthday) == m, extract("day", Contact.birthday) == d)
        for _, m, d in celebration
    ]
    contacts = db.scalars(select(Contact).where(or_(*conditions)))

    offsets: dict[tuple[int, int], int] = {}
    for offset, m, d in celebration:
        offsets.setdefault((m, d), offset)
    return sorted(contacts, key=lambda c: offsets[(c.birthday.month, c.birthday.day)])
