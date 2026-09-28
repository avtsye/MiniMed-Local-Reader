"""Local display-only viewer for stored simulated data."""
import csv
import json
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import filedialog, messagebox, ttk
from storage.db import open_db, latest_sensor, latest_status, sensor_history

class LocalViewer:
    def __init__(self, root, db_path):
        self.root, self.db_path = root, db_path
        self.auto_refresh = tk.BooleanVar(value=True)
        self.range_var = tk.StringVar(value="All")
        self.status_var = tk.StringVar()
        self.sensor_var = tk.StringVar(value="—")
        self.battery_var = tk.StringVar(value="—")
        self.reservoir_var = tk.StringVar(value="—")
        self.history = []

        root.title("MiniMed Local Reader — Simulation Viewer")
        root.geometry("1050x760")
        root.minsize(820, 600)

        header=ttk.Frame(root,padding=14); header.pack(fill="x")
        ttk.Label(header,text="MiniMed Local Reader",font=("Segoe UI",20,"bold")).pack(anchor="w")
        ttk.Label(header,text="SIMULATION DATA ONLY — display-only; not for treatment decisions").pack(anchor="w")

        cards=ttk.Frame(root,padding=(14,0,14,10)); cards.pack(fill="x")
        for i,(title,var) in enumerate((("Latest sensor",self.sensor_var),("Battery",self.battery_var),("Reservoir",self.reservoir_var))):
            box=ttk.LabelFrame(cards,text=title,padding=10); box.grid(row=0,column=i,padx=4,sticky="nsew"); cards.columnconfigure(i,weight=1)
            ttk.Label(box,textvariable=var,font=("Segoe UI",16,"bold")).pack()

        bar=ttk.Frame(root,padding=(14,0,14,8)); bar.pack(fill="x")
        ttk.Button(bar,text="Refresh",command=self.refresh).pack(side="left")
        ttk.Label(bar,text="Range:").pack(side="left",padx=(12,4))
        combo=ttk.Combobox(bar,textvariable=self.range_var,values=("1 hour","6 hours","24 hours","7 days","All"),state="readonly",width=10)
        combo.pack(side="left"); combo.bind("<<ComboboxSelected>>",lambda _e:self.refresh())
        ttk.Checkbutton(bar,text="Auto refresh",variable=self.auto_refresh).pack(side="left",padx=10)
        ttk.Button(bar,text="Export CSV",command=self.export_csv).pack(side="left",padx=3)
        ttk.Button(bar,text="Export JSON",command=self.export_json).pack(side="left",padx=3)
        ttk.Label(bar,textvariable=self.status_var).pack(side="right")

        self.canvas=tk.Canvas(root,height=220,highlightthickness=1)
        self.canvas.pack(fill="x",padx=14,pady=(0,10))
        self.canvas.bind("<Configure>",lambda _e:self.draw_chart())

        frame=ttk.Frame(root,padding=(14,0,14,14)); frame.pack(fill="both",expand=True)
        self.tree=ttk.Treeview(frame,columns=("time","value","unit","source"),show="headings")
        for key,title,width in (("time","Time (UTC)",280),("value","Sensor value",140),("unit","Unit",100),("source","Source",190)):
            self.tree.heading(key,text=title); self.tree.column(key,width=width,anchor="center")
        sb=ttk.Scrollbar(frame,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self.refresh(); self.schedule_refresh()

    def since(self):
        now=datetime.now(timezone.utc)
        return {"1 hour":now-timedelta(hours=1),"6 hours":now-timedelta(hours=6),"24 hours":now-timedelta(days=1),"7 days":now-timedelta(days=7)}.get(self.range_var.get())

    def refresh(self):
        con=open_db(self.db_path)
        try:
            sensor=latest_sensor(con); status=latest_status(con)
            since=self.since()
            self.history=sensor_history(con,1000,since.isoformat() if since else None)
        finally: con.close()
        self.sensor_var.set(f"{sensor[1]:g} {sensor[2]}" if sensor else "No data")
        self.battery_var.set(f"{status[1]}%" if status else "No data")
        self.reservoir_var.set(f"{status[2]:g} U" if status else "No data")
        self.tree.delete(*self.tree.get_children())
        for row in self.history: self.tree.insert("","end",values=row)
        self.status_var.set(f"{len(self.history)} simulated reading(s)")
        self.draw_chart()

    def schedule_refresh(self):
        if self.auto_refresh.get(): self.refresh()
        self.root.after(5000,self.schedule_refresh)

    def draw_chart(self):
        c=self.canvas; c.delete("all"); w=max(c.winfo_width(),200); h=max(c.winfo_height(),120); pad=28
        rows=list(reversed(self.history))
        if len(rows)<2:
            c.create_text(w/2,h/2,text="Not enough simulated readings for chart"); return
        vals=[float(r[1]) for r in rows]; lo,hi=min(vals),max(vals)
        if hi==lo: hi=lo+1
        pts=[]
        for i,v in enumerate(vals):
            x=pad+i*(w-2*pad)/max(1,len(vals)-1); y=h-pad-(v-lo)*(h-2*pad)/(hi-lo); pts.extend((x,y))
        c.create_line(pad,h-pad,w-pad,h-pad)
        c.create_line(pad,pad,pad,h-pad)
        c.create_line(*pts,width=2)
        c.create_text(pad+4,pad,anchor="nw",text=f"{hi:g}")
        c.create_text(pad+4,h-pad,anchor="sw",text=f"{lo:g}")

    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path:return
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            writer=csv.writer(f); writer.writerow(("timestamp","value","unit","source")); writer.writerows(self.history)
        messagebox.showinfo("Export","CSV exported.")

    def export_json(self):
        path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if not path:return
        data=[dict(zip(("timestamp","value","unit","source"),r)) for r in self.history]
        with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        messagebox.showinfo("Export","JSON exported.")

def run(db_path="minimed_local.sqlite"):
    root=tk.Tk(); LocalViewer(root,db_path); root.mainloop()
