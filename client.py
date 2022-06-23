from argparse import SUPPRESS
from pickle import TRUE
from pynput import keyboard, mouse
import requests
from lib import key_to_special
from lib import special_to_resolution, resolution_to_special
from time import sleep

ADDRESS = "http://10.42.0.92:5000/"
SUPPRESS_MOUSE = True
SUPPRESS_KEYBOARD = True
CLIENT_RESOLUTION = special_to_resolution("1280x800")


#KEYBOARD

def on_key_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
        requests.get(ADDRESS + "keyboard/press", params={"key": key.char})
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
        requests.get(ADDRESS + "keyboard/press", params={"key": key_to_special(key), "special": "true"})

def on_key_release(key):
    try:
        print('alphanumeric key {0} released'.format(
            key.char))
        requests.get(ADDRESS + "keyboard/release", params={"key": key.char})
    except AttributeError:
        print('special key {0} released'.format(
            key))
        requests.get(ADDRESS + "keyboard/release", params={"key": key_to_special(key), "special": "true"})
    if key == keyboard.Key.esc:
        # Stop listener
        return False


#MOUSE

def on_mouse_move(x, y):
    (x, y) = pos_proportion((x, y))
    print('Pointer moved to {0}'.format(
        (x, y)))
    requests.get(ADDRESS + "mouse/move", params={"x": x, "y": y})

def on_button_click(x, y, button, pressed):
    (x, y) = pos_proportion((x, y))
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))

    if(pressed):
        requests.get(ADDRESS + "mouse/press", params={"x": x, "y": y})
    else:
        requests.get(ADDRESS + "mouse/release", params={"x": x, "y": y})

def on_scroll(x, y, dx, dy):
    (x, y) = pos_proportion((x, y))
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))
    requests.get(ADDRESS + "mouse/scroll", params={"x": x, "y": y, "dx": dx, "dy": dy})


#MISC

def get_server_resolution():
    r = requests.get(ADDRESS + "resolution")
    return r.json()["resolution"] # something like "1680x1050"

def pos_proportion(pos):
    return (int(round(pos[0] / CLIENT_RESOLUTION[0] * SERVER_RESOLUTION[0])),
        int(round(pos[1] / CLIENT_RESOLUTION[1] * SERVER_RESOLUTION[1])))

#LISTENERS

k_listener = keyboard.Listener(
    on_press=on_key_press,
    on_release=on_key_release,
    suppress=SUPPRESS_KEYBOARD)

m_listener = mouse.Listener(
    on_move=on_mouse_move,
    on_click=on_button_click,
    on_scroll=on_scroll,
    suppress=SUPPRESS_MOUSE)

if __name__ == "__main__":
    SERVER_RESOLUTION = special_to_resolution(get_server_resolution())

    k_listener.start()
    m_listener.start()
    while True:
        sleep(0.1)
        if(not k_listener.running): exit()
        if(not m_listener.running): exit()
