from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from SwiftRoute import CarCounter
import csv
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor


app = Flask(__name__)
app.secret_key = 'your_secret_key'



roads = {}
road_A = {}
road_B = {}
road_C = {}
road_D = {}

class Road:
    def __init__(self, Name: str, Light_Color: str, Direction: str, Vehicle_Amount=0, People_Amount=0, Time_Interval=180):
        self.Name = Name
        self.Light_Color = Light_Color
        self.Direction = Direction
        self.Vehicle_Amount = Vehicle_Amount
        self.People_Amount = People_Amount
        self.Time_Interval = Time_Interval
    
    def LightChange(self, Ain, Bin, Cin, Din, Aout, Bout):
        if 3 * Bin.People_Amount + 3 * Bout.People_Amount > Bin.Vehicle_Amount + Bout.Vehicle_Amount:
            Ain.Light_Color = "Green"
            Bin.Light_Color = "Red"
            Cin.Light_Color = "Red"
            Din.Light_Color = "Green"
        elif 3 * Bin.People_Amount + 3 * Bout.People_Amount > Ain.Vehicle_Amount + Aout.Vehicle_Amount:
            Ain.Light_Color = "Green"
            Bin.Light_Color = "Red"
            Cin.Light_Color = "Red"
            Din.Light_Color = "Green"
        else:
            pass
        return Ain.Light_Color, Bin.Light_Color, Cin.Light_Color, Din.Light_Color

    def TimeInterval(self, Ain, Bin, Cin, Din, C_Total):
        Ain.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
        Bin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Cin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Din.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
            
        return Ain.Time_Interval, Bin.Time_Interval, Cin.Time_Interval, Din.Time_Interval

def process_video(video):
    try:
        return CarCounter(video)  # Replace this with your actual CarCounter logic
    except Exception as e:
        print(f"Error processing {video}: {e}")
        return [0, 0, 0, 0, 0]  # Default empty result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with open('credentials.txt','r') as f:
        for line in f.readlines(): 
            u1,p1=line.strip().split(':')
            if username==u1:
                    if password == p1:
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
    # Define video files
    videos = ['Road_A.mp4', 'Road_B.mp4', 'Road_C.mp4', 'Road_D.mp4']

    # Use ProcessPoolExecutor to run in parallel
    with ProcessPoolExecutor(max_workers=len(videos)) as executor:
        results = list(executor.map(process_video, videos))

    # Extract results
    Traffic1, Traffic2, Traffic3, Traffic4 = results

    Ain = Road("A", "Green", "East", Traffic1[0] + Traffic1[1], Traffic1[4])
    Bin = Road("B", "Red", "North", Traffic2[0] + Traffic2[1], Traffic2[4])
    Cin = Road("C", "Red", "West", Traffic3[0] + Traffic3[1], Traffic3[4])
    Din = Road("D", "Green", "South", Traffic4[0] + Traffic4[1], Traffic4[4])

    C_Total = Ain.Vehicle_Amount + Bin.Vehicle_Amount + Cin.Vehicle_Amount + Din.Vehicle_Amount
    Ain.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
    Bin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
    Cin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
    Din.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total

@app.route('/realtime_update')
def realtime_update():
    global road_A
    global road_B
    global road_C
    global road_D

    with open('Vehicle_Database_A.csv', 'r') as f:
        reader = csv.DictReader(f)
        road_inst = list(reader)
        for a in road_inst:
            road_A = a
    with open('Vehicle_Database_B.csv', 'r') as f:
        reader = csv.DictReader(f)
        road_inst = list(reader)
        for a in road_inst:
            road_B = a
    with open('Vehicle_Database_C.csv', 'r') as f:
        reader = csv.DictReader(f)
        road_inst = list(reader)
        for a in road_inst:
            road_C = a
    with open('Vehicle_Database_D.csv', 'r') as f:
        reader = csv.DictReader(f)
        road_inst = list(reader)
        for a in road_inst:
            road_D = a


        data = {
        'car_total': int(road_A['Cars Down']) + int(road_B['Cars Down']) + int(road_C['Cars Down']) + int(road_D['Cars Down']) + int(road_A['Cars Up']) + int(road_B['Cars Up']) + int(road_C['Cars Up']) + int(road_D['Cars Up']),
        'pedestrian_total': int(road_A['People Right']) + int(road_B['People Right']) + int(road_C['People Right']) + int(road_D['People Right']) + int(road_A['People Left']) + int(road_B['People Left']) + int(road_C['People Left']) + int(road_D['People Left']),
        'Ain': int(road_A['Cars Down']) + int(road_A['Cars Up']),
        'Bin': int(road_B['Cars Down']) + int(road_B['Cars Up']),
        'Cin': int(road_C['Cars Down']) + int(road_C['Cars Up']),
        'Din': int(road_D['Cars Down']) + int(road_D['Cars Up']),
        'ain_time': int(road_A['Cars Down']),
        'bin_time': int(road_B['Cars Down']),
        'cin_time': int(road_C['Cars Down']),
        'din_time': int(road_D['Cars Down']),
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
