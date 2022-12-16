# kneebend
Kneedbend with timer and video cleaner.<br />
In This Project, I will remove fluctuating frames from the video first and then finds the angle of the knee if the angle is less than 140° then the timer will begin and if the timer goes 8 seconds and above then add Single rep to Reps count.

## INSTRUCTIONS
### This project requires the following libraries<br />

• [Os](https://python.readthedocs.io/en/stable/library/os.html)<br />
• [Cv2(OpenCV)](https://docs.opencv.org/4.x/)<br />
• [Mediapipe](https://google.github.io/mediapipe/)<br />
• [Numpy](https://numpy.org/)<br />
• [scene detect](http://scenedetect.com/en/latest/)<br />

### Please ensure you have installed the following libraries mentioned above before continuing.


## HOW TO RUN knee_bend.py

open cmd in the file directory and write:
python knee_bend.py --video "path"

for eg: python knee_bend.py --video "C://user//jatin//downloads//kneebend.mp4"

You will get stats_of_bendness.txt in the same directory where the knee_bend.py file is saved
and kneebend_output.mp4 will also be saved in the same directory.

Press "Esc" on video windows to stop the code.
