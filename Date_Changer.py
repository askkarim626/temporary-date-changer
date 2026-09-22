import ctypes
from datetime import datetime as dt, timedelta
import os
import platform
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox


def is_admin():
  """Check whether the script is running with administrator privileges."""
  try:
    if platform.system() == "Windows":
      return ctypes.windll.shell32.IsUserAnAdmin()
    else:
      return os.getuid() == 0
  except:
    return False


def set_system_datetime(date_str, time_str):
  """Change the operating system date and time."""
  system = platform.system()
  try:
    if system == "Windows":
      date_object = dt.strptime(date_str, "%Y-%m-%d")
      windows_date = date_object.strftime("%d/%m/%Y")
      subprocess.run(f"date {windows_date}", shell=True, check=True)
      subprocess.run(f"time {time_str}", shell=True, check=True)
    elif system == "Linux" or system == "Darwin":
      date_object = dt.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
      unix_date = date_object.strftime("%m%d%H%M%Y.%S")
      subprocess.run(f"date {unix_date}", shell=True, check=True)
    return True
  except Exception as e:
    messagebox.showerror("Error", f"Could not change the date and time:\n{e}")
    return False


class DateChangerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Temporary Date Changer")
    self.root.geometry("360x290")
    self.root.resizable(False, False)

    self.original_real_date = ""
    self.original_real_time = ""
    self.original_datetime = None
    self.monotonic_start = None
    self.active = False

    current_datetime = dt.now()

    title_label = tk.Label(
        root, text="System Date and Time Modifier", font=("Arial", 11, "bold")
    )
    title_label.pack(pady=10)

    date_frame = tk.Frame(root)
    date_frame.pack(pady=5, fill="x", padx=20)
    tk.Label(
        date_frame, text="Date (YYYY-MM-DD):", width=18, anchor="w"
    ).pack(side="left")
    self.date_entry = tk.Entry(date_frame, width=15)
    self.date_entry.pack(side="right")
    self.date_entry.insert(0, current_datetime.strftime("%Y-%m-%d"))

    time_frame = tk.Frame(root)
    time_frame.pack(pady=5, fill="x", padx=20)
    tk.Label(time_frame, text="Time (HH:MM:SS):", width=18, anchor="w").pack(
        side="left"
    )
    self.time_entry = tk.Entry(time_frame, width=15)
    self.time_entry.pack(side="right")
    self.time_entry.insert(0, current_datetime.strftime("%H:%M:%S"))

    self.status_label = tk.Label(
        root,
        text="Status: Inactive (Real Time)",
        fg="red",
        font=("Arial", 9, "italic"),
    )
    self.status_label.pack(pady=10)


    self.action_button = tk.Button(
        root,
        text="Apply and Keep Date",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.toggle_state,
    )
    self.action_button.pack(pady=10, fill="x", padx=20)

    footer_label = tk.Label(
        root,
        text=(
            "Close the window to restore\nthe original date and time"
            " automatically."
        ),
        fg="gray",
        font=("Arial", 8),
    )
    footer_label.pack(pady=5)

    self.root.protocol("WM_DELETE_WINDOW", self.handle_close)

  def toggle_state(self):
    if not self.active:
      desired_date = self.date_entry.get().strip()
      desired_time = self.time_entry.get().strip()

      try:
        dt.strptime(f"{desired_date} {desired_time}", "%Y-%m-%d %H:%M:%S")
      except ValueError:
        messagebox.showerror(
            "Incorrect Format",
            "Use YYYY-MM-DD for the date and HH:MM:SS for the time.",
        )
        return

      original_datetime = dt.now()
      self.original_real_date = original_datetime.strftime("%Y-%m-%d")
      self.original_real_time = original_datetime.strftime("%H:%M:%S")
      self.original_datetime = original_datetime
      self.monotonic_start = time.monotonic()

      if set_system_datetime(desired_date, desired_time):
        self.active = True
        self.status_label.config(
            text="Status: ACTIVE (Date Modified)", fg="green"
        )
        self.action_button.config(
            text="Restore Original Time", bg="#f44336", fg="white"
        )
        self.date_entry.config(state="disabled")
        self.time_entry.config(state="disabled")
    else:
      self.restore_and_reset()

  def restore_and_reset(self):
    if self.active:
      elapsed_seconds = time.monotonic() - self.monotonic_start
      restored_datetime = self.original_datetime + timedelta(
        seconds=elapsed_seconds
      )
      restored_date = restored_datetime.strftime("%Y-%m-%d")
      restored_time = restored_datetime.strftime("%H:%M:%S")
      print(
        f"Restoring current time: {restored_date}"
        f" {restored_time}"
      )
      set_system_datetime(
        restored_date, restored_time
      )
      self.active = False

    self.status_label.config(text="Status: Inactive (Real Time)", fg="red")
    self.action_button.config(
        text="Apply and Keep Date", bg="#4CAF50", fg="white"
    )
    self.date_entry.config(state="normal")
    self.time_entry.config(state="normal")

  def handle_close(self):
    if self.active:
      if messagebox.askyesno(
          "Exit",
          "The modified date is still active. Restore the original time and exit?",
      ):
        self.restore_and_reset()
        self.root.destroy()
    else:
      self.root.destroy()


if __name__ == "__main__":
  if not is_admin():
    root_temp = tk.Tk()
    root_temp.withdraw()
    messagebox.showerror(
        "Administrator Privileges Required",
        "Please run this script or the terminal as Administrator because"
        " changing the system date and time requires elevated privileges.",
    )
    sys.exit()

  root = tk.Tk()
  app = DateChangerApp(root)
  root.mainloop()