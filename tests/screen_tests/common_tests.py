from simpleautogui import screen as sags
from pyautogui import size


def wait_for_image_test():
    result = sags.wait_for_image(
        paths="../resources/images/gfesp.png",
        timeout=10000,
        accuracy=0.9,
        error_dialog=False,
        region=(0, 0, size().width, size().height),
        check_interval=100,
    )
    print(result)
    result.moveTo()
    result.click()


# wait_for_image_test()