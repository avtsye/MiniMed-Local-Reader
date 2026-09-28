"""Local desktop viewer for stored simulated data.

Display-only UI. It does not connect to a pump and does not provide therapy
controls or treatment recommendations.
"""
import tkinter as tk
from tkinter import ttk
from storage.db import open_db

class LocalViewer:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        root.title("MiniMed Local Reader — Simulation Viewer")
        root.geometry("900x600")
        root.minsize(760, 480)

        header = ttk.Frame(root, padding=14)
        header.pack(fill="x")
        ttk.Label(header, text="MiniMed Local Reader", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="LOCAL SIMULATION DATA — display only; not for treatment decisions",
        ).pack(anchor="w", pady=(4, 0))

        cards = ttk.Frame(root, padding=(14, 0, 14, 12))
        cards.pack(fill="x")
        self.sensor_var = tk.StringVar(value="—")
        self.battery_var = tk.StringVar(value="—")
        self.reservoir_var = tk.StringVar(value="—")
        for column, (title, variable) in enumerate((
            ("Latest sensor", self.sensor_var),
            ("Battery", self.battery_var),
            ("Reservoir", self.reservoir_var),
        )):
            box = ttk.LabelFrame(cards, text=title, padding=12)
            box.grid(row=0, column=column, padx=5, sticky="nsew")
            cards.columnconfigure(column, weight=1)
            ttk.Label(box, textvariable=variable, font=("Segoe UI", 16, "bold")).pack()

        toolbar = ttk.Frame(root, padding=(14, 0, 14, 8))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left")
        self.status_var = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side="right")

        frame = ttk.Frame(root, padding=(14, 0, 14, 14))
        frame.pack(fill="both", expand=True)
        columns = ("time", "value", "unit", "source")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for key, title, width in (
            ("time", "Time (UTC)", 280),
            ("value", "Sensor value", 140),
            ("unit", "Unit", 100),
            ("source", "Source", 180),
        ):
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="center")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh()

    def refresh(self):
        con = open_db(self.db_path)
        try:
            sensor = con.execute(
                "SELECT event_time,value,unit,source FROM sensor_readings ORDER BY id DESC LIMIT 1"
            ).fetchone()
            status = con.execute(
                "SELECT battery_percent,reservoir_units FROM device_status ORDER BY id DESC LIMIT 1"
            ).fetchone()
            history = con.execute(
                "SELECT event_time,value,unit,source FROM sensor_readings ORDER BY id DESC LIMIT 100"
            ).fetchall()
        finally:
            con.close()

        self.sensor_var.set(f"{sensor[1]:g} {sensor[2]}" if sensor else "No data")
        self.battery_var.set(f"{status[0]}%" if status else "No data")
        self.reservoir_var.set(f"{status[1]:g} U" if status else "No data")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in history:
            self.tree.insert("", "end", values=row)
        self.status_var.set(f"{len(history)} stored simulated reading(s)")

def run(db_path="minimed_local.sqlite"):
    root = tk.Tk()
    LocalViewer(root, db_path)
    root.mainloop()
