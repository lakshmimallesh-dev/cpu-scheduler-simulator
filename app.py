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




@app.route('/', methods=['GET', 'POST'])
def home():
    result = None

    if request.method == 'POST':
        algorithm = request.form.get('algorithm')

        processes = [
            {'id': 'P1', 'arrival': 0, 'burst': 5},
            {'id': 'P2', 'arrival': 1, 'burst': 3},
            {'id': 'P3', 'arrival': 2, 'burst': 2}
        ]

        if algorithm == 'fcfs':
            result = fcfs(processes)
        elif algorithm == 'sjf':
            result = sjf(processes)

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)