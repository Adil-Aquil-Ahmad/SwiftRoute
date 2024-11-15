from SwiftRoute import CarCounter
import time

Traffic1 = CarCounter('Road_A.mp4')
Traffic2 = CarCounter('Road_B.mp4')
Traffic3 = CarCounter('Road_C.mp4')
Traffic4 = CarCounter('Road_D.mp4')

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
            Ain.Light_Color, Din.Light_Color, Aout.Light_Color, Dout.Light_Color, Bin.Light_Color, Cin.Light_Color, Bout.Light_Color, Cout.Light_Color = Bin.Light_Color, Cin.Light_Color, Bout.Light_Color, Cout.Light_Color, Ain.Light_Color, Din.Light_Color, Aout.Light_Color, Dout.Light_Color 
            
            pass
        return Ain.Light_Color, Bin.Light_Color, Cin.Light_Color, Din.Light_Color

    def TimeInterval(self, Ain, Bin, Cin, Din, C_Total):
        Ain.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
        Bin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Cin.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Din.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
        Aout.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
        Bout.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Cout.Time_Interval = (180 * (Cin.Vehicle_Amount + Bin.Vehicle_Amount) / C_Total) + (180 - Ain.Time_Interval)
        Dout.Time_Interval = 180 * (Ain.Vehicle_Amount + Din.Vehicle_Amount) / C_Total
        
        return Ain.Time_Interval, Bin.Time_Interval, Cin.Time_Interval, Din.Time_Interval

# Create instances of Road
Ain = Road("A", "Green", "East", Traffic1[0] + Traffic1[1], Traffic1[4])
Bin = Road("B", "Red", "North", Traffic2[0] + Traffic2[1], Traffic2[4])
Cin = Road("C", "Red", "West", Traffic3[0] + Traffic3[1], Traffic3[4])
Din = Road("D", "Green", "South", Traffic4[0] + Traffic4[1], Traffic4[4])
Aout = Road("A", "Green", "West", Traffic1[2] + Traffic1[3], Traffic1[5])
Bout = Road("B", "Red", "South", Traffic2[2] + Traffic2[3], Traffic2[5])
Cout = Road("C", "Red", "East", Traffic3[2] + Traffic3[3], Traffic3[5])
Dout = Road("D", "Green", "North", Traffic4[2] + Traffic4[3], Traffic4[5])

Car_Total = Ain.Vehicle_Amount + Bin.Vehicle_Amount + Cin.Vehicle_Amount + Din.Vehicle_Amount
P_Total = Ain.People_Amount + Bin.People_Amount + Cin.People_Amount + Din.People_Amount


light_colors = Ain.LightChange(Ain, Bin, Cin, Din, Aout, Bout)
print("Updated Light Colors: Ain -", light_colors[0], ", Bin -", light_colors[1], ", Cin -", light_colors[2], ", Din -", light_colors[3])

time_intervals = Ain.TimeInterval(Ain, Bin, Cin, Din, Car_Total)
print("Updated Time Intervals: Ain -", time_intervals[0], ", Bin -", time_intervals[1], ", Cin -", time_intervals[2], ", Din -", time_intervals[3])

while True:
    if Ain.Light_Color == "Red":
        light_colors = Ain.LightChange(Ain, Bin, Cin, Din, Aout, Bout)
        print("Updated Light Colors: Ain -", light_colors[0], ", Bin -", light_colors[1], ", Cin -", light_colors[2], ", Din -", light_colors[3])
        time.sleep(Ain.Time_Interval)
    else:
        light_colors = Ain.LightChange(Ain, Bin, Cin, Din, Aout, Bout)
        print("Updated Light Colors: Ain -", light_colors[0], ", Bin -", light_colors[1], ", Cin -", light_colors[2], ", Din -", light_colors[3])
        time.sleep(Cin.Time_Interval)


print(Car_Total)
print(P_Total)
print(vars(Ain))
print(vars(Bin))
print(vars(Cin))
print(vars(Din))
print(vars(Aout))
print(vars(Bout))
print(vars(Cout))
print(vars(Dout))
