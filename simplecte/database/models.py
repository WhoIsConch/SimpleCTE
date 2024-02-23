from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Column, Table
import enum 




class ContactInfoType(enum.Enum):
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    CUSTOM_INFO = "custom_info"


class Base(DeclarativeBase):
    pass


contacts_organizations = Table(
    "contacts_organizations",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id"), primary_key=True),
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
)

organizations_resources = Table(
    "organizations_resources",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
    Column("resource_id", ForeignKey("resources.id"), primary_key=True),
)

contacts_resources = Table(
    "contacts_resources",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id"), primary_key=True),
    Column("resource_id", ForeignKey("resources.id"), primary_key=True),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    type: Mapped[str]
    status: Mapped[str | None]
    
    contact_info: Mapped[list["ContactInfo"] | None] = relationship(back_populates="organization", foreign_keys="ContactInfo.organization_id")
    custom_fields: Mapped[list["CustomField"] | None] = relationship(back_populates="organization", foreign_keys="CustomField.organization_id")
    contacts: Mapped[list["Contact"] | None] = relationship(back_populates="organizations", secondary=contacts_organizations)
    resources: Mapped[list["Resource"] | None] = relationship(back_populates="organizations", secondary=organizations_resources)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    status: Mapped[str | None]

    contact_info: Mapped[list["ContactInfo"] | None] = relationship(back_populates="contact", foreign_keys="ContactInfo.contact_id")
    custom_fields: Mapped[list["CustomField"] | None] = relationship(back_populates="contact", foreign_keys="CustomField.contact_id")
    resources: Mapped[list["Resource"] | None] = relationship(back_populates="contacts", secondary=contacts_resources)
    organizations: Mapped[list["Organization"] | None] = relationship(back_populates="contacts", secondary=contacts_organizations)

class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    content: Mapped[str]

    custom_fields: Mapped[list["CustomField"] | None] = relationship()
    organizations: Mapped[list["Organization"] | None] = relationship(back_populates="resources", secondary=organizations_resources)
    contacts: Mapped[list["Contact"] | None] = relationship(back_populates="resources", secondary=contacts_resources)


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[ContactInfoType]

    contact: Mapped["Contact | None"] = relationship(back_populates="contact_info", foreign_keys="ContactInfo.contact_id")
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    organization: Mapped["Organization | None"] = relationship(back_populates="contact_info", foreign_keys="ContactInfo.organization_id")
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))

    content: Mapped["CustomField | None"] = relationship()


class CustomField(Base):
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
