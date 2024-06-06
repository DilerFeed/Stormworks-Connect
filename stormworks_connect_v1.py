# Flask сервер
import tkinter as tk
from tkinter import filedialog, Label, ttk, Checkbutton, BooleanVar
from PIL import Image, ImageTk
from flask import Flask, request, jsonify
import threading
import logging
import webbrowser
import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Flask app
app = Flask(__name__)
current_image = None
original_image = None

logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    app.logger.debug('Response: %s', response.get_data())
    return response

# Dictionary with monitor sizes
monitor_sizes = {
    "1x1": (32, 32),
    "1x2": (64, 32),
    "1x3": (96, 32),
    "2x2": (64, 64),
    "2x3": (96, 64),
    "3x3": (96, 96),
    "5x3": (160, 96),
    "9x5": (288, 160)
}

selected_size = (288, 160)  # Default size
fill_image = False  # Default fill option

def process_image(image, size, fill):
    if fill:
        image = image.resize(size, Image.Resampling.LANCZOS)
    else:
        image.thumbnail(size, Image.Resampling.LANCZOS)
    return image

@app.route('/upload', methods=['POST'])
def upload_image():
    global current_image, original_image
    file = request.files['file']
    image = Image.open(file.stream)
    original_image = image.copy()
    current_image = process_image(image, selected_size, fill_image)
    return "Image uploaded and processed", 200

@app.route('/image', methods=['GET'])
def get_image():
    global current_image
    if current_image is None:
        return "No image uploaded", 404

    pixels = current_image.load()
    width, height = current_image.size
    image_data = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixels[x, y][:3]
            pixel_str = f"{r} {g} {b}"
            row.append(pixel_str)
        image_data.append(",".join(row))
    
    image_string = "\n".join(image_data)
    image_string_with_size = f"{width} {height}\n{image_string}"
    return image_string_with_size

@app.route('/column', methods=['GET'])
def get_column():
    global current_image
    if current_image is None:
        return "No image uploaded", 404

    pixels = current_image.load()
    width, height = current_image.size
    x = int(request.args.get('x'))
    if x < 0 or x >= width:
        return "Column coordinates out of bounds", 400

    column_data = []
    for y in range(height):
        r, g, b = pixels[x, y][:3]
        pixel_str = f"{r} {g} {b}"
        column_data.append(pixel_str)

    column_string = "\n".join(column_data)
    return column_string, 200

def start_flask():
    app.run(debug=True, use_reloader=False)

thread = threading.Thread(target=start_flask)
thread.daemon = True
thread.start()

def open_file():
    global current_image, original_image
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path)
        original_image = image.copy()
        current_image = process_image(image, selected_size, fill_image)
        update_display_image()

def update_display_image():
    global current_image
    if original_image:
        current_image = process_image(original_image.copy(), selected_size, fill_image)
        display_image = current_image.copy()
        display_image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(display_image)
        image_label.config(image=img_tk)
        image_label.image = img_tk
        server_status.config(text=f"Server is running on port 5000\nImage loaded")

def on_monitor_size_change(event):
    global selected_size
    selected_size = monitor_sizes[monitor_size_var.get()]
    update_display_image()

def on_fill_option_change():
    global fill_image
    fill_image = fill_var.get()
    update_display_image()

def open_steam_profile(event):
    webbrowser.open_new("https://steamcommunity.com/id/inspirers/")

def open_github_profile(event):
    webbrowser.open_new("https://github.com/DilerFeed")

root = tk.Tk()
root.title("Stormworks Connect")

root.geometry("500x600")
root.iconphoto(False, tk.PhotoImage(file=resource_path('SC_cover.png')))

monitor_size_var = tk.StringVar(value="9x5")
monitor_size_menu = ttk.Combobox(root, textvariable=monitor_size_var, values=list(monitor_sizes.keys()))
monitor_size_menu.bind("<<ComboboxSelected>>", on_monitor_size_change)
monitor_size_menu.pack(pady=10)

fill_var = BooleanVar(value=False)
fill_checkbutton = Checkbutton(root, text="Fill", variable=fill_var, command=on_fill_option_change)
fill_checkbutton.pack(pady=5)

upload_button = tk.Button(root, text="Upload image", command=open_file, font=("Arial", 14))
upload_button.pack(pady=10)

image_label = Label(root)
image_label.pack(pady=10)

server_status = Label(root, text="Server is running on port 5000", fg="green", font=("Arial", 12))
server_status.pack(pady=5)

# The name of the program
program_title = Label(root, text="Stormworks Connect", font=("Arial", 16))
program_title.pack(pady=5)

# Author information
author_info = Label(root, text="© Hlib Ishchenko 2024", font=("Arial", 10))
author_info.pack(pady=5)

# Steam profile link
steam_profile = Label(root, text="Steam Profile", fg="blue", cursor="hand2", font=("Arial", 12))
steam_profile.pack(pady=5)
steam_profile.bind("<Button-1>", open_steam_profile)

# Link to GitHub profile
github_profile = Label(root, text="GitHub Profile", fg="blue", cursor="hand2", font=("Arial", 12))
github_profile.pack(pady=5)
github_profile.bind("<Button-1>", open_github_profile)

root.mainloop()
