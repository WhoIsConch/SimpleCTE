from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Column, Table
import enum 


__all__ = (
    "Organization",
    "Contact",
    "Resource",
    "ContactInfo",
    "CustomField",
    "ContactInfoType"
)


class ContactInfoType(enum.Enum):
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    CUSTOM_INFO = "custom_info"


class _Base(DeclarativeBase):
    pass


_contacts_organizations = Table(
    "contacts_organizations",
    _Base.metadata,
    Column("contact_id", ForeignKey("contacts.id"), primary_key=True),
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
)

_organizations_resources = Table(
    "organizations_resources",
    _Base.metadata,
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
    Column("resource_id", ForeignKey("resources.id"), primary_key=True),
)

_contacts_resources = Table(
    "contacts_resources",
    _Base.metadata,
    Column("contact_id", ForeignKey("contacts.id"), primary_key=True),
    Column("resource_id", ForeignKey("resources.id"), primary_key=True),
)


class Organization(_Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    type: Mapped[str]
    status: Mapped[str | None]
    
    contact_info: Mapped[list["ContactInfo"] | None] = relationship(back_populates="organization", foreign_keys="ContactInfo.organization_id", cascade="all, delete-orphan")
    custom_fields: Mapped[list["CustomField"] | None] = relationship(back_populates="organization", foreign_keys="CustomField.organization_id", cascade="all, delete-orphan")
    contacts: Mapped[list["Contact"] | None] = relationship(back_populates="organizations", secondary=_contacts_organizations)
    resources: Mapped[list["Resource"] | None] = relationship(back_populates="organizations", secondary=_organizations_resources)


class Contact(_Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    status: Mapped[str | None]

    contact_info: Mapped[list["ContactInfo"] | None] = relationship(back_populates="contact", foreign_keys="ContactInfo.contact_id", cascade="all, delete-orphan")
    custom_fields: Mapped[list["CustomField"] | None] = relationship(back_populates="contact", foreign_keys="CustomField.contact_id", cascade="all, delete-orphan")
    resources: Mapped[list["Resource"] | None] = relationship(back_populates="contacts", secondary=_contacts_resources)
    organizations: Mapped[list["Organization"] | None] = relationship(back_populates="contacts", secondary=_contacts_organizations)

class Resource(_Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    content: Mapped[str]

    custom_fields: Mapped[list["CustomField"] | None] = relationship(cascade="all, delete-orphan")
    organizations: Mapped[list["Organization"] | None] = relationship(back_populates="resources", secondary=_organizations_resources)
    contacts: Mapped[list["Contact"] | None] = relationship(back_populates="resources", secondary=_contacts_resources)


class ContactInfo(_Base):
    __tablename__ = "contact_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[ContactInfoType]

    contact: Mapped["Contact | None"] = relationship(back_populates="contact_info", foreign_keys="ContactInfo.contact_id")
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    organization: Mapped["Organization | None"] = relationship(back_populates="contact_info", foreign_keys="ContactInfo.organization_id")
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))

    content: Mapped["CustomField | None"] = relationship()


class CustomField(_Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_info_id = mapped_column(ForeignKey("contact_info.id"))

    contact: Mapped["Contact | None"] = relationship(back_populates="custom_fields")
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    organization: Mapped["Organization | None"] = relationship(back_populates="custom_fields")
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    resource: Mapped["Resource | None"] = relationship(back_populates="custom_fields")
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))

    title: Mapped[str]
    content: Mapped[str]
