from .models import Contact, Organization
from typing import TYPE_CHECKING
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from process.app import App


__all__ = (
    "get_table_values",
)


def get_table_values(
        app: "App",
        record_type: Contact | Organization,
        amount: int | None = 10,
        search_info: dict | None = None,
        descending: bool = False,
) -> list[Contact]:
    """
    Get the necessary information from the database to populate the 
    Contact search table
    """

    with Session(app.engine) as session:
        query = session.query(record_type)

        if search_info:
            query = query.filter(
                Contact.name.ilike(f"%{search_info['name']}%")
            )

        if descending:
            query = query.order_by(record_type.id.desc())
        else:
            query = query.order_by(record_type.id)

        if amount:
            query = query.limit(amount)

        return query.all()
    