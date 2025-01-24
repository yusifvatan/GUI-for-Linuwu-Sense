import os
import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import messagebox
from ttkthemes import ThemedTk

# Function to convert RGB to hex
def rgb_to_hex(rgb):
    r, g, b = map(int, rgb.split(","))
    return f"{r:02x}{g:02x}{b:02x}"

# Function to apply per zone mode
def apply_per_zone_mode(zone1, zone2, zone3, zone4):
    try:
        zone1_hex = rgb_to_hex(zone1)
        zone2_hex = rgb_to_hex(zone2)
        zone3_hex = rgb_to_hex(zone3)
        zone4_hex = rgb_to_hex(zone4)

        command = f"echo {zone1_hex},{zone2_hex},{zone3_hex},{zone4_hex} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/per_zone_mode"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", "Per-Zone Mode applied successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to apply four zone mode
def apply_four_zone_mode(mode, speed, brightness, direction, red, green, blue):
    try:
        command = f"echo {mode},{speed},{brightness},{direction},{red},{green},{blue} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb/four_zone_mode"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", "Four-Zone Mode applied successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to set backlight timeout
def set_backlight_timeout(state):
    try:
        command = f"echo {state} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/backlight_timeout"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", f"Backlight timeout {'enabled' if state == 1 else 'disabled'} successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to check backlight timeout
def check_backlight_timeout():
    try:
        with os.popen("cat /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/backlight_timeout") as output:
            state = output.read().strip()
            return int(state)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# Function to apply fan speed
def apply_fan_speed(cpu_speed, gpu_speed):
    try:
        if cpu_speed == "Automatic":
            cpu_speed = 0
        if gpu_speed == "Automatic":
            gpu_speed = 0
        command = f"echo {cpu_speed},{gpu_speed} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/fan_speed"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", "Fan speed applied successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

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
        command = f"echo {state} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense/battery_limiter"
        print(f"Running command: {command}")
        os.system(command)
        messagebox.showinfo("Success", f"Battery limiter {'enabled' if state == 1 else 'disabled'} successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

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

    root.mainloop()

if __name__ == "__main__":
    create_gui()
