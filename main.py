import tkinter as tk
from tkinter import ttk

# Store processes
processes = []
process_count = 1

# Function to add process
def add_process():
    global process_count
    
    at = entry_at.get()
    bt = entry_bt.get()
    pr = entry_pr.get()
    
    if at == "" or bt == "":
        return
    
    pid = f"P{process_count}"
    
    processes.append({
        "pid": pid,
        "at": int(at),
        "bt": int(bt),
        "priority": int(pr) if pr != "" else 0
    })
    
    tree.insert("", "end", values=(pid, at, bt, pr))
    
    process_count += 1
    
    entry_at.delete(0, tk.END)
    entry_bt.delete(0, tk.END)
    entry_pr.delete(0, tk.END)

# Function to clear all
def clear_all():
    global processes, process_count
    processes = []
    process_count = 1
    for item in tree.get_children():
        tree.delete(item)

# Main window
root = tk.Tk()
root.title("CPU Scheduler Simulator")
root.geometry("700x500")

# -------- Input Section --------
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Arrival Time").grid(row=0, column=0, padx=5)
entry_at = tk.Entry(frame_input)
entry_at.grid(row=1, column=0, padx=5)

tk.Label(frame_input, text="Burst Time").grid(row=0, column=1, padx=5)
entry_bt = tk.Entry(frame_input)
entry_bt.grid(row=1, column=1, padx=5)

tk.Label(frame_input, text="Priority").grid(row=0, column=2, padx=5)
entry_pr = tk.Entry(frame_input)
entry_pr.grid(row=1, column=2, padx=5)

btn_add = tk.Button(frame_input, text="Add Process", command=add_process, bg="lightgreen")
btn_add.grid(row=1, column=3, padx=10)

btn_clear = tk.Button(frame_input, text="Clear All", command=clear_all, bg="red")
btn_clear.grid(row=1, column=4, padx=10)

# -------- Table Section --------
columns = ("PID", "Arrival Time", "Burst Time", "Priority")

tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.pack(pady=20)

# -------- Run Button (Next use) --------
btn_run = tk.Button(root, text="Run Simulation", bg="lightblue")
btn_run.pack(pady=10)

root.mainloop()