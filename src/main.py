from src.process.app import App
from src.process.main_loop import main_loop


def start():
    app = App()
    main_loop(app)


if __name__ == '__main__':
    start()
