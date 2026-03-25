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

def fcfs(processes):
    # Sort by Arrival Time
    processes = sorted(processes, key=lambda x: x["at"])
    
    time = 0
    result = []
    
    for p in processes:
        # If CPU is idle
        if time < p["at"]:
            time = p["at"]
        
        start = time
        completion = time + p["bt"]
        
        result.append({
            "pid": p["pid"],
            "at": p["at"],
            "bt": p["bt"],
            "start": start,
            "completion": completion
        })
        
        time = completion
    
    return result

def run_simulation():
    if not processes:
        print("❌ No processes added!")
        return
    
    selected_algo = algo_var.get()
    
    if selected_algo == "FCFS":
        scheduled = fcfs(processes)
    else:
        print(f"⚠️ {selected_algo} not implemented yet")
        return
    
    result, avg_wt, avg_tat = calculate_metrics(scheduled)
    
    print("\n===== FCFS Scheduling Result =====")
    print("PID | AT | BT | ST | CT | WT | TAT")
    
    for p in result:
        print(f"{p['pid']} | {p['at']} | {p['bt']} | {p['start']} | {p['completion']} | {p['wt']} | {p['tat']}")
    
    print("\nAverage Waiting Time:", round(avg_wt, 2))
    print("Average Turnaround Time:", round(avg_tat, 2))


def calculate_metrics(processes):
    total_wt = 0
    total_tat = 0
    
    results = []
    
    for p in processes:
        tat = p["completion"] - p["at"]
        wt = tat - p["bt"]
        
        total_wt += wt
        total_tat += tat
        
        results.append({
            **p,
            "tat": tat,
            "wt": wt
        })
    
    avg_wt = total_wt / len(processes)
    avg_tat = total_tat / len(processes)
    
    return results, avg_wt, avg_tat


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

# -------- Algorithm Selection --------
frame_algo = tk.Frame(root)
frame_algo.pack(pady=10)

tk.Label(frame_algo, text="Select Algorithm:").pack(side=tk.LEFT, padx=5)

algo_var = tk.StringVar()

algo_dropdown = ttk.Combobox(
    frame_algo,
    textvariable=algo_var,
    values=["FCFS", "SJF", "Round Robin", "Priority"],
    state="readonly"
)
algo_dropdown.current(0)
algo_dropdown.pack(side=tk.LEFT, padx=5)

# -------- Run Button (Next use) --------
btn_run = tk.Button(root, text="Run Simulation", bg="lightblue", command=run_simulation)
btn_run.pack(pady=10)

root.mainloop()