import tkinter as tk
from tkinter import filedialog, StringVar, BooleanVar, DoubleVar, IntVar
from tkinter import ttk
from PIL import Image, ImageTk
from flask import Flask, request, jsonify
import threading
import logging
import webbrowser
import sys
import os
import pygame
import requests
from packaging import version
import TKinterModernThemes as TKMT
import ctypes
import darkdetect

# Enable High DPI support
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(e)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def open_download_link(url):
    webbrowser.open_new(url)

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        # Define current version
        self.current_version = "1.1.0.0"

        # Detect system theme
        system_theme = self.get_system_theme()

        # Initialize with detected theme
        super().__init__("Stormworks Connect", "sun-valley", system_theme)
        
        # Flask app initialization
        self.app = Flask(__name__)
        self.current_image = None
        self.original_image = None
        self.init_flask()
        
        # Setting up logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Initialize Pygame
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        
        # Variables for joystick control
        self.joystick_name = tk.StringVar()
        self.steering_angle = DoubleVar()
        self.gas_pedal = DoubleVar()
        self.brake_pedal = DoubleVar()
        self.deadzone = DoubleVar(value=0.05)
        self.swap_pedals = BooleanVar(value=False)
        self.combined_pedals = BooleanVar(value=False)
        self.steering_axis = tk.IntVar(value=0)
        self.gas_axis = tk.IntVar(value=2)
        self.brake_axis = tk.IntVar(value=1)
        self.shift_up_button = tk.IntVar(value=1)
        self.shift_down_button = tk.IntVar(value=0)
        self.custom_button_1 = tk.IntVar(value=9)
        self.custom_button_2 = tk.IntVar(value=8)
        self.custom_button_3 = tk.IntVar(value=6)
        self.custom_button_4 = tk.IntVar(value=7)
        
        self.shift_up_status = tk.StringVar()
        self.shift_down_status = tk.StringVar()
        self.custom_button_1_status = tk.StringVar()
        self.custom_button_2_status = tk.StringVar()
        self.custom_button_3_status = tk.StringVar()
        self.custom_button_4_status = tk.StringVar()
        
        # Monitor sizes dictionary
        self.monitor_sizes = {
            "1x1": (32, 32),
            "1x2": (64, 32),
            "1x3": (96, 32),
            "2x2": (64, 64),
            "2x3": (96, 64),
            "3x3": (96, 96),
            "5x3": (160, 96),
            "9x5": (288, 160)
        }

        self.selected_size = (288, 160)
        self.fill_image = False

        self.create_widgets()
        self.poll_joystick()
        self.check_for_updates()
        
        self.root.geometry("800x600")
        self.root.update_idletasks()
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.root.minsize(int(self.root.winfo_width() * scaleFactor), int(self.root.winfo_height() * scaleFactor))
        self.root.resizable(True, True)
        
        self.root.iconphoto(False, tk.PhotoImage(file=resource_path('SC_cover.png')))
        
        self.run()

    def get_system_theme(self):
        try:
            if darkdetect.isDark():
                return 'dark'
            else:
                return 'light'
        except Exception as e:
            print(e)
            return 'light'
        
    def switch_to_dark_theme(self):
        self.root.tk.call("set_theme", "dark")
        self.mode = "dark"

    def switch_to_light_theme(self):
        self.root.tk.call("set_theme", "light")
        self.mode = "light"
        
    def check_for_updates(self):
        try:
            response = requests.get("https://dilerfeed.github.io/Stormworks-Connect/version.json")
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info["version"]
                download_url = version_info["download_url"]

                if version.parse(latest_version) > version.parse(self.current_version):
                    self.show_update_notification(download_url)
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def show_update_notification(self, download_url):
        update_window = tk.Toplevel(self)
        update_window.title("Update Available")
        update_window.geometry("300x150")

        label = ttk.Label(update_window, text="A new version of the program is available!")
        label.pack(pady=10)

        download_button = ttk.Button(update_window, text="Download", command=lambda: self.open_download_link(download_url))
        download_button.pack(pady=5)

        close_button = ttk.Button(update_window, text="Close", command=update_window.destroy)
        close_button.pack(pady=5)

    def create_widgets(self):
        # Frames for different tabs
        self.tab_control = ttk.Notebook(self.root)
        self.image_transmit_frame = ttk.Frame(self.tab_control)
        self.steering_wheel_frame = ttk.Frame(self.tab_control)
        self.info_frame = ttk.Frame(self.tab_control)

        self.tab_control.add(self.image_transmit_frame, text="Image transmit")
        self.tab_control.add(self.steering_wheel_frame, text="Steering wheel")
        self.tab_control.add(self.info_frame, text="Info")
        self.tab_control.pack(expand=1, fill="both")

        # Image transmit tab
        self.monitor_size_var = tk.StringVar(value="9x5")
        monitor_size_menu = ttk.Combobox(self.image_transmit_frame, textvariable=self.monitor_size_var, values=list(self.monitor_sizes.keys()))
        monitor_size_menu.bind("<<ComboboxSelected>>", self.on_monitor_size_change)
        monitor_size_menu.pack(pady=10)

        self.fill_var = tk.BooleanVar(value=False)
        fill_checkbutton = ttk.Checkbutton(self.image_transmit_frame, text="Fill", variable=self.fill_var, command=self.on_fill_option_change)
        fill_checkbutton.pack(pady=5)

        upload_button = ttk.Button(self.image_transmit_frame, text="Upload image", command=self.open_file)
        upload_button.pack(pady=10)

        self.image_label = ttk.Label(self.image_transmit_frame)
        self.image_label.pack(pady=10)

        self.status_label = ttk.Label(self.image_transmit_frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Info tab
        ttk.Button(self.info_frame, text="Switch to Dark Theme", command=self.switch_to_dark_theme).pack(pady=10)
        ttk.Button(self.info_frame, text="Switch to Light Theme", command=self.switch_to_light_theme).pack(pady=10)

        server_status = ttk.Label(self.info_frame, text="Server is running on port 5000", foreground="green", font=("Arial", 12))
        server_status.pack(pady=5)

        program_title = ttk.Label(self.info_frame, text="Stormworks Connect v1.1.0.0", font=("Arial", 16))
        program_title.pack(pady=5)

        author_info = ttk.Label(self.info_frame, text="© Hlib Ishchenko 2024", font=("Arial", 10))
        author_info.pack(pady=5)

        steam_profile = ttk.Label(self.info_frame, text="Steam Profile", foreground="blue", cursor="hand2", font=("Arial", 12))
        steam_profile.pack(pady=5)
        steam_profile.bind("<Button-1>", self.open_steam_profile)

        github_profile = ttk.Label(self.info_frame, text="GitHub Profile", foreground="blue", cursor="hand2", font=("Arial", 12))
        github_profile.pack(pady=5)
        github_profile.bind("<Button-1>", self.open_github_profile)

        # Steering wheel tab
        ttk.Label(self.steering_wheel_frame, text="Select Joystick:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.joystick_menu = ttk.Combobox(self.steering_wheel_frame, textvariable=self.joystick_name)
        self.joystick_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Steering Angle:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.steering_angle).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Gas Pedal:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.gas_pedal).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Brake Pedal:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.brake_pedal).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Deadzone:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        deadzone_scale = ttk.Scale(self.steering_wheel_frame, from_=0, to=0.2, orient=tk.HORIZONTAL, variable=self.deadzone)
        deadzone_scale.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        deadzone_entry = ttk.Entry(self.steering_wheel_frame, textvariable=self.deadzone)
        deadzone_entry.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        ttk.Checkbutton(self.steering_wheel_frame, text="Swap Gas and Brake Pedals", variable=self.swap_pedals).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(self.steering_wheel_frame, text="Combined Pedals", variable=self.combined_pedals).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        self.create_joystick_buttons()

        # Add labels for shift and custom button statuses
        self.create_joystick_button("Shift Up Button", 6, self.shift_up_button, self.shift_up_status)
        self.create_joystick_button("Shift Down Button", 7, self.shift_down_button, self.shift_down_status)
        self.create_joystick_button("Custom Button 1", 8, self.custom_button_1, self.custom_button_1_status)
        self.create_joystick_button("Custom Button 2", 9, self.custom_button_2, self.custom_button_2_status)
        self.create_joystick_button("Custom Button 3", 10, self.custom_button_3, self.custom_button_3_status)
        self.create_joystick_button("Custom Button 4", 11, self.custom_button_4, self.custom_button_4_status)

    def create_joystick_buttons(self):
        ttk.Button(self.steering_wheel_frame, text="Set Steering Axis", command=lambda: self.open_axis_window(self.steering_axis, "Steering")).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Gas Axis", command=lambda: self.open_axis_window(self.gas_axis, "Gas Pedal")).grid(row=2, column=2, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Brake Axis", command=lambda: self.open_axis_window(self.brake_axis, "Brake Pedal")).grid(row=3, column=2, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Shift Up Button", command=lambda: self.open_button_window(self.shift_up_button, "Shift Up Button")).grid(row=6, column=3, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Shift Down Button", command=lambda: self.open_button_window(self.shift_down_button, "Shift Down Button")).grid(row=7, column=3, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Custom Button 1", command=lambda: self.open_button_window(self.custom_button_1, "Custom Button 1")).grid(row=8, column=3, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Custom Button 2", command=lambda: self.open_button_window(self.custom_button_2, "Custom Button 2")).grid(row=9, column=3, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Custom Button 3", command=lambda: self.open_button_window(self.custom_button_3, "Custom Button 3")).grid(row=10, column=3, padx=10, pady=5)
        ttk.Button(self.steering_wheel_frame, text="Set Custom Button 4", command=lambda: self.open_button_window(self.custom_button_4, "Custom Button 4")).grid(row=11, column=3, padx=10, pady=5)

    def create_joystick_button(self, text, row, button_var, status_label):
        ttk.Label(self.steering_wheel_frame, text=text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=button_var).grid(row=row, column=1, padx=10, pady=5, sticky="w")
        status_label_label = ttk.Label(self.steering_wheel_frame, textvariable=status_label)
        status_label_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        ttk.Button(self.steering_wheel_frame, text=f"Set {text}", command=lambda: self.open_button_window(button_var, text)).grid(row=row, column=3, padx=10, pady=5)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            self.original_image = image.copy()
            self.current_image = self.process_image(image, self.selected_size, self.fill_image)
            self.update_display_image()

    def process_image(self, image, size, fill):
        if fill:
            image = image.resize(size, Image.Resampling.LANCZOS)
        else:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        return image

    def update_display_image(self):
        if self.original_image:
            self.current_image = self.process_image(self.original_image.copy(), self.selected_size, self.fill_image)
            display_image = self.current_image.copy()
            display_image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(display_image)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
            self.status_label.config(text="Image loaded")

    def on_monitor_size_change(self, event):
        self.selected_size = self.monitor_sizes[self.monitor_size_var.get()]
        self.update_display_image()

    def on_fill_option_change(self):
        self.fill_image = self.fill_var.get()
        self.update_display_image()

    def open_steam_profile(self, event):
        webbrowser.open_new("https://steamcommunity.com/id/inspirers/")

    def open_github_profile(self, event):
        webbrowser.open_new("https://github.com/DilerFeed")

    def show_frame(self, frame):
        frame.tkraise()

    def open_axis_window(self, axis_var, axis_name):
        def detect_axis():
            nonlocal axis_detected, previous_values
            pygame.event.pump()
            significant_change_detected = False

            for i in range(self.joystick.get_numaxes()):
                value = self.joystick.get_axis(i)
                if abs(value - previous_values[i]) > 0.2:  # Сравниваем текущее значение с предыдущим
                    axis_detected = i
                    axis_label.config(text=f"Detected Axis: {axis_detected}")
                    significant_change_detected = True
                    previous_values[i] = value

            if not significant_change_detected:
                assign_window.after(50, detect_axis)  # Продолжаем проверять

        def apply_axis():
            axis_var.set(axis_detected)
            assign_window.destroy()

        def cancel():
            assign_window.destroy()

        axis_detected = axis_var.get()
        previous_values = [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]
        assign_window = tk.Toplevel(self.root)
        assign_window.title(f"Assign {axis_name} Axis")
        ttk.Label(assign_window, text=f"Move the {axis_name} or press a pedal.").pack(pady=10)
        axis_label = ttk.Label(assign_window, text=f"Detected Axis: {axis_detected}")
        axis_label.pack(pady=5)
        apply_button = ttk.Button(assign_window, text="Apply", command=apply_axis)
        apply_button.pack(side="left", padx=10, pady=10)
        cancel_button = ttk.Button(assign_window, text="Cancel", command=cancel)
        cancel_button.pack(side="right", padx=10, pady=10)

        detect_axis()  # Начинаем проверять сразу после открытия окна

    def open_button_window(self, button_var, description):
        def on_detect_button():
            pygame.event.pump()
            detected_button = -1
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    detected_button = i
                    break
            button_var.set(detected_button)
            detected_label.config(text=f"Detected Button: {detected_button}")
        def on_apply():
            button_var.set(button_var.get())
            button_window.destroy()
        button_window = tk.Toplevel(self.root)
        button_window.title(f"Detect {description}")
        ttk.Label(button_window, text=f"Press the {description}").pack(pady=5)
        detected_label = ttk.Label(button_window, text="Detected Button: -1")
        detected_label.pack(pady=5)
        ttk.Button(button_window, text="Detect Button", command=on_detect_button).pack(pady=5)
        ttk.Button(button_window, text="Apply", command=on_apply).pack(pady=5)
        ttk.Button(button_window, text="Cancel", command=button_window.destroy).pack(pady=5)

    def poll_joystick(self):
        self.update_joystick_list()
        if self.joystick:
            pygame.event.pump()
            raw_angle = self.joystick.get_axis(self.steering_axis.get())
            deadzone_value = self.deadzone.get()

            if abs(raw_angle) < deadzone_value:
                raw_angle = 0
            adjusted_angle = max(min(raw_angle, 1), -1)
            self.steering_angle.set(adjusted_angle)

            if self.combined_pedals.get():
                combined_value = self.joystick.get_axis(1)
                gas_value = -min(0, combined_value)
                brake_value = max(0, combined_value)
                self.gas_pedal.set(self.apply_deadzone(gas_value, deadzone_value))
                self.brake_pedal.set(self.apply_deadzone(brake_value, deadzone_value))
            else:
                if self.swap_pedals.get():
                    self.gas_pedal.set(self.apply_deadzone((1 - (self.joystick.get_axis(self.brake_axis.get()) + 1) / 2), deadzone_value))
                    self.brake_pedal.set(self.apply_deadzone((1 - (self.joystick.get_axis(self.gas_axis.get()) + 1) / 2), deadzone_value))
                else:
                    self.gas_pedal.set(self.apply_deadzone((1 - (self.joystick.get_axis(self.gas_axis.get()) + 1) / 2), deadzone_value))
                    self.brake_pedal.set(self.apply_deadzone((1 - (self.joystick.get_axis(self.brake_axis.get()) + 1) / 2), deadzone_value))

            if self.shift_up_button.get() != -1 and self.joystick.get_button(self.shift_up_button.get()):
                self.update_button_status(self.shift_up_status, "Shift Up Pressed")
            if self.shift_down_button.get() != -1 and self.joystick.get_button(self.shift_down_button.get()):
                self.update_button_status(self.shift_down_status, "Shift Down Pressed")
            if self.custom_button_1.get() != -1 and self.joystick.get_button(self.custom_button_1.get()):
                self.update_button_status(self.custom_button_1_status, "Custom Button 1 Pressed")
            if self.custom_button_2.get() != -1 and self.joystick.get_button(self.custom_button_2.get()):
                self.update_button_status(self.custom_button_2_status, "Custom Button 2 Pressed")
            if self.custom_button_3.get() != -1 and self.joystick.get_button(self.custom_button_3.get()):
                self.update_button_status(self.custom_button_3_status, "Custom Button 3 Pressed")
            if self.custom_button_4.get() != -1 and self.joystick.get_button(self.custom_button_4.get()):
                self.update_button_status(self.custom_button_4_status, "Custom Button 4 Pressed")

        self.root.after(50, self.poll_joystick)

    def update_joystick_list(self):
        joystick_names = [pygame.joystick.Joystick(i).get_name() for i in range(pygame.joystick.get_count())]
        self.joystick_menu['values'] = joystick_names
        if joystick_names:
            self.joystick_name.set(joystick_names[0])
            self.select_joystick(0)
        else:
            self.joystick_name.set("")

    def select_joystick(self, index):
        if index < pygame.joystick.get_count():
            self.joystick = pygame.joystick.Joystick(index)
            self.joystick.init()
        else:
            self.joystick = None

    def apply_deadzone(self, value, deadzone_value):
        return 0 if abs(value) < deadzone_value else value

    def update_button_status(self, status_var, text):
        status_var.set(text)
        self.root.after(1000, lambda: status_var.set(""))

    def init_flask(self):
        @self.app.before_request
        def log_request_info():
            self.app.logger.debug('Headers: %s', request.headers)
            self.app.logger.debug('Body: %s', request.get_data())

        @self.app.after_request
        def log_response_info(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            self.app.logger.debug('Response: %s', response.get_data())
            return response

        @self.app.route('/upload', methods=['POST'])
        def upload_image():
            file = request.files['file']
            image = Image.open(file.stream)
            self.original_image = image.copy()
            self.current_image = self.process_image(image, self.selected_size, self.fill_image)
            return "Image uploaded and processed", 200

        @self.app.route('/image', methods=['GET'])
        def get_image():
            if self.current_image is None:
                return "No image uploaded", 404

            pixels = self.current_image.load()
            width, height = self.current_image.size
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

        @self.app.route('/column', methods=['GET'])
        def get_column():
            if self.current_image is None:
                return "No image uploaded", 404

            pixels = self.current_image.load()
            width, height = self.current_image.size
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

        @self.app.route('/controller_data', methods=['GET'])
        def controller_data():
            data = {
                "steering_angle": self.steering_angle.get(),
                "gas_pedal": self.gas_pedal.get(),
                "brake_pedal": self.brake_pedal.get(),
                "shift_up": 1 if self.joystick.get_button(self.shift_up_button.get()) else 0,
                "shift_down": 1 if self.joystick.get_button(self.shift_down_button.get()) else 0,
                "custom_button_1": 1 if self.joystick.get_button(self.custom_button_1.get()) else 0,
                "custom_button_2": 1 if self.joystick.get_button(self.custom_button_2.get()) else 0,
                "custom_button_3": 1 if self.joystick.get_button(self.custom_button_3.get()) else 0,
                "custom_button_4": 1 if self.joystick.get_button(self.custom_button_4.get()) else 0
            }
            return '\n'.join([f'{key}={value}' for key, value in data.items()]), 200

        thread = threading.Thread(target=self.start_flask)
        thread.daemon = True
        thread.start()

    def start_flask(self):
        self.app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    App()
