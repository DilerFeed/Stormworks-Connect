import tkinter as tk
from tkinter import filedialog, StringVar, BooleanVar, DoubleVar, IntVar, Frame, Button, Label, Entry, Toplevel, Scrollbar, Listbox, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
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
import imageio
import time
import configparser
from bs4 import BeautifulSoup, SoupStrainer
import textwrap
from urllib.request import urlopen, Request
from io import BytesIO
import serial
import queue
import ast

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
        self.current_version = "1.3.0.0"
        self.suppress_update_notification = 'False'
        self.config_file = "config.ini"

        # Detect system theme
        system_theme = self.get_system_theme()

        # Initialize with detected theme
        super().__init__("Stormworks Connect", "sun-valley", system_theme)
        
        # Flask app initialization
        self.app = Flask(__name__)
        self.current_image = None
        self.original_image = None
        self.original_gif = None
        self.current_gif = None
        self.selected_gif_size = (32, 32)
        self.current_gif_animation_id = None
        self.gif_frames_data = []  # Add this line to store GIF frames data
        self.current_result_index = 0  # index to track the current result
        self.results_per_page = 3  # number of results on one page
        self.results_list = []  # a list to store all results
        self.current_page = 0  # Initializing the current_page variable
        self.result_text = []  # Initializing a variable to store search results
        self.page_content = []
        self.page_line_count = 10  # number of lines per page
        self.search_complete = False
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
        
        self.device_blocks = []
        # Arrays for input and output values
        self.digital_inputs = [0] * 4
        self.digital_outputs = [0] * 4
        self.boolean_inputs = [False] * 4
        self.boolean_outputs = [False] * 4
        self.arduino_handler = ArduinoHandler()
        # Start a thread to read data from Arduino
        self.read_arduino_thread = threading.Thread(target=self.read_arduino_data)
        self.read_arduino_thread.daemon = True
        self.read_arduino_thread.start()
        self.update_device_blocks()
        
        # Load images for tabs
        self.image_transmit_icon = ImageTk.PhotoImage(Image.open(resource_path("picture.png")))
        self.steering_wheel_icon = ImageTk.PhotoImage(Image.open(resource_path("steering-wheel.png")))
        self.info_icon = ImageTk.PhotoImage(Image.open(resource_path("info.png")))
        self.arduino_icon = ImageTk.PhotoImage(Image.open(resource_path("integrated.png")))

        self.create_widgets()
        self.poll_joystick()
        self.load_config()
        self.check_for_updates()
        
        self.root.geometry("800x600")
        self.root.update_idletasks()
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.root.minsize(int(self.root.winfo_width() * scaleFactor), int(self.root.winfo_height() * scaleFactor))
        self.root.resizable(True, True)
        
        self.root.iconphoto(False, tk.PhotoImage(file=resource_path('SC_cover.png')))
        
        self.run()
        
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if 'Settings' not in self.config.sections():
            self.config.add_section('Settings')
        if 'SteeringWheel' not in self.config.sections():
            self.config.add_section('SteeringWheel')
        if 'Arduino' not in self.config.sections():
            self.config.add_section('Arduino')
        
        # Load settings
        self.suppress_update_notification = self.config.getboolean('Settings', 'suppress_update_notification', fallback=False)
        
        self.deadzone.set(self.config.getfloat('SteeringWheel', 'deadzone', fallback=0.05))
        self.swap_pedals.set(self.config.getboolean('SteeringWheel', 'swap_pedals', fallback=False))
        self.combined_pedals.set(self.config.getboolean('SteeringWheel', 'combined_pedals', fallback=False))
        self.steering_axis.set(self.config.getint('SteeringWheel', 'steering_axis', fallback=0))
        self.gas_axis.set(self.config.getint('SteeringWheel', 'gas_axis', fallback=2))
        self.brake_axis.set(self.config.getint('SteeringWheel', 'brake_axis', fallback=1))
        self.shift_up_button.set(self.config.getint('SteeringWheel', 'shift_up_button', fallback=1))
        self.shift_down_button.set(self.config.getint('SteeringWheel', 'shift_down_button', fallback=0))
        self.custom_button_1.set(self.config.getint('SteeringWheel', 'custom_button_1', fallback=9))
        self.custom_button_2.set(self.config.getint('SteeringWheel', 'custom_button_2', fallback=8))
        self.custom_button_3.set(self.config.getint('SteeringWheel', 'custom_button_3', fallback=6))
        self.custom_button_4.set(self.config.getint('SteeringWheel', 'custom_button_4', fallback=7))
        self.update_swap_pedals_state()
        # Load Arduino blocks
        self.load_arduino_blocks()

    def save_config(self, save_arduino=False):
        self.config['Settings']['suppress_update_notification'] = str(self.suppress_update_notification)
        self.config['SteeringWheel']['deadzone'] = str(self.deadzone.get())
        self.config['SteeringWheel']['swap_pedals'] = str(self.swap_pedals.get())
        self.config['SteeringWheel']['combined_pedals'] = str(self.combined_pedals.get())
        self.config['SteeringWheel']['steering_axis'] = str(self.steering_axis.get())
        self.config['SteeringWheel']['gas_axis'] = str(self.gas_axis.get())
        self.config['SteeringWheel']['brake_axis'] = str(self.brake_axis.get())
        self.config['SteeringWheel']['shift_up_button'] = str(self.shift_up_button.get())
        self.config['SteeringWheel']['shift_down_button'] = str(self.shift_down_button.get())
        self.config['SteeringWheel']['custom_button_1'] = str(self.custom_button_1.get())
        self.config['SteeringWheel']['custom_button_2'] = str(self.custom_button_2.get())
        self.config['SteeringWheel']['custom_button_3'] = str(self.custom_button_3.get())
        self.config['SteeringWheel']['custom_button_4'] = str(self.custom_button_4.get())
        
        if save_arduino:
            # Save Arduino blocks
            self.save_arduino_blocks()

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
            
    def save_arduino_blocks(self):
        if 'Arduino' not in self.config.sections():
            self.config.add_section('Arduino')
        else:
            self.config.remove_section('Arduino')
            self.config.add_section('Arduino')
            
        for idx, block in enumerate(self.device_blocks):
            block_config = {
                'type': block['type'],
                'name': block['name']
            }
            if 'listbox_var' in block:
                block_config['listbox_var'] = block['listbox_var'].get()
            if 'listbox_var1' in block:
                block_config['listbox_var1'] = block['listbox_var1'].get()
            if 'listbox_var2' in block:
                block_config['listbox_var2'] = block['listbox_var2'].get()
            if 'assigned_output' in block:
                block_config['assigned_output'] = block['assigned_output']
            if 'line1_prefix' in block:
                block_config['line1_prefix'] = block['line1_prefix'].get()
            if 'line1_suffix' in block:
                block_config['line1_suffix'] = block['line1_suffix'].get()
            if 'line2_prefix' in block:
                block_config['line2_prefix'] = block['line2_prefix'].get()
            if 'line2_suffix' in block:
                block_config['line2_suffix'] = block['line2_suffix'].get()
            if 'tone_entry' in block:
                block_config['tone_entry'] = block['tone_entry'].get()
            if 'r_entry' in block:
                block_config['r_entry'] = block['r_entry'].get()
            if 'g_entry' in block:
                block_config['g_entry'] = block['g_entry'].get()
            if 'b_entry' in block:
                block_config['b_entry'] = block['b_entry'].get()

            self.config['Arduino'][f'block_{idx}'] = str(block_config)

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def load_arduino_blocks(self):
        if 'Arduino' in self.config.sections():
            print("Arduino section found in config")
            arduino_keys = sorted(self.config['Arduino'].keys())
            print(f"Arduino keys: {arduino_keys}")
            for key in arduino_keys:
                try:
                    if key in self.config['Arduino']:
                        block_data = self.config['Arduino'][key]
                        print(f"Loading block: {key} with data: {block_data}")
                        block_config = ast.literal_eval(block_data)
                        block_type = block_config.pop('type')
                        block_name = block_config.pop('name')
                        print(f"Creating block: {block_type} with name: {block_name}")

                        # Temporarily disable trace while loading configuration
                        disable_trace = True
                        self.add_device_block(block_type, save_config=False, disable_trace=disable_trace)
                        
                        block = self.device_blocks[-1]
                        for config_key, config_value in block_config.items():
                            print(f"Setting {config_key} to {config_value} in block {block_name}")
                            if config_key == 'listbox_var':
                                block['listbox_var'].set(config_value)
                            elif config_key == 'listbox_var1':
                                block['listbox_var1'].set(config_value)
                            elif config_key == 'listbox_var2':
                                block['listbox_var2'].set(config_value)
                            elif config_key == 'assigned_output':
                                block['assigned_output'] = config_value
                                block['frame'].children['!label2'].config(text=config_value)
                            elif config_key == 'line1_prefix':
                                block['line1_prefix'].delete(0, tk.END)  # Clear any default text
                                block['line1_prefix'].insert(0, config_value)
                            elif config_key == 'line1_suffix':
                                block['line1_suffix'].delete(0, tk.END)  # Clear any default text
                                block['line1_suffix'].insert(0, config_value)
                            elif config_key == 'line2_prefix':
                                block['line2_prefix'].delete(0, tk.END)  # Clear any default text
                                block['line2_prefix'].insert(0, config_value)
                            elif config_key == 'line2_suffix':
                                block['line2_suffix'].delete(0, tk.END)  # Clear any default text
                                block['line2_suffix'].insert(0, config_value)
                            elif config_key == 'tone_entry':
                                block['tone_entry'].delete(0, tk.END)  # Clear any default text
                                block['tone_entry'].insert(0, config_value)
                            elif config_key == 'r_entry':
                                block['r_entry'].delete(0, tk.END)  # Clear any default text
                                block['r_entry'].insert(0, config_value)
                            elif config_key == 'g_entry':
                                block['g_entry'].delete(0, tk.END)  # Clear any default text
                                block['g_entry'].insert(0, config_value)
                            elif config_key == 'b_entry':
                                block['b_entry'].delete(0, tk.END)  # Clear any default text
                                block['b_entry'].insert(0, config_value)
                        
                        # Re-enable trace after loading configuration
                        disable_trace = False
                        self.reenable_trace(block)

                    else:
                        print(f"Key {key} not found in Arduino section")
                except KeyError as ke:
                    print(f"KeyError loading Arduino block {key}: {ke}")
                except SyntaxError as se:
                    print(f"SyntaxError loading Arduino block {key}: {se}")
                except Exception as e:
                    print(f"Error loading Arduino block {key}: {e}")

    def reenable_trace(self, block):
        if 'listbox_var' in block:
            block['listbox_var'].trace_add("write", lambda *args: self.save_config(save_arduino=True))
        if 'listbox_var1' in block:
            block['listbox_var1'].trace_add("write", lambda *args: self.save_config(save_arduino=True))
        if 'listbox_var2' in block:
            block['listbox_var2'].trace_add("write", lambda *args: self.save_config(save_arduino=True))
        if 'line1_prefix' in block:
            block['line1_prefix'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'line1_suffix' in block:
            block['line1_suffix'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'line2_prefix' in block:
            block['line2_prefix'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'line2_suffix' in block:
            block['line2_suffix'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'tone_entry' in block:
            block['tone_entry'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'r_entry' in block:
            block['r_entry'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'g_entry' in block:
            block['g_entry'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))
        if 'b_entry' in block:
            block['b_entry'].bind("<FocusOut>", lambda e: self.save_config(save_arduino=True))

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
        if self.suppress_update_notification:
            logging.debug("Update check is suppressed by user settings.")
            return

        try:
            logging.debug("Checking for updates...")
            response = requests.get("https://dilerfeed.github.io/Stormworks-Connect/version.json")
            logging.debug(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info["version"]
                download_url = version_info["download_url"]
                
                logging.debug(f"Latest version available: {latest_version}")
                logging.debug(f"Current version: {self.current_version}")
                
                if version.parse(latest_version) > version.parse(self.current_version):
                    logging.debug("A new version is available. Showing update notification.")
                    self.show_update_notification(download_url)
                else:
                    logging.debug("No new version available.")
            else:
                logging.error(f"Failed to fetch update information. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error checking for updates: {e}")

    def show_update_notification(self, download_url):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Available")
        update_window.geometry("350x250")

        label = ttk.Label(update_window, text="A new version of the program is available!")
        label.pack(pady=10)

        download_button = ttk.Button(update_window, text="Download", command=lambda: self.open_download_link(download_url))
        download_button.pack(pady=5)

        def close_and_remember():
            self.config['Settings']['suppress_update_notification'] = 'True'
            self.suppress_update_notification = True
            self.save_config()
            update_window.destroy()

        close_button = ttk.Button(update_window, text="Close", command=update_window.destroy)
        close_button.pack(pady=5)

        suppress_button = ttk.Button(update_window, text="Don't remind me again", command=close_and_remember)
        suppress_button.pack(pady=5)
        
    def create_custom_button(self, parent, text, command):
        # Creating a custom button using a regular tkinter button
        button = tk.Button(parent, text=text, command=command, bg='gold', fg='black', font=('Arial', 16, 'bold'),
                        activebackground='black', activeforeground='gold', relief='flat', borderwidth=2)
        button.pack(pady=20, padx=20)
        
        def on_enter(event):
            button.config(bg='black', fg='gold')

        def on_leave(event):
            button.config(bg='gold', fg='black')

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def create_widgets(self):
        # Frames for different tabs
        self.tab_control = ttk.Notebook(self.root)
        self.image_transmit_frame = ttk.Frame(self.tab_control)
        self.steering_wheel_frame = ttk.Frame(self.tab_control)
        self.arduino_frame = ttk.Frame(self.tab_control)  # Add new frame for Arduino settings
        self.info_frame = ttk.Frame(self.tab_control)

        self.tab_control.add(self.image_transmit_frame, text=" Image transmit", image=self.image_transmit_icon, compound='left')
        self.tab_control.add(self.steering_wheel_frame, text=" Steering wheel", image=self.steering_wheel_icon, compound='left')
        self.tab_control.add(self.arduino_frame, text=" Arduino", image=self.arduino_icon, compound='left')  # Add Arduino tab
        self.tab_control.add(self.info_frame, text=" Info", image=self.info_icon, compound='left')
        self.tab_control.pack(expand=1, fill="both")

        # Frame for image and gif transmit sections
        image_gif_frame = ttk.Frame(self.image_transmit_frame)
        image_gif_frame.pack(expand=1, fill="both")

        # Image transmit section
        image_frame = ttk.Frame(image_gif_frame)
        image_frame.pack(side="left", fill="both", expand=True, padx=(10, 5))

        ttk.Label(image_frame, text="Image Transmit", font=("Arial", 14)).pack(pady=10)
        
        self.monitor_size_var = tk.StringVar(value="9x5")
        monitor_size_menu = ttk.Combobox(image_frame, textvariable=self.monitor_size_var, values=list(self.monitor_sizes.keys()), state="readonly")
        monitor_size_menu.bind("<<ComboboxSelected>>", self.on_monitor_size_change)
        monitor_size_menu.pack(pady=10)

        self.fill_var = tk.BooleanVar(value=False)
        fill_checkbutton = ttk.Checkbutton(image_frame, text="Fill", variable=self.fill_var, command=self.on_fill_option_change)
        fill_checkbutton.pack(pady=5)

        upload_button = ttk.Button(image_frame, text="Upload image", command=self.open_file)
        upload_button.pack(pady=10)

        ttk.Label(image_frame, text="or upload image from URL:", font=("Arial", 10)).pack(pady=5)
        self.image_url_var = tk.StringVar()
        image_url_entry = ttk.Entry(image_frame, textvariable=self.image_url_var, width=50)
        image_url_entry.pack(pady=5)
        load_image_button = ttk.Button(image_frame, text="Upload image from URL", command=self.load_image_from_url_click)
        load_image_button.pack(pady=5)
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(pady=10)

        self.status_label = ttk.Label(image_frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Separator (vertical)
        ttk.Separator(image_gif_frame, orient='vertical').pack(side="left", fill='y', padx=5)

        # GIF transmit section
        gif_frame = ttk.Frame(image_gif_frame)
        gif_frame.pack(side="left", fill="both", expand=True, padx=(5, 10))

        ttk.Label(gif_frame, text="GIF Transmit", font=("Arial", 14)).pack(pady=10)

        self.gif_monitor_size_var = tk.StringVar(value="1x1")
        gif_monitor_size_menu = ttk.Combobox(gif_frame, textvariable=self.gif_monitor_size_var, values=list(self.monitor_sizes.keys()), state="readonly")
        gif_monitor_size_menu.bind("<<ComboboxSelected>>", self.on_gif_monitor_size_change)
        gif_monitor_size_menu.pack(pady=10)

        self.gif_fill_var = tk.BooleanVar(value=False)
        gif_fill_checkbutton = ttk.Checkbutton(gif_frame, text="Fill GIF", variable=self.gif_fill_var, command=self.on_gif_fill_option_change)
        gif_fill_checkbutton.pack(pady=5)

        upload_gif_button = ttk.Button(gif_frame, text="Upload GIF", command=self.open_gif_file)
        upload_gif_button.pack(pady=10)

        ttk.Label(gif_frame, text="or upload GIF from URL:", font=("Arial", 10)).pack(pady=5)
        self.gif_url_var = tk.StringVar()
        gif_url_entry = ttk.Entry(gif_frame, textvariable=self.gif_url_var, width=50)
        gif_url_entry.pack(pady=5)
        load_gif_button = ttk.Button(gif_frame, text="Upload GIF from URL", command=self.load_gif_from_url_click)
        load_gif_button.pack(pady=5)
        
        self.gif_label = ttk.Label(gif_frame)
        self.gif_label.pack(pady=10)

        self.gif_status_label = ttk.Label(gif_frame, text="", font=("Arial", 12))
        self.gif_status_label.pack(pady=5)
        
        # Call method to create Arduino tab widgets
        self.create_arduino_widgets()

        # Info tab with two sections: Info and Features
        info_features_frame = ttk.Frame(self.info_frame)
        info_features_frame.pack(expand=1, fill="both")

        # Info section
        info_frame = ttk.Frame(info_features_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=(10, 5))
        
        ttk.Label(info_frame, text="Info", font=("Arial", 14)).pack(pady=10)

        server_status = ttk.Label(info_frame, text="Server is running on port 5000", foreground="green", font=("Arial", 12))
        server_status.pack(pady=5)

        program_title = ttk.Label(info_frame, text="Stormworks Connect v1.3.0.0", font=("Arial", 16))
        program_title.pack(pady=5)

        author_info = ttk.Label(info_frame, text="© Hlib Ishchenko 2024", font=("Arial", 10))
        author_info.pack(pady=5)

        steam_profile = ttk.Label(info_frame, text="Steam Profile", foreground="blue", cursor="hand2", font=("Arial", 12))
        steam_profile.pack(pady=5)
        steam_profile.bind("<Button-1>", self.open_steam_profile)

        github_profile = ttk.Label(info_frame, text="GitHub Profile", foreground="blue", cursor="hand2", font=("Arial", 12))
        github_profile.pack(pady=5)
        github_profile.bind("<Button-1>", self.open_github_profile)
        
        ttk.Button(info_frame, text="Switch to Dark Theme", command=self.switch_to_dark_theme).pack(pady=10)
        ttk.Button(info_frame, text="Switch to Light Theme", command=self.switch_to_light_theme).pack(pady=10)

        # Separator (vertical)
        ttk.Separator(info_features_frame, orient='vertical').pack(side="left", fill='y', padx=5)

        # Features section
        features_frame = ttk.Frame(info_features_frame)
        features_frame.pack(side="left", fill="both", expand=True, padx=(5, 10))

        ttk.Label(features_frame, text="Features", font=("Arial", 14)).pack(pady=10)

        features = [
            ("Image Transmit", "https://steamcommunity.com/sharedfiles/filedetails/?id=3256896125"),
            ("GIF Transmit", "https://steamcommunity.com/sharedfiles/filedetails/?id=3262978714"),
            ("Steering Wheel Support", "https://steamcommunity.com/sharedfiles/filedetails/?id=3261140680"),
            ("In-game text web browser", "https://steamcommunity.com/sharedfiles/filedetails/?id=3267509700"),
            ("Arduino Support", "https://steamcommunity.com/sharedfiles/filedetails/?id=3288246525"),
        ]

        for feature, link in features:
            feature_label = ttk.Label(features_frame, text=f"• {feature}", foreground="blue", cursor="hand2", font=("Arial", 12))
            feature_label.pack(pady=2, anchor='w')
            feature_label.bind("<Button-1>", lambda e, url=link: webbrowser.open_new(url))

        small_notice = ttk.Label(features_frame, text="Clicking on a feature will open the relevant controller page in the browser.", font=("Arial", 8))
        small_notice.pack(pady=5, anchor='w')

        # Steering wheel tab
        ttk.Label(self.steering_wheel_frame, text="Select Joystick:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.joystick_menu = ttk.Combobox(self.steering_wheel_frame, textvariable=self.joystick_name, state="readonly")
        self.joystick_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Steering Angle:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.steering_angle).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Gas Pedal:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.gas_pedal).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Current Brake Pedal:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.steering_wheel_frame, textvariable=self.brake_pedal).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.steering_wheel_frame, text="Deadzone:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        deadzone_scale = ttk.Scale(self.steering_wheel_frame, from_=0, to=0.2, orient=tk.HORIZONTAL, variable=self.deadzone, command=lambda x: self.save_config())
        deadzone_scale.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        deadzone_entry = ttk.Entry(self.steering_wheel_frame, textvariable=self.deadzone)
        deadzone_entry.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self.swap_pedals_checkbutton = ttk.Checkbutton(self.steering_wheel_frame, text="Swap Gas and Brake Pedals", variable=self.swap_pedals, command=self.save_config)
        self.swap_pedals_checkbutton.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        ttk.Checkbutton(self.steering_wheel_frame, text="Combined Pedals", variable=self.combined_pedals, command=lambda: [self.update_swap_pedals_state(), self.save_config()]).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        self.create_joystick_buttons()

        # Add labels for shift and custom button statuses
        self.create_joystick_button("Shift Up Button", 6, self.shift_up_button, self.shift_up_status)
        self.create_joystick_button("Shift Down Button", 7, self.shift_down_button, self.shift_down_status)
        self.create_joystick_button("Custom Button 1", 8, self.custom_button_1, self.custom_button_1_status)
        self.create_joystick_button("Custom Button 2", 9, self.custom_button_2, self.custom_button_2_status)
        self.create_joystick_button("Custom Button 3", 10, self.custom_button_3, self.custom_button_3_status)
        self.create_joystick_button("Custom Button 4", 11, self.custom_button_4, self.custom_button_4_status)
        
    def create_arduino_widgets(self):
        # Create a frame for the Arduino tab
        arduino_tab_frame = ttk.Frame(self.arduino_frame)
        arduino_tab_frame.pack(expand=1, fill="both")

        # Add a '+' button to add new device blocks
        add_device_button = ttk.Button(arduino_tab_frame, text="+", command=self.show_device_selection)
        add_device_button.pack(pady=5)
        
        self.arduino_warning_placeholder = tk.Frame(arduino_tab_frame)
        self.arduino_warning_placeholder.pack(pady=5)

        # Create a canvas and a vertical scrollbar
        canvas = tk.Canvas(arduino_tab_frame)
        scrollbar = ttk.Scrollbar(arduino_tab_frame, orient="vertical", command=canvas.yview)
        self.device_blocks_frame = ttk.Frame(canvas)

        # Bind the device_blocks_frame width to the canvas width
        self.device_blocks_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig('frame', width=canvas.winfo_width()))

        canvas.create_window((0, 0), window=self.device_blocks_frame, anchor="nw", tags='frame')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # List to hold references to device blocks
        self.device_blocks = []
        
    def create_empty_icon(self, size):
        return ImageTk.PhotoImage(Image.new("RGBA", size, (255, 255, 255, 0)))

    def show_device_selection(self):
        # Open a new window to select the device type
        selection_window = Toplevel(self.root)
        selection_window.title("Select Device")
        selection_window.geometry("300x375")  # Adjusted window size

        # List of available devices
        devices = ["LED", "Button", "Potentiometer", "Active Buzzer", "4 digit 7-segment", "1 digit 7-segment"]

        # Use Treeview instead of Listbox
        device_tree = ttk.Treeview(selection_window, show="tree")
        device_tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Increase the font size for Treeview items
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12))  # Set the font size to 16
        
        # Create empty icon
        self.empty_icon = self.create_empty_icon((24, 24))

        # Add devices to Treeview
        for device in devices:
            device_tree.insert("", "end", text=device, image=self.empty_icon)

        # Align the text and image to be next to each other
        style.configure("Treeview", rowheight=24, font=("Arial", 12))  # Ensure the row height matches the icon
        
        # Apply zebra-like pattern manually
        for index, item in enumerate(device_tree.get_children()):
            if 'disabled' in device_tree.item(item, 'tags'):
                bg_color = 'darkgray' if index % 2 == 0 else 'black'
                device_tree.tag_configure('disabled', background=bg_color)

        def on_select_device():
            selected_item = device_tree.selection()
            if selected_item:
                selected_device = device_tree.item(selected_item, "text")
                self.add_device_block(selected_device)
                selection_window.destroy()

        select_button = ttk.Button(selection_window, text="Select", command=on_select_device)
        select_button.pack(pady=5)

        # Bind the treeview select event
        device_tree.bind("<ButtonRelease-1>", lambda event: device_tree.selection())  # just select the element

        # Custom tag configuration for aligning text and image
        style.configure("Treeview.Item", compound="right")  # Align image to the right of the text

    def get_next_device_index(self, device_type):
        # Get all current indices for the specified device type
        current_indices = [int(device['name'].split()[-1]) for device in self.device_blocks if device['type'] == device_type]
        # Find the smallest available index
        index = 1
        while index in current_indices:
            index += 1
        return index

    def get_used_outputs(self):
        used_boolean_outputs = set()
        used_number_outputs = set()
        for device in self.device_blocks:
            if 'listbox_var' in device:
                if 'Boolean Output' in device['listbox_var'].get():
                    used_boolean_outputs.add(device['listbox_var'].get())
                elif 'Number Output' in device['listbox_var'].get():
                    used_number_outputs.add(device['listbox_var'].get())
            elif 'listbox_vars' in device:
                for var in device['listbox_vars']:
                    if 'Boolean Output' in var.get():
                        used_boolean_outputs.add(var.get())
                    elif 'Number Output' in var.get():
                        used_number_outputs.add(var.get())
            elif 'assigned_output' in device:
                if 'Boolean Output' in device['assigned_output']:
                    used_boolean_outputs.add(device['assigned_output'])
                elif 'Number Output' in device['assigned_output']:
                    used_number_outputs.add(device['assigned_output'])
        return used_boolean_outputs, used_number_outputs

    def add_device_block(self, device_type, save_config=True, disable_trace=False):
        if len(self.device_blocks) >= 16:
            return  # Limit to 16 blocks

        # Get the next available index for the device type
        device_index = self.get_next_device_index(device_type)

        # Create a new frame for the device block
        device_block_frame = ttk.Frame(self.device_blocks_frame, relief="raised", borderwidth=1)
        device_block_frame.pack(fill="x", pady=5, padx=10)

        # Configure grid layout for device_block_frame
        device_block_frame.columnconfigure(0, weight=0)
        device_block_frame.columnconfigure(1, weight=0)
        device_block_frame.columnconfigure(2, weight=1)  # This allows the frame to expand
        device_block_frame.columnconfigure(3, weight=0)
        device_block_frame.columnconfigure(4, weight=0)
        device_block_frame.columnconfigure(5, weight=0)
        device_block_frame.columnconfigure(6, weight=0)
        device_block_frame.columnconfigure(7, weight=0)
        device_block_frame.columnconfigure(8, weight=0)
        device_block_frame.columnconfigure(9, weight=0)

        # Add label for the device name and index
        device_name_label = ttk.Label(device_block_frame, text=f"{device_type} {device_index}")
        device_name_label.grid(row=0, column=0, rowspan=1, padx=5, pady=5, sticky="w")

        # Add vertical separator
        separator = ttk.Separator(device_block_frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=1, sticky="ns", padx=2, pady=5)

        # Add delete button for the device block
        delete_button = ttk.Button(device_block_frame, text="-", width=2, command=lambda: self.delete_device_block(device_block_frame))
        delete_button.grid(row=0, column=9, rowspan=2 if device_type == "LCD" else 1, padx=(0, 5), pady=5, sticky="e")

        # Create a dictionary to store references to the widgets
        block_widgets = {
            "frame": device_block_frame,
            "type": device_type,
            "name": f"{device_type} {device_index}"
        }

        # Add functionality for each device type
        if device_type == "LED":
            status_label = ttk.Label(device_block_frame, text="Status: inactive")
            status_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["status_label"] = status_label

            separator1 = ttk.Separator(device_block_frame, orient='vertical')
            separator1.grid(row=0, column=3, padx=2, pady=5, sticky="ns")

            test_button = ttk.Button(device_block_frame, text="Test", command=lambda: self.test_led(status_label, device_index))
            test_button.grid(row=0, column=4, padx=(0, 5), pady=5, sticky="e")

            separator2 = ttk.Separator(device_block_frame, orient='vertical')
            separator2.grid(row=0, column=5, padx=2, pady=5, sticky="ns")

        elif device_type == "Button":
            status_label = ttk.Label(device_block_frame, text="Status: not pressed")
            status_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["status_label"] = status_label

            separator = ttk.Separator(device_block_frame, orient='vertical')
            separator.grid(row=0, column=3, padx=2, pady=5, sticky="ns")
            
        elif device_type == "Potentiometer":
            status_label = ttk.Label(device_block_frame, text="Value: 0")
            status_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["value_label"] = status_label

            separator = ttk.Separator(device_block_frame, orient='vertical')
            separator.grid(row=0, column=3, padx=2, pady=5, sticky="ns")

        elif device_type == "Active Buzzer":
            status_label = ttk.Label(device_block_frame, text="Status: inactive")
            status_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["status_label"] = status_label

            separator1 = ttk.Separator(device_block_frame, orient='vertical')
            separator1.grid(row=0, column=3, padx=2, pady=5, sticky="ns")

            test_button = ttk.Button(device_block_frame, text="Test", command=lambda: self.test_buzzer(status_label, None, device_index, active=True))
            test_button.grid(row=0, column=4, padx=(0, 5), pady=5, sticky="e")

            separator2 = ttk.Separator(device_block_frame, orient='vertical')
            separator2.grid(row=0, column=5, padx=2, pady=5, sticky="ns")
            
        elif device_type == "4 digit 7-segment":
            value_label = ttk.Label(device_block_frame, text="Value: 0")
            value_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["value_label"] = value_label

            separator = ttk.Separator(device_block_frame, orient='vertical')
            separator.grid(row=0, column=3, padx=2, pady=5, sticky="ns")
            
        elif device_type == "1 digit 7-segment":
            value_label = ttk.Label(device_block_frame, text="Value: 0")
            value_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
            block_widgets["value_label"] = value_label

            separator = ttk.Separator(device_block_frame, orient='vertical')
            separator.grid(row=0, column=3, padx=2, pady=5, sticky="ns")

        # Add label for displaying assigned output/input
        used_boolean_outputs, used_number_outputs = self.get_used_outputs()

        if device_type in ["LED", "Active Buzzer"]:
            io_options = ["Boolean Input 1", "Boolean Input 2", "Boolean Input 3", "Boolean Input 4"]
            listbox_var = tk.StringVar(value=io_options[0])
            listbox = ttk.Combobox(device_block_frame, textvariable=listbox_var, values=io_options, state="readonly")
            listbox.grid(row=0, column=8, padx=(0, 5), pady=5, sticky="e")
            block_widgets["listbox_var"] = listbox_var
            if not disable_trace:
                listbox_var.trace_add("write", lambda *args: self.save_config(save_arduino=True))

        elif device_type in ["Button"]:
            io_options = ["Boolean Output 1", "Boolean Output 2", "Boolean Output 3", "Boolean Output 4"]
            available_outputs = [output for output in io_options if output not in used_boolean_outputs]
            if not available_outputs:
                tk.messagebox.showerror("Error", "All Boolean Outputs are used.")
                device_block_frame.destroy()
                return
            assigned_output = available_outputs[0]
            output_label = ttk.Label(device_block_frame, text=assigned_output)
            output_label.grid(row=0, column=8, padx=(0, 5), pady=5, sticky="e")
            block_widgets["assigned_output"] = assigned_output
            # If there's a UI element to change assigned_output, add the save_config call there

        elif device_type in ["Potentiometer"]:
            io_options = ["Number Output 1", "Number Output 2", "Number Output 3", "Number Output 4"]
            available_outputs = [output for output in io_options if output not in used_number_outputs]
            if not available_outputs:
                tk.messagebox.showerror("Error", "All Number Outputs are used.")
                device_block_frame.destroy()
                return
            assigned_output = available_outputs[0]
            output_label = ttk.Label(device_block_frame, text=assigned_output)
            output_label.grid(row=0, column=8, padx=(0, 5), pady=5, sticky="e")
            block_widgets["assigned_output"] = assigned_output
            # If there's a UI element to change assigned_output, add the save_config call there
                
        elif device_type in ["4 digit 7-segment", "1 digit 7-segment"]:
            io_options = ["Number Input 1", "Number Input 2", "Number Input 3", "Number Input 4"]
            listbox_var = tk.StringVar(value=io_options[0])
            listbox = ttk.Combobox(device_block_frame, textvariable=listbox_var, values=io_options, state="readonly")
            listbox.grid(row=0, column=4, padx=(0, 5), pady=5, sticky="e")
            block_widgets["listbox_var"] = listbox_var
            if not disable_trace:
                listbox_var.trace_add("write", lambda *args: self.save_config(save_arduino=True))

        # Store the device block information
        self.device_blocks.append(block_widgets)
        if save_config:
            self.save_config(save_arduino=True)

    def delete_device_block(self, device_block_frame):
        for device in self.device_blocks:
            if device['frame'] == device_block_frame:
                if 'assigned_output' in device:
                    assigned_output = device['assigned_output']
                    if 'Boolean Output' in assigned_output:
                        used_boolean_outputs = self.get_used_outputs()[0]
                        used_boolean_outputs.remove(assigned_output)
                    elif 'Number Output' in assigned_output:
                        used_number_outputs = self.get_used_outputs()[1]
                        used_number_outputs.remove(assigned_output)
                self.device_blocks.remove(device)
                device_block_frame.destroy()
                
                self.save_config(save_arduino=True)
                break

    def read_arduino_data(self):
        while True:
            data = self.arduino_handler.read_from_arduino()
            if data:
                self.process_arduino_data(data)

    def process_arduino_data(self, data):
        if data.startswith("BUTTON"):
            button_index = int(data.split(":")[0][-1])
            status = data.split(":")[1]
            for block in self.device_blocks:
                if block['type'] == 'Button' and block['name'].endswith(str(button_index)):
                    assigned_output = block['assigned_output']
                    output_index = int(assigned_output.split()[-1]) - 1
                    self.boolean_outputs[output_index] = (status == "PRESSED")
                    
                    # Reset the button value after a second if a new value does not arrive
                    if hasattr(self, f"button_timer_{button_index}"):
                        self.root.after_cancel(getattr(self, f"button_timer_{button_index}"))
                    
                    setattr(self, f"button_timer_{button_index}", self.root.after(1000, lambda: self.reset_button_output(output_index)))
                    break
        elif data.startswith("POTENTIOMETER"):
            pot_index = int(data.split(":")[0][-1])
            value = int(data.split(":")[1])
            for block in self.device_blocks:
                if block['type'] == 'Potentiometer' and block['name'].endswith(str(pot_index)):
                    assigned_output = block['assigned_output']
                    output_index = int(assigned_output.split()[-1]) - 1
                    self.digital_outputs[output_index] = value
                    break
                
    def reset_button_output(self, output_index):
        self.boolean_outputs[output_index] = False

    def reset_keypad_output(self, output_index):
        self.digital_outputs[output_index] = 0
                
    def reset_button_and_keypad_states(self):
        for block in self.device_blocks:
            if block['type'] == 'Button':
                assigned_output = block['assigned_output']
                output_index = int(assigned_output.split()[-1]) - 1
                self.boolean_outputs[output_index] = False

    def test_led(self, status_label, device_index):
        self.arduino_handler.send_to_arduino(f"LED{device_index}:1")
        status_label.config(text="Status: active")
        self.root.after(1000, lambda: self.arduino_handler.send_to_arduino(f"LED{device_index}:0"))
        self.root.after(1000, lambda: status_label.config(text="Status: inactive"))

    def test_buzzer(self, status_label, tone_entry=None, device_index=None, active=False):
        if active:
            self.arduino_handler.send_to_arduino(f"ACTIVE_BUZZER{device_index}:1")
            status_label.config(text="Status: active")
            self.root.after(1000, lambda: self.arduino_handler.send_to_arduino(f"ACTIVE_BUZZER{device_index}:0"))

        self.root.after(1000, lambda: status_label.config(text="Status: inactive"))
        
    def update_device_blocks(self):
        for block in self.device_blocks:
            if block['type'] == 'LED':
                assigned_input = block["listbox_var"].get()
                index = int(assigned_input.split()[-1]) - 1
                status = 'active' if self.boolean_inputs[index] else 'inactive'
                block['status_label'].config(text=f"Status: {status}")
                self.arduino_handler.send_to_arduino(f"LED{block['name'].split()[-1]}:{1 if self.boolean_inputs[index] else 0}")

            elif block['type'] == 'Button':
                assigned_output = block["assigned_output"]
                index = int(assigned_output.split()[-1]) - 1
                status = 'pressed' if self.boolean_outputs[index] else 'not pressed'
                block['status_label'].config(text=f"Status: {status}")

            elif block['type'] == 'Potentiometer':
                assigned_output = block["assigned_output"]
                index = int(assigned_output.split()[-1]) - 1
                block['value_label'].config(text=f"Value: {self.digital_outputs[index]}")

            elif block['type'] == 'Active Buzzer':
                assigned_input = block["listbox_var"].get()
                index = int(assigned_input.split()[-1]) - 1
                status = 'active' if self.boolean_inputs[index] else 'inactive'
                block['status_label'].config(text=f"Status: {status}")
                self.arduino_handler.send_to_arduino(f"ACTIVE_BUZZER{block['name'].split()[-1]}:{1 if self.boolean_inputs[index] else 0}")
                
            elif block['type'] == '4 digit 7-segment':
                assigned_input = block["listbox_var"].get()
                index = int(assigned_input.split()[-1]) - 1
                value = self.digital_inputs[index]
                # Converting the value for display
                if value >= 0:
                    if value >= 1000:
                        display_value = f"{int(value)}"  # Leave only the whole part
                    elif value >= 100:
                        display_value = f"{value:.1f}"  # Leave one digit after the dot
                    else:
                        display_value = f"{value:.2f}"  # Leave two digits after the dot
                else:
                    if value <= -100:
                        display_value = f"{int(value)}"
                    elif value <= -10:
                        display_value = f"{value:.1f}"
                    else:
                        display_value = f"{value:.2f}"

                block['value_label'].config(text=f"Value: {display_value}")
                self.arduino_handler.send_to_arduino(f"4SEGMENT{block['name'].split()[-1]}:{display_value}")
                
            elif block['type'] == '1 digit 7-segment':
                assigned_input = block["listbox_var"].get()
                index = int(assigned_input.split()[-1]) - 1
                value = self.digital_inputs[index]
                # Converting the value for display
                if value >= 0:
                    display_value = str(int(value)) if value < 10 else str(int(value // 10))
                else:
                    display_value = '-'
                block['value_label'].config(text=f"Value: {display_value}")
                self.arduino_handler.send_to_arduino(f"1SEGMENT{block['name'].split()[-1]}:{display_value}")

        self.root.after(1000, self.update_device_blocks)
    
    def support_load_and_play_gif(self, gif_path):
        gif_image = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(gif_image)]

        def update_frame(index):
            frame = frames[index]
            self.support_gif_label.config(image=frame)
            self.root.after(400, update_frame, (index + 1) % len(frames))

        self.root.after(0, update_frame, 0)
        
    def update_swap_pedals_state(self):
        if self.combined_pedals.get():
            self.swap_pedals.set(False)
            self.swap_pedals_checkbutton.config(state="disabled")
        else:
            self.swap_pedals_checkbutton.config(state="normal")
        self.save_config()

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
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            image = Image.open(file_path)
            self.original_image = image.copy()
            self.current_image = self.process_static_image(image, self.selected_size, self.fill_image)
            self.update_display_image()

    def process_static_image(self, image, size, fill):
        if fill:
            image = image.resize(size, Image.Resampling.LANCZOS)
        else:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        return image

    def update_display_image(self):
        if self.original_image:
            self.current_image = self.process_static_image(self.original_image.copy(), self.selected_size, self.fill_image)
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
        
    def open_download_link(self, link):
        webbrowser.open_new(link)

    def show_frame(self, frame):
        frame.tkraise()
        
    def open_gif_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
        if file_path:
            gif = imageio.mimread(file_path)
            self.original_gif = gif
            self.update_gif_display_and_data()

    def update_gif_display_and_data(self):
        if self.original_gif:
            self.current_gif = [self.process_gif_frame(frame, self.selected_gif_size, self.gif_fill_var.get()) for frame in self.original_gif]
            self.gif_frames_data = self.prepare_gif_data(self.current_gif)  # Prepare GIF data for transmission
            self.update_display_gif()

    def process_gif_frame(self, frame, size, fill):
        image = Image.fromarray(frame)
        if fill:
            image = image.resize(size, Image.Resampling.LANCZOS)
        else:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        return image

    def prepare_gif_data(self, frames):
        gif_data = []
        for frame in frames:
            pixels = frame.load()
            width, height = frame.size
            frame_data = []
            for y in range(height):
                row = []
                for x in range(width):
                    r, g, b = pixels[x, y][:3]
                    pixel_str = f"{r} {g} {b}"
                    row.append(pixel_str)
                frame_data.append(",".join(row))
            gif_data.append("\n".join(frame_data))
        return gif_data

    def update_display_gif(self):
        if self.original_gif:
            self.stop_current_gif_animation()  # Stop the previous animation
            gif_frames = [ImageTk.PhotoImage(frame) for frame in self.current_gif]
            self.gif_label.config(image=gif_frames[0])
            self.gif_label.image = gif_frames
            self.animate_gif(gif_frames)
            self.gif_status_label.config(text="GIF loaded")

    def animate_gif(self, frames):
        def update(index):
            frame = frames[index]
            self.gif_label.config(image=frame)
            self.current_gif_animation_id = self.root.after(100, update, (index + 1) % len(frames))
        self.current_gif_animation_id = self.root.after(0, update, 0)

    def stop_current_gif_animation(self):
        if self.current_gif_animation_id is not None:
            self.root.after_cancel(self.current_gif_animation_id)
            self.current_gif_animation_id = None

    def on_gif_monitor_size_change(self, event):
        self.selected_gif_size = self.monitor_sizes[self.gif_monitor_size_var.get()]
        self.update_gif_display_and_data()

    def on_gif_fill_option_change(self):
        self.update_gif_display_and_data()
        
    def load_image_from_url(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = Request(url, headers=headers)
            with urlopen(req) as response:
                image_data = response.read()
                image = Image.open(BytesIO(image_data))
                if image.format.lower() not in ["png", "jpeg", "jpg"]:
                    self.status_label.config(text="Invalid image format")
                    return None
                return image
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {e}")
            return None

    def load_gif_from_url(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = Request(url, headers=headers)
            with urlopen(req) as response:
                gif_data = response.read()
                gif = imageio.mimread(BytesIO(gif_data))
                return gif
        except Exception as e:
            self.gif_status_label.config(text=f"Error loading GIF: {e}")
            return None
        
    def load_image_from_url_click(self):
        url = self.image_url_var.get()
        image = self.load_image_from_url(url)
        if image:
            self.original_image = image.copy()
            self.current_image = self.process_static_image(image, self.selected_size, self.fill_image)
            self.update_display_image()

    def load_gif_from_url_click(self):
        url = self.gif_url_var.get()
        gif = self.load_gif_from_url(url)
        if gif:
            self.original_gif = gif
            self.update_gif_display_and_data()

    def open_axis_window(self, axis_var, axis_name):
        def detect_axis():
            nonlocal axis_detected, previous_values
            pygame.event.pump()
            significant_change_detected = False

            for i in range(self.joystick.get_numaxes()):
                value = self.joystick.get_axis(i)
                if abs(value - previous_values[i]) > 0.2:  # Compare the current value with the previous one
                    axis_detected = i
                    axis_label.config(text=f"Detected Axis: {axis_detected}")
                    significant_change_detected = True
                    previous_values[i] = value

            if not significant_change_detected:
                assign_window.after(50, detect_axis)  # We continue to check

        def apply_axis():
            axis_var.set(axis_detected)
            self.save_config()
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

        detect_axis()  # We start checking immediately after opening the window

    def open_button_window(self, button_var, description):
        def on_detect_button():
            pygame.event.pump()
            detected_button = -1
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    detected_button = i
                    break
            button_var.set(detected_button)
            self.save_config()
            detected_label.config(text=f"Detected Button: {detected_button}")
        def on_apply():
            button_var.set(button_var.get())
            self.save_config()
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
        
    def update_display_results(self):
        start_index = self.current_result_index
        end_index = min(start_index + self.results_per_page, len(self.results_list))
        display_results = self.results_list[start_index:end_index]
        self.result_text = "\n\n".join(display_results)
        
    # Limit search to English language pages
    def perform_search(self, query):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        search_results = []

        # We go through several pages of results
        for start in range(0, 50, 10):
            response = requests.get(f"https://www.google.com/search?q={query}&start={start}&lr=lang_en", headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            for g in soup.find_all('div', class_='tF2Cxc'):
                title_elem = g.find('h3')
                link_elem = g.find('a')
                if title_elem and link_elem:
                    title = title_elem.text
                    link = link_elem['href']
                    search_results.append((title, link))

        self.result_text = search_results[:50]  # Saving the first 50 results
        self.current_page = 0  # Reset to first page
        self.search_complete = True  # Set the search completion flag

    def get_current_results(self):
        start = self.current_page * 3
        end = start + 3
        return self.result_text[start:end]
    
    def load_page_content(self, url):
        try:
            response = requests.get(url, timeout=10)  # Set timeout to 10 seconds
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            page_content = "\n\n".join([p.text for p in paragraphs])

            # Split text into 500-character chunks, avoiding word cutting
            self.page_content = []
            current_chunk = ""
            for paragraph in paragraphs:
                wrapped_lines = textwrap.wrap(paragraph.text, width=80, break_long_words=False)
                for line in wrapped_lines:
                    if len(current_chunk) + len(line) + 1 > 500:  # +1 for adding a space or newline
                        self.page_content.append(current_chunk.strip())
                        current_chunk = line
                    else:
                        if current_chunk:
                            current_chunk += " " + line
                        else:
                            current_chunk = line
            if current_chunk:  # Add last chunk
                self.page_content.append(current_chunk.strip())

            self.is_page_loaded = True
            self.is_loading = False  # Resetting the loading flag after completion
        except Exception as e:
            self.page_content = ["Failed to load page content"]
            logging.error(f"Failed to load page content: {e}")
            self.is_page_loaded = True
            self.is_loading = False  # Resetting the loading flag after completion

    def get_page_content(self, index):
        if index < 0 or index >= len(self.page_content):
            return "No more content", 200
        return self.page_content[index], 200
    
    # Улучшение разбивки текста на строки
    def split_text_into_lines(self, text, max_line_length):
        wrapped_lines = []
        for line in text.split('\n'):
            wrapped_lines.extend(textwrap.wrap(line, width=max_line_length, break_long_words=False))
        return wrapped_lines

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
            self.current_image = self.process_static_image(image, self.selected_size, self.fill_image)
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

        @self.app.route('/gif_frame/<int:frame_index>', methods=['GET'])
        def get_gif_frame(frame_index):
            start_time = time.time()  # Start of countdown
            if frame_index < 0 or frame_index >= len(self.gif_frames_data):
                return "Frame index out of range", 400
            end_time = time.time()  # End of countdown
            print(f"Time taken for frame {frame_index}: {end_time - start_time} seconds")  # Print countdown
            return self.gif_frames_data[frame_index], 200

        @self.app.route('/gif_frame_count', methods=['GET'])
        def get_gif_frame_count():
            return str(len(self.gif_frames_data)), 200
        
        @self.app.route('/search', methods=['GET'])
        def search():
            query = request.args.get('query')
            if query:
                decoded_query = "".join([chr(int(x)) for x in query.split()])
                self.search_complete = False  # Set the search start flag
                threading.Thread(target=self.perform_search, args=(decoded_query,)).start()
                print(f"Received query: {decoded_query}")
                return jsonify({'status': 'searching'})
            return 'Invalid query', 400

        @self.app.route('/search_status', methods=['GET'])
        def search_status():
            if self.search_complete:
                return jsonify({'status': 'complete'}), 200
            return jsonify({'status': 'searching'}), 200

        @self.app.route('/result', methods=['GET'])
        def result():
            if not self.search_complete:
                return "Search in progress", 202
            results = self.get_current_results()
            formatted_results = []
            for title, link in results:
                formatted_results.append(f"{title}\n{link}")
            return "\n\n".join(formatted_results).encode('utf-8')

        @self.app.route('/scroll', methods=['GET'])
        def scroll():
            direction = request.args.get('direction')
            results_count = len(self.result_text)
            if direction == 'up' and self.current_page > 0:
                self.current_page -= 1
            elif direction == 'down' and (self.current_page + 1) * 3 < results_count:
                self.current_page += 1
            results = self.get_current_results()
            formatted_results = []
            for title, link in results:
                formatted_results.append(f"{title}\n{link}")
            return "\n\n".join(formatted_results).encode('utf-8')
        
        @self.app.route('/page_content', methods=['GET'])
        def page_content():
            url = request.args.get('url')
            if url:
                self.is_page_loaded = False
                self.is_loading = True  # Setting the loading flag
                threading.Thread(target=self.load_page_content, args=(url,)).start()
                return jsonify({'status': 'loading'}), 200
            return 'Invalid URL', 400

        @self.app.route('/page_status', methods=['GET'])
        def page_status():
            if self.is_page_loaded:
                return jsonify({'status': 'loaded'}), 200
            return jsonify({'status': 'loading'}), 200

        @self.app.route('/page_part', methods=['GET'])
        def page_part():
            index = int(request.args.get('index', 0))
            max_line_length = 40  # Set max line length based on screen width
            if index < 0 or index >= len(self.page_content):
                return "No more content", 200
            lines = self.split_text_into_lines(self.page_content[index], max_line_length)
            return "\n".join(lines), 200
        
        @self.app.route('/arduino_data', methods=['GET'])
        def arduino_data():
            input_data = request.args
            for i in range(1, 5):
                self.boolean_inputs[i-1] = input_data.get(f'bool_in{i}', '0') == '1'
            for i in range(5, 9):
                self.digital_inputs[i-5] = float(input_data.get(f'digit_in{i}', '0.0'))
            return jsonify({
                'bool_out1': 1 if self.boolean_outputs[0] else 0,
                'bool_out2': 1 if self.boolean_outputs[1] else 0,
                'bool_out3': 1 if self.boolean_outputs[2] else 0,
                'bool_out4': 1 if self.boolean_outputs[3] else 0,
                'digit_out5': self.digital_outputs[0],
                'digit_out6': self.digital_outputs[1],
                'digit_out7': self.digital_outputs[2],
                'digit_out8': self.digital_outputs[3]
            })

        thread = threading.Thread(target=self.start_flask)
        thread.daemon = True
        thread.start()

    def start_flask(self):
        self.app.run(debug=True, use_reloader=False)
        
class ArduinoHandler:
    def __init__(self, port="COM3", baud_rate=9600):
        self.ser = None
        self.task_queue = queue.Queue()
        self.thread = threading.Thread(target=self.process_tasks)
        self.thread.daemon = True
        self.thread.start()
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=0.1)
            time.sleep(2)
            print(f"Connected to Arduino on port {port}")
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")

    def read_from_arduino(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    return line
            except Exception as e:
                print(f"Error reading line: {e}")
        return None

    def send_to_arduino(self, command):
        self.task_queue.put(command)

    def process_tasks(self):
        while True:
            command = self.task_queue.get()
            if command is None:
                break
            self._send_command(command)
            self.task_queue.task_done()

    def _send_command(self, command):
        try:
            if self.ser:
                self.ser.write(f"{command}\n".encode('utf-8'))
                time.sleep(0.1)  # Small delay for stable command sending
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")

    def close(self):
        self.task_queue.put(None)
        self.thread.join()
        if self.ser:
            self.ser.close()

if __name__ == "__main__":
    App()
