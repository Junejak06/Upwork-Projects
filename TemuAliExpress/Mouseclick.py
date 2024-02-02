from pynput.mouse import Listener

def on_click(x, y, button, pressed):
    if pressed:
        print(f'Mouse clicked at ({x}, {y}) with {button}')

# Set up the listener
with Listener(on_click=on_click) as listener:
    listener.join()
