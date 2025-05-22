import os
os.environ["GDK_BACKEND"] = "wayland,x11"  
os.environ["XDG_SESSION_TYPE"] = "wayland"
import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import messagebox
from ttkthemes import ThemedTk
import re
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AppIndicator3
import threading
import os



class TrayManager:
    def __init__(self, root):
        self.root = root
    
        # Custom icon path (update with your actual path)
        icon_path = "/home/yusifvatan/Projects/GUI-for-Linuwu-Sense/logo_predator.png"
    
        self.indicator = AppIndicator3.Indicator.new(
        "keyboard-controller",
        icon_path,  # Use file path instead of stock icon name
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS
    )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.build_menu()
        # Start GTK thread
        self.gtk_thread = threading.Thread(target=Gtk.main, daemon=True)
        self.gtk_thread.start()
    def get_sensor_data(self):
        try:
            output = subprocess.check_output(["sensors"], text=True)
            
            # Find acer-isa section
            acer_section = re.search(
                r'acer-isa-0000(.*?)\n\n',  # Capture until next empty line
                output, 
                re.DOTALL
            )
            
            if not acer_section:
                return "N/A", "N/A", "N/A", "N/A"

            section = acer_section.group(1)
            
            # Parse CPU Fan (fan1)
            cpu_fan = re.search(r'fan1:\s+(\d+) RPM', section)
            cpu_fan = f"{cpu_fan.group(1)} RPM" if cpu_fan else "N/A"
            
            # Parse GPU Fan (fan2)
            gpu_fan = re.search(r'fan2:\s+(\d+) RPM', section)
            gpu_fan = f"{gpu_fan.group(1)} RPM" if gpu_fan else "N/A"
            
            # Parse CPU Temp (temp1)
            cpu_temp = re.search(r'temp1:\s+([+-]?\d+\.\d+)°C', section)
            cpu_temp = f"{cpu_temp.group(1)}°C" if cpu_temp else "N/A"
            
            # Parse GPU Temp (temp3)
            gpu_temp = re.search(r'temp3:\s+([+-]?\d+\.\d+)°C', section)
            gpu_temp = f"{gpu_temp.group(1)}°C" if gpu_temp else "N/A"
            
            return cpu_fan, gpu_fan, cpu_temp, gpu_temp
            
        except Exception as e:
            print(f"Sensor read error: {e}")
            return "ERR", "ERR", "ERR", "ERR"

    def update_sensors(self):
        cpu_fan, gpu_fan, cpu_temp, gpu_temp = self.get_sensor_data()
        
        # Update menu labels with actual sensor data
        GLib.idle_add(self.status_fans.set_label, 
                     f"Fans: CPU {cpu_fan} | GPU {gpu_fan}")
        GLib.idle_add(self.status_temps.set_label,
                     f"Temps: CPU {cpu_temp} | GPU {gpu_temp}")
        
        # Reschedule update every 3 seconds
        return True  # Keep the timeout active

    def build_menu(self):
        menu = Gtk.Menu()


        
        # Open Application
        open_item = Gtk.MenuItem(label="Show or Hide")
        open_item.connect("activate", self.toggle_window)
        menu.append(open_item)

        # Lighting Modes (Updated)
        lighting_menu = Gtk.Menu()
        lighting_item = Gtk.MenuItem(label="Lighting Modes ▶")
        
        # Add all 8 modes
        modes = [
            (0, "Static Mode", True),
            (1, "Breathing Mode", True),
            (2, "Neon Mode", False),  # No color needed
            (3, "Wave Mode", False),   # No color needed
            (4, "Shifting Mode", True),
            (5, "Zoom Mode", True),
            (6, "Meteor Mode", True),
            (7, "Twinkling Mode", True)
        ]

        for mode_num, mode_name, needs_color in modes:
            item = Gtk.MenuItem(label=mode_name)
            if needs_color:
                # Modes that require color selection
                item.connect("activate", 
                            lambda w, m=mode_num: self.create_color_chooser(m))
            else:
                # Modes with default white color (255,255,255)
                item.connect("activate", 
                            lambda w, m=mode_num: apply_four_zone_mode(
                                m, 1, 100, 1, 255, 255, 255
                            ))
            lighting_menu.append(item)    

        lighting_item.set_submenu(lighting_menu)
        menu.append(lighting_item)
        

   
        
        
        
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Settings
        settings_menu = Gtk.Menu()
        settings_item = Gtk.MenuItem(label="Settings ▶")
        
        # Backlight Timeout
        self.timeout_item = Gtk.CheckMenuItem(label="Backlight Timeout")
        self.timeout_item.set_active(True)
        self.timeout_item.connect("toggled", self.on_timeout_toggled)
        settings_menu.append(self.timeout_item)
        
        # Battery Limiter
        self.limiter_item = Gtk.CheckMenuItem(label="Battery Limiter")
        self.limiter_item.connect("toggled", self.on_limiter_toggled)
        settings_menu.append(self.limiter_item)
        
        settings_item.set_submenu(settings_menu)
        menu.append(settings_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Status
        self.status_fans = Gtk.MenuItem(label="Loading sensor data...")
        self.status_temps = Gtk.MenuItem(label="Loading sensor data...")
        for item in [self.status_fans, self.status_temps]:
            item.set_sensitive(False)
            menu.append(item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # System
        system_menu = Gtk.Menu()
        system_item = Gtk.MenuItem(label="System ▶")
        
        exit_item = Gtk.MenuItem(label="Exit")
        exit_item.connect("activate", self.on_exit)
        system_menu.append(exit_item)
        
        system_item.set_submenu(system_menu)
        menu.append(system_item)

        menu.show_all()
        self.indicator.set_menu(menu)
        
        # Start sensor updates
        GLib.timeout_add_seconds(3, self.update_sensors)
    def toggle_window(self, widget=None):
        """Toggle main window visibility"""
        if self.root.winfo_viewable():
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.root.lift()

    def on_exit(self, widget=None):
        """Handle exit menu item"""
        Gtk.main_quit()
        self.root.destroy()

    def on_timeout_toggled(self, widget):
        """Handle backlight timeout toggle"""
        state = 1 if widget.get_active() else 0
        set_backlight_timeout(state)

    def on_limiter_toggled(self, widget):
        """Handle battery limiter toggle"""
        state = 1 if widget.get_active() else 0
        set_battery_limiter(state)

    def create_color_chooser(self, mode):
        dialog = Gtk.ColorChooserDialog(title="Choose Color")
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            rgb = (
                int(color.red * 255),
                int(color.green * 255),
                int(color.blue * 255)
            )
            # Use default values from GUI (speed=1, brightness=100, direction=1)
            apply_four_zone_mode(mode, 1, 100, 1, *rgb)
            
        dialog.destroy()
    


 


# Function to convert RGB to hex
def rgb_to_hex(rgb):
    r, g, b = map(int, rgb.split(","))
    return f"{r:02x}{g:02x}{b:02x}"

def apply_per_zone_mode(zone1, zone2, zone3, zone4):
    path = '/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/per_zone_mode'
    data = f"{zone1},{zone2},{zone3},{zone4}"
    try:
        with open(path, 'w') as f:
            f.write(data)
    except PermissionError:
        subprocess.run(['sudo', 'tee', path], input=data.encode(), check=True)
# Function to apply four zone mode

def apply_four_zone_mode(mode, speed, brightness, direction, red, green, blue):
    path = '/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/four_zone_mode'
    data = f"{mode},{speed},{brightness},{direction},{red},{green},{blue}"
    try:
        with open(path, 'w') as f:
            f.write(data)
    except PermissionError:
        subprocess.run(['sudo', 'tee', path], input=data.encode(), check=True)


def set_backlight_timeout(state):
    path = '/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/backlight_timeout'
    try:
        with open(path, 'w') as f:
            f.write(str(state))
    except PermissionError:
        subprocess.run(['sudo', 'tee', path], input=str(state).encode(), check=True)

# Function to check backlight timeout
def check_backlight_timeout():
    try:
        with os.popen("cat /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/backlight_timeout") as output:
            state = output.read().strip()
            return int(state)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def apply_fan_speed(cpu_speed, gpu_speed):
    # Convert "Automatic" to 0
    cpu = 0 if isinstance(cpu_speed, str) and cpu_speed.lower() == "automatic" else cpu_speed
    gpu = 0 if isinstance(gpu_speed, str) and gpu_speed.lower() == "automatic" else gpu_speed
    
    path = '/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/fan_speed'
    try:
        with open(path, 'w') as f:
            f.write(f"{cpu},{gpu}")
    except (PermissionError, IOError) as e:
        print(f"Error writing fan speed: {e}")
        # Fallback to sudo
        subprocess.run(['sudo', 'tee', path], 
                      input=f"{cpu},{gpu}".encode(), 
                      check=True)

# Color picker function
def color_picker(label, preview_label):
    color_code = colorchooser.askcolor(title="Choose color")
    if color_code[0]:
        r, g, b = map(int, color_code[0])
        label.config(text=f"{r},{g},{b}")
        preview_label.config(background=f"#{r:02x}{g:02x}{b:02x}")

# Battery Calibration function
def start_stop_battery_calibration(state):
    try:
        command = f"echo {state} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_calibration"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", f"Battery calibration {'started' if state == 1 else 'stopped'} successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Battery Limiter function
def set_battery_limiter(state):
    try:
        with open('/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_limiter', 'w') as f:
            f.write(str(state))
    except IOError as e:
        print(f"Error writing to sysfs: {e}")
        # Fallback to sudo if udev rules didn't work
        subprocess.run(['sudo', 'tee', '/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_limiter'], 
                      input=str(state).encode(), check=True)

# Function to check the status of Battery Calibration
def check_battery_calibration_status():
    try:
        with os.popen("cat /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_calibration") as output:
            status = output.read().strip()
            messagebox.showinfo("Battery Calibration Status", f"Current status: {'Started' if status == '1' else 'Stopped'}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to check the status of Battery Limiter
def check_battery_limiter_status():
    try:
        with os.popen("cat /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_limiter") as output:
            status = output.read().strip()
            messagebox.showinfo("Battery Limiter Status", f"Current status: {'Enabled' if status == '1' else 'Disabled'}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to create the GUI
def create_gui():
    root = ThemedTk(theme="arc")  # Using 'arc' as a modern theme resembling Azure's style
    root.title("Keyboard Backlight & Fan Speed Controller")
    root.geometry("800x1200")
    
    # Start minimized (withdrawn)
    root.withdraw()  # <-- This hides the main window
    
    # Your existing GUI setup code...
    notebook = ttk.Notebook(root)
    # ... rest of your code


    
    


    # Theme selection
    theme_frame = ttk.Frame(root)
    theme_frame.pack(pady=10)

    ttk.Label(theme_frame, text="Select Theme:").pack(side="left", padx=5)
    theme_var = tk.StringVar(value="arc")  # Default theme
    theme_dropdown = ttk.Combobox(
        theme_frame,
        textvariable=theme_var,
        values=["arc", "default", "black", "clearlooks", "classic", "dark", "kroc", "radiance", "scidgrey"],
        state="readonly"
    )
    theme_dropdown.pack(side="left", padx=5)

    def change_theme():
        selected_theme = theme_var.get()
        root.set_theme(selected_theme)

    theme_dropdown.bind("<<ComboboxSelected>>", lambda event: change_theme())

    # Create the main notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab 1: Backlight Control and Timeout
    backlight_frame = ttk.Frame(notebook)
    notebook.add(backlight_frame, text="Backlight Control & Timeout")

    # Keyboard layout resembling the zones
    keyboard_frame = ttk.LabelFrame(backlight_frame, text="Keyboard Lighting Zones")
    keyboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

    zone_frame = tk.Frame(keyboard_frame)
    zone_frame.pack(pady=10)

    zone_labels = []
    zone_previews = []

    for i, zone_text in enumerate(["Section 1", "Section 2", "Section 3", "Section 4"], start=1):
        frame = tk.Frame(zone_frame)
        frame.pack(side="left", padx=10)

        preview = tk.Label(
            frame,
            text=zone_text,
            width=10,
            height=5,
            relief="ridge",
            bg="black",
            fg="white"
        )
        preview.pack()

        label = ttk.Label(frame, text="0,0,0", relief="solid", width=12)
        label.pack(pady=5)

        ttk.Button(
            frame,
            text="Pick Color",
            command=lambda lbl=label, pv=preview: color_picker(lbl, pv)
        ).pack()

        zone_labels.append(label)
        zone_previews.append(preview)

    ttk.Button(
        keyboard_frame,
        text="Apply Colors",
        command=lambda: apply_per_zone_mode(
            zone_labels[0].cget("text"),
            zone_labels[1].cget("text"),
            zone_labels[2].cget("text"),
            zone_labels[3].cget("text"),
        ),
    ).pack(pady=10)

    # Four-Zone Mode
    four_zone_frame = ttk.LabelFrame(backlight_frame, text="Four-Zone Mode")
    four_zone_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Label(four_zone_frame, text="Mode:").pack(anchor="w")
    mode_var = tk.StringVar()
    mode_dropdown = ttk.Combobox(
        four_zone_frame,
        textvariable=mode_var,
        values=[
            "0: Static Mode",
            "1: Breathing Mode",
            "2: Neon Mode",
            "3: Wave Mode",
            "4: Shifting Mode",
            "5: Zoom Mode",
            "6: Meteor Mode",
            "7: Twinkling Mode"
        ],
        state="readonly"
    )
    mode_dropdown.pack(fill="x", pady=5)

    ttk.Label(four_zone_frame, text="Speed:").pack(anchor="w")
    speed_var = tk.IntVar(value=1)  # Default speed
    speed_dropdown = ttk.Combobox(four_zone_frame, textvariable=speed_var, values=list(range(10)), state="readonly")
    speed_dropdown.pack(fill="x", pady=5)

    ttk.Label(four_zone_frame, text="Brightness:").pack(anchor="w")
    brightness_var = tk.IntVar(value=100)  # Default brightness
    ttk.Scale(four_zone_frame, variable=brightness_var, from_=0, to=100, orient="horizontal").pack(fill="x", pady=5)

    ttk.Label(four_zone_frame, text="Direction:").pack(anchor="w")
    direction_var = tk.IntVar(value=1)  # Default direction
    direction_dropdown = ttk.Combobox(four_zone_frame, textvariable=direction_var, values=[1, 2], state="readonly")
    direction_dropdown.pack(fill="x", pady=5)

    rgb_frame = ttk.Frame(four_zone_frame)
    rgb_frame.pack(fill="x", pady=5)

    ttk.Label(rgb_frame, text="RGB:").pack(side="left", padx=5)
    color_label = ttk.Label(rgb_frame, text="0,0,0", relief="solid", width=12)
    color_label.pack(side="left", padx=5)
    ttk.Button(rgb_frame, text="Pick", command=lambda lbl=color_label: color_picker(lbl, lbl)).pack(side="left", padx=5)

    ttk.Button(
        four_zone_frame,
        text="Apply",
        command=lambda: apply_four_zone_mode(
            int(mode_var.get().split(":")[0]),
            speed_var.get(),
            brightness_var.get(),
            direction_var.get(),
            *map(int, color_label.cget("text").split(","))
        ),
    ).pack(pady=10)

    # Backlight Timeout
    timeout_frame = ttk.LabelFrame(backlight_frame, text="Backlight Timeout")
    timeout_frame.pack(fill="both", expand=True, padx=10, pady=10)

    current_state = check_backlight_timeout()
    state_var = tk.IntVar(value=current_state if current_state is not None else 1)

    ttk.Radiobutton(timeout_frame, text="Enable Timeout", variable=state_var, value=1).pack(anchor="w")
    ttk.Radiobutton(timeout_frame, text="Disable Timeout", variable=state_var, value=0).pack(anchor="w")

    ttk.Button(
        timeout_frame,
        text="Apply",
        command=lambda: set_backlight_timeout(state_var.get())
    ).pack(pady=5)

    ttk.Button(
        timeout_frame,
        text="Check Current Status",
        command=lambda: messagebox.showinfo("Backlight Timeout Status", f"Current status: {'Enabled' if check_backlight_timeout() == 1 else 'Disabled'}")
    ).pack(pady=5)

    # Tab 2: Fan Speed Control
    fan_speed_frame = ttk.Frame(notebook)
    notebook.add(fan_speed_frame, text="Fan Speed Control")

    ttk.Label(fan_speed_frame, text="CPU Fan Speed:").pack(anchor="w")
    cpu_speed_var = tk.StringVar(value="Automatic")  # Default set to "Automatic"
    cpu_speed_dropdown = ttk.Combobox(fan_speed_frame, textvariable=cpu_speed_var, values=["Automatic"] + list(range(5, 101, 5)), state="readonly")
    cpu_speed_dropdown.pack(fill="x", pady=5)

    ttk.Label(fan_speed_frame, text="GPU Fan Speed:").pack(anchor="w")
    gpu_speed_var = tk.StringVar(value="Automatic")  # Default set to "Automatic"
    gpu_speed_dropdown = ttk.Combobox(fan_speed_frame, textvariable=gpu_speed_var, values=["Automatic"] + list(range(5, 101, 5)), state="readonly")
    gpu_speed_dropdown.pack(fill="x", pady=5)

    ttk.Button(
        fan_speed_frame,
        text="Apply Fan Speed",
        command=lambda: apply_fan_speed(cpu_speed_var.get(), gpu_speed_var.get())
    ).pack(pady=10)

    # Tab 3: Battery Settings (New Tab for Calibration and Limiter)
    battery_frame = ttk.Frame(notebook)
    notebook.add(battery_frame, text="Battery Settings")

    # Battery Calibration
    battery_calibration_frame = ttk.LabelFrame(battery_frame, text="Battery Calibration")
    battery_calibration_frame.pack(fill="both", expand=True, padx=10, pady=10)

    calibration_state_var = tk.IntVar(value=0)  # Default set to 0 (off)
    
    ttk.Radiobutton(
        battery_calibration_frame,
        text="Start Calibration",
        variable=calibration_state_var,
        value=1
    ).pack(anchor="w")
    ttk.Radiobutton(
        battery_calibration_frame,
        text="Stop Calibration",
        variable=calibration_state_var,
        value=0
    ).pack(anchor="w")

    ttk.Button(
        battery_calibration_frame,
        text="Apply Battery Calibration",
        command=lambda: start_stop_battery_calibration(calibration_state_var.get())
    ).pack(pady=5)

    ttk.Button(
        battery_calibration_frame,
        text="Check Calibration Status",
        command=check_battery_calibration_status
    ).pack(pady=5)

    # Battery Limiter
    battery_limiter_frame = ttk.LabelFrame(battery_frame, text="Battery Limiter")
    battery_limiter_frame.pack(fill="both", expand=True, padx=10, pady=10)

    limiter_state_var = tk.IntVar(value=0)  # Default set to 0 (disabled)
    
    ttk.Radiobutton(
        battery_limiter_frame,
        text="Enable Battery Limiter",
        variable=limiter_state_var,
        value=1
    ).pack(anchor="w")
    ttk.Radiobutton(
        battery_limiter_frame,
        text="Disable Battery Limiter",
        variable=limiter_state_var,
        value=0
    ).pack(anchor="w")

    ttk.Button(
        battery_limiter_frame,
        text="Apply Battery Limiter",
        command=lambda: set_battery_limiter(limiter_state_var.get())
    ).pack(pady=5)

    ttk.Button(
        battery_limiter_frame,
        text="Check Limiter Status",
        command=check_battery_limiter_status
    ).pack(pady=5)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    tray = TrayManager(root)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

