from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from SwiftRoute import CarCounter

app = Flask(__name__)
app.secret_key = 'your_secret_key'

credentials = {
    'adil': 'adil786',
    'arveen': 'arveen786'
}

class Road:
    def __init__(self, Name: str, Light_Color: str, Direction: str, Vehicle_Amount=0, People_Amount=0, Time_Interval=180):
        self.Name = Name
        self.Light_Color = Light_Color
        self.Direction = Direction
        self.Vehicle_Amount = Vehicle_Amount
        self.People_Amount = People_Amount
        self.Time_Interval = Time_Interval

roads = {}

def run_traffic_counting():
    Traffic1 = CarCounter('traffic_video1.mp4')
    Traffic2 = CarCounter('traffic_video2.mp4')
    Traffic3 = CarCounter('traffic_video3.mp4')
    Traffic4 = CarCounter('traffic_video4.mp4')

    roads['A'] = Road("A", "Green", "East", Traffic1[0] + Traffic1[1], Traffic1[4])
    roads['B'] = Road("B", "Red", "North", Traffic2[0] + Traffic2[1], Traffic2[4])
    roads['C'] = Road("C", "Red", "West", Traffic3[0] + Traffic3[1], Traffic3[4])
    roads['D'] = Road("D", "Green", "South", Traffic4[0] + Traffic4[1], Traffic4[4])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in credentials and credentials[username] == password:
        session['username'] = username
        run_traffic_counting() # Start traffic counting on successful login
        return redirect(url_for('dashboard'))

    flash('Invalid credentials. Please try again.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        flash('You are not logged in.')
        return redirect(url_for('index'))
    return render_template('dashboard1.html', username=username)

@app.route('/update_traffic')
        
def update_traffic():
    if not roads:
        return jsonify({"error": "Traffic data is not available."}), 500

    Ain = roads['A']
    Bin = roads['B']
    Cin = roads['C']
    Din = roads['D']
    C_Total = Ain.Vehicle_Amount + Bin.Vehicle_Amount + Cin.Vehicle_Amount + Din.Vehicle_Amount
    Ain.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
    Bin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
    Cin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
    Din.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
   
    data = {
        'car_total': Ain.Vehicle_Amount + Bin.Vehicle_Amount + Cin.Vehicle_Amount + Din.Vehicle_Amount,
        'pedestrian_total': Ain.People_Amount + Bin.People_Amount + Cin.People_Amount + Din.People_Amount,
        'Ain': Ain.Vehicle_Amount,
        'Bin': Bin.Vehicle_Amount,
        'Cin': Cin.Vehicle_Amount,
        'Din': Din.Vehicle_Amount,
        'ain_time': Ain.Time_Interval,
        'bin_time': Bin.Time_Interval,
        'cin_time': Cin.Time_Interval,
        'din_time': Din.Time_Interval,
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
