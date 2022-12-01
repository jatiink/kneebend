# kneebend
Kneedbend with timer and video cleaner
############ INSTRUCTIONS ##############

Libraries(dependencies) used
1. os
2. cv2
3. mediapipe
4. numpy
5. argparse
6. scene detect

How to install those libraries
pip install os
pip install opencv-python
pip install mediapipe
pip install numpy
pip install argparse
pip install scenedetect


############ HOW TO RUN knee_bend.py ##############

open cmd in the file directory and write:
python knee_bend.py --video "path"

for eg: python knee_bend.py --video "C://user//jatin//downloads//kneebend.mp4"

You will get stats_of_bendness.txt in the same directory where the knee_bend.py file is saved
and kneebend_output.mp4 will also be saved in the same directory.

Press "Esc" on video windows to stop the code.
