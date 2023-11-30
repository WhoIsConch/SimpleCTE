from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.enums import Screen


class Stack:
    """
    Add a stack that will keep track of each screen.
    If a stack is associated with information, such as a Viewer,
    it will also keep track of that information.
    """

    def __init__(self):
        self.stack = []

    def push(self, screen: "Screen", data: any = None) -> None:
        self.stack.append((screen, data))

    def pop(self) -> None:
        self.stack.pop()

    def peek(self) -> tuple["Screen", dict | None]:
        return self.stack[-1]

    def clear(self) -> None:
        self.stack.clear()

    def search_and_pop(self, data: any) -> None:
        """
        Search for a specific screen in the stack and pop it.
        """
        for i, (screen, value) in enumerate(self.stack):
            if value == data:
                self.stack.pop(i)
                break
