from .manage_record import EVENT_MAP as RECORD_MAP, _delete_record
from .edit_info import EVENT_MAP as EDIT_INFO_MAP
from .manage_ui import EVENT_MAP as UI_MAP
from .debug import handle_debug
from typing import TYPE_CHECKING
from inspect import signature

if TYPE_CHECKING:
    from process.app import App


def handle_other_events(app: "App", event: str, data: dict) -> bool:
    """
    Updates some part of the system, whether it be a record, a screen, or something else.
    """
    if event.find("::CODE") != -1:
        return handle_debug(event)

    for func_map in [EDIT_INFO_MAP, RECORD_MAP, UI_MAP]:
        method = func_map.get(event, None)

        # _delete_record() gets special treatment
        if method is None:
            if event.lower().strip("-").startswith("delete"):
                method = _delete_record
            else:
                continue

        # Find out how many parameters the callback takes and call it based on that
        num_params = len(signature(method).parameters)
        params = [app, data, event]

        method(*params[0:num_params])

        return True

    return False
