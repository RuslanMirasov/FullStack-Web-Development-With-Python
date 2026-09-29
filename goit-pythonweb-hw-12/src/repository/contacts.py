from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> list[Contact]:
        stmt = select(Contact).filter_by(user=user)
        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        stmt = stmt.offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_upcoming_birthdays(self, days: int, user: User) -> list[Contact]:
        today = date.today()
        end_date = today + timedelta(days=days)
        birthday_md = func.to_char(Contact.birthday, "MM-DD")
        start_md = today.strftime("%m-%d")
        end_md = end_date.strftime("%m-%d")

        if start_md <= end_md:
            condition = birthday_md.between(start_md, end_md)
        else:
            condition = or_(birthday_md >= start_md, birthday_md <= end_md)

        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(condition)
            .order_by(birthday_md)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_email(self, email: str, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(email=email, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact