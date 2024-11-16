from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from SwiftRoute import CarCounter
import csv
from concurrent.futures import ProcessPoolExecutor
import hashlib
from User import load_users, save_user, hash_password

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = []
    with open('User_Database.csv', newline='') as f:
        reader = csv.DictReader(f)
        for user in reader:
            users.append(user)
    return users

def save_user(username, email, password):
    with open('User_Database.csv', 'a', newline='') as f:
        fieldnames = ['username', 'email', 'password']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({'username': username, 'email': email, 'password': hash_password(password)})


app = Flask(__name__)
app.secret_key = 'your_secret_key'

credentials = {
    'adil': 'adil786',
    'arveen': 'arveen786'
}

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
        return CarCounter(video)
    except Exception as e:
        print(f"Error processing {video}: {e}")
        return [0, 0, 0, 0, 0]

@app.route('/')
def index():
    open('Vehicle_Database_A.csv', 'w') 
    open('Vehicle_Database_B.csv', 'w')
    open('Vehicle_Database_C.csv', 'w')
    open('Vehicle_Database_D.csv', 'w')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
            
        for user in users:
            if user['username'] == username and user['password'] == hash_password(password):
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            
        flash("Invalid username or password.", "danger")
        return redirect(url_for('login'))
        
    return render_template('INDEX.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))

        users = load_users()
        if any(user['username'] == username for user in users):
            flash("Username already taken.", "danger")
            return redirect(url_for('register'))
            
        save_user(username, email, password)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('Register.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        flash('You are not logged in.')
        return redirect(url_for('index'))
    return render_template('dashboard1.html', username=username)

@app.route('/update_traffic')
def update_traffic():
    videos = ['Road_A.mp4', 'Road_B.mp4', 'Road_C.mp4', 'Road_D.mp4']

    with ProcessPoolExecutor(max_workers=len(videos)) as executor:
        results = list(executor.map(process_video, videos))

    Traffic1, Traffic2, Traffic3, Traffic4 = results

    Ain = Road("A", "Green", "East", Traffic1[0] + Traffic1[1], Traffic1[4])
    Bin = Road("B", "Red", "North", Traffic2[0] + Traffic2[1], Traffic2[4])
    Cin = Road("C", "Red", "West", Traffic3[0] + Traffic3[1], Traffic3[4])
    Din = Road("D", "Green", "South", Traffic4[0] + Traffic4[1], Traffic4[4])
    
    C_Total = Ain.Vehicle_Amount + Bin.Vehicle_Amount + Cin.Vehicle_Amount + Din.Vehicle_Amount
    if C_Total < 1:
        C_Total = 1
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
    global people_total
    global car_total

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

        people_total = int(road_A['People Right']) + int(road_B['People Right']) + int(road_C['People Right']) + int(road_D['People Right']) + int(road_A['People Left']) + int(road_B['People Left']) + int(road_C['People Left']) + int(road_D['People Left'])
        car_total = int(road_A['Cars Down']) + int(road_B['Cars Down']) + int(road_C['Cars Down']) + int(road_D['Cars Down']) + int(road_A['Cars Up']) + int(road_B['Cars Up']) + int(road_C['Cars Up']) + int(road_D['Cars Up'])
        
        data = {
        'car_total':  car_total,
        'pedestrian_total': people_total,
        'Ain': int(road_A['Cars Down']) + int(road_A['Cars Up']),
        'Bin': int(road_B['Cars Down']) + int(road_B['Cars Up']),
        'Cin': int(road_C['Cars Down']) + int(road_C['Cars Up']),
        'Din': int(road_D['Cars Down']) + int(road_D['Cars Up']),
    }
    
    return jsonify(data)

@app.route('/time_update')
def time_update():
    if car_total<50:
        time1 = 30
        time2 = 30
    else:
        time1 = ((int(road_A['Cars Up']) + int(road_A['Cars Down']) + int(road_D['Cars Up']) + int(road_A['Cars Down']))/car_total)*60
        time2 = 60 - (((int(road_A['Cars Up']) + int(road_A['Cars Down']) + int(road_D['Cars Up']) + int(road_A['Cars Down']))/car_total)*60)

    data = {
        'ain_time': round(time1),
        'bin_time': round(time2),
        'cin_time': round(time2),
        'din_time': round(time1),
        "ain_color": "green",
        "bin_color": "red",
        "cin_color": "red",
        "din_color": "green"
    }
    
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
