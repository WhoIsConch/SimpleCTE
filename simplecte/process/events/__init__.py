from .manage_record import EVENT_MAP as RECORD_MAP, _delete_record
from .edit_info import EVENT_MAP as EDIT_INFO_MAP
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from process.app import App


def handle_other_events(app: "App", event: str, data: dict) -> bool:
    """
    Updates some part of the system, whether it be a record, a screen, or something else.
    """
    for func_map in (RECORD_MAP, EDIT_INFO_MAP):
        method = func_map.get(event, None)

        if method is None:
            if event.lower().strip("-").startswith("delete"):
                method = _delete_record
            else:
                continue

        # Check if the method requires one argument, App, or both App and Data
        try:
            method(app)
        except TypeError:
            try:
                method(app, data)
            except TypeError:
                method(app, data, event)

        return True

    return False


