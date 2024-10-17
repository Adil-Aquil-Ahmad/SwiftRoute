import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *

def CarCounter(traffic_video):
    model = YOLO('yolov9c.pt')
    model.overrides['verbose'] = True
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

    y_line = 308  
    left_line = 0  # Vertical line position for extreme left detection
    right_line = None  # This will be set to the frame width later

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

        # Set the right line position to the width of the frame
        frame_height, frame_width = frame.shape[:2]
        right_line = frame_width  # Vertical line position for extreme right detection

        for bbox in bbox_id:
            x3, y3, x4, y4, id, obj_class = bbox
            cx, cy = (x3 + x4) // 2, (y3 + y4) // 2
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
            cv2.putText(frame, f'{obj_class} {id}', (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

            # Counting cars and motorcycles moving downwards
            if cx < frame.shape[1] // 2:  # Downward counting
                if y_line < (cy + 7) and y_line > (cy - 7):
                    if id not in counter_down_cars and id not in counter_down_motorcycles:  
                        if obj_class == 'car':
                            counter_down_cars.add(id)
                        elif obj_class == 'motorcycle':
                            counter_down_motorcycles.add(id)

            # Counting cars and motorcycles moving upwards
            if cx >= frame.shape[1] // 2:  # Upward counting
                if y_line < (cy + 7) and y_line > (cy - 7):
                    if id not in counter_up_cars and id not in counter_up_motorcycles:  
                        if obj_class == 'car':
                            counter_up_cars.add(id)
                        elif obj_class == 'motorcycle':
                            counter_up_motorcycles.add(id)

            # Left line detection for people
            if obj_class == 'person' and left_line < (cx + 7) and left_line > (cx - 7):
                if id not in left_people:
                    left_people.add(id)

            # Right line detection for people
            if obj_class == 'person' and right_line < (cx + 7) and right_line > (cx - 7):
                if id not in right_people:
                    right_people.add(id)

        text_color = (255, 255, 255)
        red_color = (0, 0, 255)   

        cv2.line(frame, (0, y_line), (frame_width // 2, y_line), red_color, 3)
        cv2.putText(frame, 'Down Line', (10, y_line - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        cv2.line(frame, (frame_width // 2, y_line), (frame_width, y_line), red_color, 3)
        cv2.putText(frame, 'Up Line', (frame_width // 2 + 10, y_line - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        # Draw extreme left and right lines
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


