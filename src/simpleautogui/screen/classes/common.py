from pyautogui import (
    click,
    dragTo,
    dragRel,
    moveTo,
    doubleClick
)


class Box:
    """
    Represents a rectangular area on the screen, providing methods to interact with it.

    :param x: The x-coordinate of the top-left corner of the box.
    :param y: The y-coordinate of the top-left corner of the box.
    :param width: The width of the box.
    :param height: The height of the box.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.cx = self.x + self.width // 2
        self.cy = self.y + self.height // 2

    def __str__(self):
        return f'Box(x={self.x}, y={self.y}, w={self.width}, h={self.height}, cx={self.cx}, cy={self.cy})'

    def click(self, center: bool = True, oX: int = 0, oY: int = 0, **click_kwargs) -> None:
        """
        Performs a mouse click on the box.

        :param center: If True, clicks the center of the box; otherwise clicks the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.click().
        """
        click_x = self.cx + oX if center else self.x + oX
        click_y = self.cy + oY if center else self.y + oY
        click(click_x, click_y, **click_kwargs)

    def doubleClick(self, center: bool = True, oX: int = 0, oY: int = 0, **click_kwargs) -> None:
        """
        Performs a double mouse click on the box.

        :param center: If True, double-clicks the center of the box; otherwise double-clicks the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.doubleClick().
        """
        click_x = self.cx + oX if center else self.x + oX
        click_y = self.cy + oY if center else self.y + oY
        doubleClick(click_x, click_y, **click_kwargs)

    def moveTo(self, center: bool = True, oX: int = 0, oY: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor to the box.
        :param center: If True, moves to the center of the box; otherwise moves to the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param move_kwargs: Additional keyword arguments for pyautogui.moveTo().
        """

        move_x = self.cx + oX if center else self.x + oX
        move_y = self.cy + oY if center else self.y + oY
        moveTo(move_x, move_y, **move_kwargs)

    def dragDropTo(self, endX, endY, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box and drops to a target box.

        :param endX: Finish x-coordinate
        :param endY: Finish y-coordinate
        :param center: If True, starts from the center of the current box.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragTo().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        dragTo(start_x, start_y, endX, endY, **drag_kwargs)

    def dragDropRel(self, relX: int, relY: int, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box to a relative position.

        :param relX: The relative x-coordinate to drag to.
        :param relY: The relative y-coordinate to drag to.
        :param center: If True, starts from the center of the box.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragRel().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        dragRel(start_x, start_y, relX, relY, **drag_kwargs)
