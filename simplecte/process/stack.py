from utils.enums import Screen
from typing import Generator, Any


__all__ = ("Stack",)


class Stack:
    """
    Add a stack that will keep track of each screen.
    If a stack is associated with information, such as a Viewer,
    it will also keep track of that information.
    """

    def __init__(self):
        self.stack: list[tuple[Screen, Any]] = []

    def push(self, screen: "Screen", data: Any = None) -> None:
        self.stack.append((screen, data))

    def pop(self) -> None:
        self.stack.pop()

    def peek(self) -> tuple["Screen", dict | None]:
        return self.stack[-1]

    def clear(self) -> None:
        self.stack.clear()

    def search_and_pop(self, data: Any) -> None:
        """
        Search for a specific screen in the stack and pop it.
        """
        for i, (screen, value) in enumerate(self.stack):
            if value == data:
                self.stack.pop(i)

            if isinstance(data, int) and value and value.id == data:
                self.stack.pop(i)

    def generate_previews(self) -> Generator[str, str, None]:
        """
        Generates a list of strings that will be used to preview what is in the stack.
        """
        for screen, value in self.stack:
            screen_title = screen.name.replace("_", " ").title()

            if value and screen in (
                Screen.ORG_VIEW,
                Screen.CONTACT_VIEW,
                Screen.RESOURCE_VIEW,
            ):
                yield value.name
            else:
                yield screen_title

    def jump_to(self, index: int) -> None:
        """
        Jump to a specific index in the stack. This will pop all screens above the index.
        """

        for _ in range(len(self.stack) - index - 1):
            self.stack.pop()
