from process import App
from process import main_loop


def start():
    app = App()
    main_loop(app)


if __name__ == "__main__":
    start()
