import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import csv

def CarCounter(traffic_video):
    model = YOLO('yolov9c.pt')
    model.overrides['verbose'] = True
    model.overrides['device'] = 'cuda' 
    class_list = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 
        'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 
        'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 
        'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 
        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 
        'toothbrush'
    ]
    tracker = Tracker()
    count = 0
    cap = cv2.VideoCapture(traffic_video)

    counter_down_cars = set()
    counter_down_motorcycles = set()
    counter_up_cars = set()
    counter_up_motorcycles = set()
    
    left_people = set()
    right_people = set()
    file_name = f"Vehicle_Database_{traffic_video[5:6]}.csv"
    with open(file_name, 'w', newline='') as f:
        fieldnames = [
            'Road Name', 'Cars Down', 'Motorcycles Down', 'Cars Up', 'Motorcycles Up', 
            'People Left', 'People Right',
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if f.tell() == 0:
            writer.writeheader()

        writer.writerow({
            'Road Name': 0,
            'Cars Down': 0,
            'Motorcycles Down': 0,
            'Cars Up': 0,
            'Motorcycles Up': 0,
            'People Left': 0,
            'People Right': 0,
            })
    y_line = 308  
    left_line = 0  # extreme left position
    right_line = None  # frame width will set later

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        results = model.predict(frame)
        
        a = results[0].boxes.data
        a = a.detach().cpu().numpy()  
        px = pd.DataFrame(a).astype("float")
        
        detected_objects = []
        
        for index, row in px.iterrows():
            x1, y1, x2, y2, d = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[5])
            c = class_list[d]

            if c in ['car', 'motorcycle', 'person', 'truck']:
                detected_objects.append([x1, y1, x2, y2, c])

        bbox_id = tracker.update(detected_objects)

        frame_height, frame_width = frame.shape[:2]
        right_line = frame_width 

        for bbox in bbox_id:
            x3, y3, x4, y4, id, obj_class = bbox
            cx, cy = (x3 + x4) // 2, (y3 + y4) // 2
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
            cv2.putText(frame, f'{obj_class} {id}', (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

            # counting cars and motorcycles moving downwards
            if cx < frame.shape[1] // 2:
                if y_line < (cy + 7) and y_line > (cy - 7):
                    if id not in counter_down_cars and id not in counter_down_motorcycles and id not in right_people and id not in left_people:  
                        if obj_class == 'car':
                            counter_down_cars.add(id)
                        elif obj_class == 'motorcycle':
                            counter_down_motorcycles.add(id)
                        with open(file_name, 'a', newline='') as f:
                            fieldnames = [
                                'Road Name', 'Cars Down', 'Motorcycles Down', 'Cars Up', 'Motorcycles Up', 
                                'People Left', 'People Right',
                            ]
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            f.seek(106)

                            if f.tell() == 0:
                                writer.writeheader()

                            writer.writerow({
                                'Road Name': traffic_video[0:6],
                                'Cars Down': len(counter_down_cars),
                                'Motorcycles Down': len(counter_down_motorcycles),
                                'Cars Up': len(counter_up_cars),
                                'Motorcycles Up': len(counter_up_motorcycles),
                                'People Left': len(left_people),
                                'People Right': len(right_people),
                            })

            # counting cars and motorcycles moving upwards
            if cx >= frame.shape[1] // 2:
                if y_line < (cy + 7) and y_line > (cy - 7):
                    if id not in counter_up_cars and id not in counter_up_motorcycles:  
                        if obj_class == 'car':
                            counter_up_cars.add(id)
                        elif obj_class == 'motorcycle':
                            counter_up_motorcycles.add(id)

            # left line detection of pedestrians
            if obj_class == 'person' and left_line < (cx + 7) and left_line > (cx - 7):
                if id not in left_people:
                    left_people.add(id)

            # right line detection of pedestrians
            if obj_class == 'person' and right_line < (cx + 7) and right_line > (cx - 7):
                if id not in right_people:
                    right_people.add(id)        

        text_color = (255, 255, 255)
        red_color = (0, 0, 255)   

        cv2.line(frame, (0, y_line), (frame_width // 2, y_line), red_color, 3)
        cv2.putText(frame, 'Down Line', (10, y_line - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        cv2.line(frame, (frame_width // 2, y_line), (frame_width, y_line), red_color, 3)
        cv2.putText(frame, 'Up Line', (frame_width // 2 + 10, y_line - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        # Drawing extreme left and right lines
        cv2.line(frame, (left_line, 0), (left_line, frame_height), red_color, 3)
        cv2.putText(frame, 'Left Line', (left_line + 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
        cv2.line(frame, (right_line, 0), (right_line, frame_height), red_color, 3)
        cv2.putText(frame, 'Right Line', (right_line + 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        cars_down = len(counter_down_cars)
        motorcycles_down = len(counter_down_motorcycles)
        cars_up = len(counter_up_cars)
        motorcycles_up = len(counter_up_motorcycles)
        people_left = len(left_people)
        people_right = len(right_people)

        cv2.putText(frame, f'Cars Down: {cars_down}', (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f'Motorcycles Down: {motorcycles_down}', (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f'Cars Up: {cars_up}', (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f'Motorcycles Up: {motorcycles_up}', (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f'People Left: {people_left}', (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f'People Right: {people_right}', (300, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1, cv2.LINE_AA)

        cv2.imshow("frames", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return cars_down, motorcycles_down, cars_up, motorcycles_up, people_left, people_right


