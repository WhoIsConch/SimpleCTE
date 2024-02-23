from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    type: Mapped[str]
    status: Mapped[Optional[str]]
    
    contact_info: Mapped["ContactInfo"] = relationship(back_populates="organization")
    contacts: Mapped[List["Contact"]] = relationship(back_populates="organizations",)
    custom_fields: Mapped[List["CustomField"]] = relationship(back_populates="record")
    resources: Mapped[List["Resource"]] = relationship(back_populates="organizations")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    status: Mapped[str | None]

    contact_info: Mapped["ContactInfo"] = relationship(back_populates="contact")
    custom_fields: Mapped[List["CustomField"]] = relationship(back_populates="record")
    resources: Mapped[List["Resource"]] = relationship(back_populates="contacts")

class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    content: Mapped[str]

    custom_fields: Mapped[List["CustomField"]] = relationship(
        back_populates="record"
    )
    organizations: Mapped[List["Organization"]] = relationship(
        back_populates="resources"
    )
    contacts: Mapped[List["Contact"]] = relationship(
        back_populates="contacts"
    )

class ContactInfo(Base):
    __tablename__ = "contact_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    contact: Mapped[Optional["Contact"]] = relationship(back_populates="contact_info")
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="contact_info")

    addresses: Mapped[Optional[List[str]]]
    phones: Mapped[Optional[List[int]]]
    emails: Mapped[Optional[List[str]]]
    custom_info: Mapped[Optional[dict[str, str]]]


class CustomField(Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    record: Mapped["Contact" | "Organization" | "Resource"]

    title: Mapped[str]
    content: Mapped[str]
