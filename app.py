from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


# ---------------- FCFS ----------------
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival'])
    time = 0
    result = []
    gantt = []

    for p in processes:
        if time < p['arrival']:
            time = p['arrival']

        start = time
        finish = time + p['burst']

        gantt.append({'id': p['id'], 'start': start, 'end': finish})

        wt = start - p['arrival']
        tat = finish - p['arrival']

        result.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': wt,
            'turnaround': tat
        })

        time = finish

    return result, gantt


# ---------------- SJF ----------------
def sjf(processes):
    time = 0
    completed = []
    ready = []
    remaining = processes.copy()
    gantt = []

    while remaining or ready:
        for p in remaining[:]:
            if p['arrival'] <= time:
                ready.append(p)
                remaining.remove(p)

        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: x['burst'])
        p = ready.pop(0)

        start = time
        finish = time + p['burst']

        gantt.append({'id': p['id'], 'start': start, 'end': finish})

        wt = start - p['arrival']
        tat = finish - p['arrival']

        completed.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': wt,
            'turnaround': tat
        })

        time = finish

    return completed, gantt


# ---------------- SRTF ----------------
def srtf(processes):
    n = len(processes)


    remaining_bt = [p['burst'] for p in processes]


    start_time = [-1] * n
    finish_time = [0] * n

    time = 0
    completed = 0
    gantt = []

    last_process = None
    block_start = 0

    while completed < n:
        idx = -1
        min_bt = float('inf')

  
        for i in range(n):
            if processes[i]['arrival'] <= time and remaining_bt[i] > 0:
                if remaining_bt[i] < min_bt:
                    min_bt = remaining_bt[i]
                    idx = i


        if idx == -1:
            time += 1
            continue

        if start_time[idx] == -1:
            start_time[idx] = time

        current_process = processes[idx]['id']

        if last_process != current_process:
            if last_process is not None:
                gantt.append({
                    'id': last_process,
                    'start': block_start,
                    'end': time
                })
            block_start = time
            last_process = current_process

        remaining_bt[idx] -= 1
        time += 1

        if remaining_bt[idx] == 0:
            finish_time[idx] = time
            completed += 1


    if last_process is not None:
        gantt.append({
            'id': last_process,
            'start': block_start,
            'end': time
        })


    result = []
    total_wt = total_tat = 0

    for i in range(n):
        tat = finish_time[i] - processes[i]['arrival']
        wt = tat - processes[i]['burst']

        total_wt += wt
        total_tat += tat

        result.append({
            'id': processes[i]['id'],
            'start': start_time[i],
            'finish': finish_time[i],
            'waiting': wt,
            'turnaround': tat
        })

    return result, gantt


# ---------------- ROUND ROBIN ----------------
def round_robin(processes, quantum):
    time = 0
    queue = []
    gantt = []

    remaining = {p['id']: p['burst'] for p in processes}
    processes.sort(key=lambda x: x['arrival'])
    i = 0

    start_time = {}

    while i < len(processes) or queue:
        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        p = queue.pop(0)


        if p['id'] not in start_time:
            start_time[p['id']] = time

        exec_time = min(quantum, remaining[p['id']])

        start = time
        time += exec_time
        remaining[p['id']] -= exec_time

        gantt.append({'id': p['id'], 'start': start, 'end': time})

        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if remaining[p['id']] > 0:
            queue.append(p)

    result = []
    finish = {g['id']: g['end'] for g in gantt}

    for p in processes:
        tat = finish[p['id']] - p['arrival']
        wt = tat - p['burst']

        result.append({
            'id': p['id'],
            'start': start_time[p['id']],
            'finish': finish[p['id']],
            'waiting': wt,
            'turnaround': tat
        })

    return result, gantt


# ---------------- PRIORITY ----------------
def priority_scheduling(processes):
    time = 0
    completed = []
    ready = []
    remaining = processes.copy()
    gantt = []

    while remaining or ready:
        for p in remaining[:]:
            if p['arrival'] <= time:
                ready.append(p)
                remaining.remove(p)

        if not ready:
            time += 1
            continue

        ready.sort(key=lambda x: x['priority'])
        p = ready.pop(0)

        start = time
        finish = time + p['burst']

        gantt.append({'id': p['id'], 'start': start, 'end': finish})

        wt = start - p['arrival']
        tat = finish - p['arrival']

        completed.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': wt,
            'turnaround': tat
        })

        time = finish

    return completed, gantt


# ---------------- ROUTES ----------------
@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/home')
def home():
    return render_template("home.html")
@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    result = None
    gantt = []
    avg_wt = avg_tat = 0

    if request.method == 'POST':
        algorithm = request.form.get('algorithm')

        processes = []
        i = 0

        while True:
            arrival = request.form.get(f'arrival{i}')
            burst = request.form.get(f'burst{i}')
            p = request.form.get(f'priority{i}')
            priority = int(p) if p and p.isdigit() else 0

            if arrival is None:
                break

            if arrival == '' or burst == '':
                i += 1
                continue

            if priority == '' or priority is None:
                priority = 0

            processes.append({
                'id': f'P{i+1}',
                'arrival': int(arrival),
                'burst': int(burst),
                'priority': int(priority)
            })

            i += 1

        if algorithm == 'fcfs':
            result, gantt = fcfs(processes)

        elif algorithm == 'sjf':
            result, gantt = sjf(processes)

        elif algorithm == 'srtf':
            result, gantt = srtf(processes)

        elif algorithm == 'rr':
            quantum = int(request.form.get('quantum') or 1)
            if quantum <= 0:
                quantum = 1
            result, gantt = round_robin(processes, quantum)

        elif algorithm == 'priority':
            result, gantt = priority_scheduling(processes)

        if result and len(result) > 0:
            n = len(result)
            avg_wt = round(sum(p['waiting'] for p in result) / n, 2)
            avg_tat = round(sum(p['turnaround'] for p in result) / n, 2)
        else:
            avg_wt = avg_tat = 0

    return render_template('index.html',
                       result=result,
                       gantt=gantt,
                       avg_wt=avg_wt,
                       avg_tat=avg_tat,
                       form_data=request.form)


# ---------------- CHATBOT (WITH FALLBACK) ----------------
def local_answer(q):
    q = q.lower()

    def format_answer(title, points, example=None, conclusion=None):
        text = f"{title}:\n\n"
        for p in points:
            text += f"• {p}\n"

        if example:
            text += f"\nExample:\n{example}\n"

        if conclusion:
            text += f"\nConclusion:\n{conclusion}\n"

        return text


    if "vs" in q or "compare" in q or "difference" in q:

        if "fcfs" in q and "sjf" in q:
            return """🔥 FCFS vs SJF

FCFS:
• Executes in arrival order  
• Simple but higher waiting time  

SJF:
• Executes shortest job first  
• Minimizes waiting time  

Example:
P1(5), P2(3)

FCFS → P1 → P2  
SJF → P2 → P1  

🚀 Conclusion:
SJF is more efficient than FCFS."""

        if "sjf" in q and "srtf" in q:
            return """🔥 SJF vs SRTF

SJF:
• Non-preemptive  

SRTF:
• Preemptive  

🚀 Conclusion:
SRTF is more optimal"""


    if "scheduling" in q or "cpu scheduling" in q:
        return """🔥 CPU Scheduling:

• Decides which process runs first
• Optimizes CPU usage
• Reduces waiting time

Types:
1. FCFS
2. SJF
3. SRTF
4. Round Robin
5. Priority"""

    if "starvation" in q:
        return """🔥 Starvation:

• Process waits indefinitely
• Happens in SJF / Priority

🚀 Solution:
Use Aging"""

    if "aging" in q:
        return """🔥 Aging:

• Increases priority over time
• Prevents starvation"""


    if "fcfs" in q:
        return format_answer(
            "🔥 FCFS",
            ["Arrival order", "Non-preemptive"],
            "P1 → P2",
            "Simple but inefficient"
        )

    if "sjf" in q:
        return format_answer(
            "🔥 SJF",
            ["Shortest job first", "Efficient"],
            "P3 → P2 → P1"
        )

    if "srtf" in q:
        return format_answer(
            "🔥 SRTF",
            ["Preemptive SJF", "Interrupts process"]
        )

    if "round robin" in q:
        return format_answer(
            "🔥 Round Robin",
            ["Time quantum", "Fair scheduling"]
        )

    if "priority" in q:
        return format_answer(
            "🔥 Priority",
            ["Higher priority executes first"]
        )

    return "Ask me anything about CPU Scheduling 😄"

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get("question", "").lower()
    if question in ["bye", "exit", "goodbye"]:
        return jsonify({
        "answer": "Bye bro 👋 See you next time!",
        "action": "close"
    })
    if question in ["hi", "hello", "hey"]:
        return jsonify({"answer": "Hey bro 👋 Ask me anything about CPU scheduling!"})

    if any(word in question for word in [
        "cpu", "process", "scheduling", "fcfs", "sjf",
        "srtf", "round", "priority", "starvation", "aging"
    ]):
        return jsonify({"answer": local_answer(question)})

    return jsonify({"answer": "Bro ask something related to CPU scheduling 😄"})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)