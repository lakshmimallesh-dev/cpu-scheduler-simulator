from flask import Flask, render_template, request

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

        result.append({'id': p['id'], 'start': start, 'finish': finish,
                       'waiting': wt, 'turnaround': tat})

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

        completed.append({'id': p['id'], 'start': start, 'finish': finish,
                          'waiting': wt, 'turnaround': tat})

        time = finish

    return completed, gantt


# ---------------- SRTF (PREEMPTIVE SJF) ----------------
def srtf(processes):
    n = len(processes)
    remaining_bt = {p['id']: p['burst'] for p in processes}
    time = 0
    completed = 0
    gantt = []
    last_process = None
    start_time = 0

    while completed < n:
        available = [p for p in processes if p['arrival'] <= time and remaining_bt[p['id']] > 0]

        if not available:
            time += 1
            continue

        available.sort(key=lambda x: remaining_bt[x['id']])
        current = available[0]

        # start new gantt block
        if last_process != current['id']:
            if last_process is not None:
                gantt.append({'id': last_process, 'start': start_time, 'end': time})
            start_time = time
            last_process = current['id']

        remaining_bt[current['id']] -= 1
        time += 1

        if remaining_bt[current['id']] == 0:
            completed += 1

    # last block
    if last_process is not None:
        gantt.append({'id': last_process, 'start': start_time, 'end': time})

    # calculate WT & TAT
    result = []
    finish_time = {}

    for g in gantt:
        finish_time[g['id']] = g['end']

    for p in processes:
        tat = finish_time[p['id']] - p['arrival']
        wt = tat - p['burst']

        result.append({
            'id': p['id'],
            'start': '-',
            'finish': finish_time[p['id']],
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

    while i < len(processes) or queue:
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

        gantt.append({'id': p['id'], 'start': start, 'end': time})

        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if remaining[p['id']] > 0:
            queue.append(p)

    result = []
    finish_time = {}

    for g in gantt:
        finish_time[g['id']] = g['end']

    for p in processes:
        tat = finish_time[p['id']] - p['arrival']
        wt = tat - p['burst']

        result.append({
            'id': p['id'],
            'start': '-',
            'finish': finish_time[p['id']],
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

        completed.append({'id': p['id'], 'start': start, 'finish': finish,
                          'waiting': wt, 'turnaround': tat})

        time = finish

    return completed, gantt


# ---------------- MAIN ROUTE ----------------
@app.route('/')
def intro():
    return render_template('home.html')


@app.route('/simulator', methods=['GET', 'POST'])
def home():
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
            priority = request.form.get(f'priority{i}')

            if arrival is None:
                break

            if arrival == '' or burst == '' or priority == '':
                return render_template('index.html', result=None, gantt=[])

            if int(arrival) < 0 or int(burst) <= 0:
                return render_template('index.html', result=None, gantt=[])

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
            result, gantt = round_robin(processes, quantum)

        elif algorithm == 'priority':
            result, gantt = priority_scheduling(processes)

        if result:
            total_wt = sum(p['waiting'] for p in result)
            total_tat = sum(p['turnaround'] for p in result)
            n = len(result)

            avg_wt = round(total_wt / n, 2)
            avg_tat = round(total_tat / n, 2)

    return render_template('index.html',
                           result=result,
                           gantt=gantt,
                           avg_wt=avg_wt,
                           avg_tat=avg_tat)


if __name__ == '__main__':
    app.run(debug=True)