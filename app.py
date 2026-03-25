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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # sample data (temporary)
        processes = [
            {'id': 'P1', 'arrival': 0, 'burst': 5},
            {'id': 'P2', 'arrival': 1, 'burst': 3},
            {'id': 'P3', 'arrival': 2, 'burst': 2}
        ]

        result = fcfs(processes)
        return render_template('index.html', result=result)

    return render_template('index.html', result=None)


if __name__ == '__main__':
    app.run(debug=True)