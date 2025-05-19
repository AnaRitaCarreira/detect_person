# People detection alarm system

#### Here you can find the yolov5 from ultralytics modified code that I used to detect people and make a sound when the person is in the frame. 
#### It also saves the frame and puts the date and time detected. 
#### You can change the hours you want it to work.

(https://github.com/AnaRitaCarreira/AnaCarreira/blob/main/yolov5_alarm/yolov5/detected_person/2025_04_11_11_54_45_088709.png?raw=true)
#### requirements for windows:

- pygame:
  - pip install pygame
- torch:
  - pip3 install torch torchvision torchaudio
- cv2:
  - pip install opencv-python 
- pandas:
  - pip install pandas
- requests
  - pip install requests
- ultralytics:
  - pip install ultralytics

usage:

    python ./yolov5/detect_person.py --source "ADD THE URL/PATH to your source" 
