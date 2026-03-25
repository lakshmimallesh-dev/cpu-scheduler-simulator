from flask import Flask, render_template, request

app = Flask(__name__)

# FCFS Algorithm
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival'])
    
    time = 0
    result = []

    for p in processes:
        if time < p['arrival']:
            time = p['arrival']
        
        start = time
        finish = time + p['burst']
        
        waiting = start - p['arrival']
        turnaround = finish - p['arrival']

        result.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': waiting,
            'turnaround': turnaround
        })

        time = finish

    return result

def sjf(processes):
    processes.sort(key=lambda x: (x['arrival'], x['burst']))
    
    time = 0
    completed = []
    ready_queue = []
    remaining = processes.copy()

    while remaining or ready_queue:
        # Add arrived processes
        for p in remaining[:]:
            if p['arrival'] <= time:
                ready_queue.append(p)
                remaining.remove(p)

        if not ready_queue:
            time += 1
            continue

        # Pick shortest job
        ready_queue.sort(key=lambda x: x['burst'])
        p = ready_queue.pop(0)

        start = time
        finish = time + p['burst']

        waiting = start - p['arrival']
        turnaround = finish - p['arrival']

        completed.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': waiting,
            'turnaround': turnaround
        })

        time = finish

    return completed

def round_robin(processes, quantum):
    time = 0
    queue = []
    result = []
    
    remaining = {p['id']: p['burst'] for p in processes}
    arrival_map = {p['id']: p['arrival'] for p in processes}

    processes.sort(key=lambda x: x['arrival'])
    i = 0

    while i < len(processes) or queue:
        # Add arrived processes
        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        p = queue.pop(0)

        exec_time = min(quantum, remaining[p['id']])
        start = time
        time += exec_time
        remaining[p['id']] -= exec_time

        result.append({
            'id': p['id'],
            'start': start,
            'finish': time
        })

        # Add newly arrived processes during execution
        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if remaining[p['id']] > 0:
            queue.append(p)

    # Calculate waiting & turnaround
    final = []
    finish_time = {}

    for r in result:
        finish_time[r['id']] = r['finish']

    for p in processes:
        tat = finish_time[p['id']] - p['arrival']
        wt = tat - p['burst']

        final.append({
            'id': p['id'],
            'start': '-',   # RR has multiple starts
            'finish': finish_time[p['id']],
            'waiting': wt,
            'turnaround': tat
        })

    return final

def priority_scheduling(processes):
    processes.sort(key=lambda x: (x['arrival'], x['priority']))
    
    time = 0
    completed = []
    ready_queue = []
    remaining = processes.copy()

    while remaining or ready_queue:
        # Add arrived processes
        for p in remaining[:]:
            if p['arrival'] <= time:
                ready_queue.append(p)
                remaining.remove(p)

        if not ready_queue:
            time += 1
            continue

        # Pick highest priority (smallest number)
        ready_queue.sort(key=lambda x: x['priority'])
        p = ready_queue.pop(0)

        start = time
        finish = time + p['burst']

        waiting = start - p['arrival']
        turnaround = finish - p['arrival']

        completed.append({
            'id': p['id'],
            'start': start,
            'finish': finish,
            'waiting': waiting,
            'turnaround': turnaround
        })

        time = finish

    return completed

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None

    if request.method == 'POST':
        algorithm = request.form.get('algorithm')

        processes = []

        for i in range(3):
            processes.append({
                'id': f'P{i+1}',
                'arrival': int(request.form.get(f'arrival{i}') or 0),
                'burst': int(request.form.get(f'burst{i}') or 0),
                'priority': int(request.form.get(f'priority{i}') or 0)
            })

        if algorithm == 'fcfs':
            result = fcfs(processes)

        elif algorithm == 'sjf':
            result = sjf(processes)

        elif algorithm == 'rr':
            quantum = int(request.form.get('quantum') or 1)
            result = round_robin(processes, quantum)

        elif algorithm == 'priority':
            result = priority_scheduling(processes)

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)