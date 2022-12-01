import os
import cv2
import mediapipe as mp
import numpy as np
import argparse

from scenedetect import VideoManager
from scenedetect import SceneManager

from scenedetect.detectors import ContentDetector


def find_scenes(video_path, threshold=10.0):
    # video & scene managers, then add the detector.
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=1))

    # Base timestamp at frame 0 (required to obtain the scene list)
    base_timecode = video_manager.get_base_timecode()

    # Improve processing speed by downscaling before processing
    video_manager.set_downscale_factor()

    # Start the video manager and perform the scene detection
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    # Each returned scene is a tuple of the (start, end) timecode.
    return scene_manager.get_scene_list(base_timecode)


# To calculate angle of bend
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180:
        angle = 360-angle

    return angle


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, default=r"C:\Users\jatin\Downloads\KneeBendVideo.mp4", help="Video path")

    opt = parser.parse_args()

    # for drawing on frames
    mp_pose = mp.solutions.pose

    # Reading Video and assigning variables
    video_path = opt.video
    video = cv2.VideoCapture(video_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(os.path.join(os.getcwd(), "kneebend_output.mp4"), fourcc, fps, size)
    reps_count = 0
    bents_frames = 0
    old_bent_time = 0
    bent_times = []
    angles_list = []
    scenes_list = []
    total_dummy_frames = []
    scenes = find_scenes(video_path)

    # Unpacking scenes and Adding frames to list
    for i in scenes:
        a, b = i
        scenes_list.append(int(a))
        scenes_list.append(int(b))

    # Taking unique values of dummy scenes
    np.array(scenes_list)
    dummy_scenes = np.unique(np.array(scenes_list))  # taking unique values of dummy scenes

    # Taking all the dummy frames and appending to the list
    for i in range(len(dummy_scenes)-1):
        if (dummy_scenes[i] - dummy_scenes[i-1]) < fps:
            for i in range(dummy_scenes[i-1], dummy_scenes[i]+1):
                total_dummy_frames.append(i)

    # i will be taken as frame number
    i = 0
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while video.isOpened():
            # Reading Frames
            ret, frame = video.read()
            if i == frames:
                break
            if i not in total_dummy_frames:
                # Converting to RGB Because mediapipe uses RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Processing pose on image
                results = pose.process(image)

                # Converting back to BGR for openCV
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                try:
                    # Taking landmarks from image
                    landmarks = results.pose_landmarks.landmark

                    # Taking Co-ordinates
                    hips = [landmarks[23].x, landmarks[23].y]
                    knee = [landmarks[25].x, landmarks[25].y]
                    ankle = [landmarks[27].x, landmarks[27].y]

                    # Calculating angle
                    angle = calculate_angle(hips, knee, ankle)

                    # creates and image for Visualization
                    shapes = np.zeros_like(image, np.uint8)

                    # Checking knee bend if knee is bent then adding frames in bents_frames
                    if angle < 140:
                        bents_frames += 1

                    # Else printing feedback
                    if angle > 140:
                        bents_frames = 0
                        bent_time = 0
                        cv2.rectangle(shapes, (int((width/2)-200), int(height-85)),  (int((width/2)+200), int(height-20)), (2, 2, 2), cv2.FILLED)
                        cv2.putText(image, "Bend Your Knee", (int((width/2)-190), int(height-35)), cv2.FONT_ITALIC, 1.5, (0, 255, 0), 4, cv2.LINE_AA)

                    # Checking bent time
                    bent_time = bents_frames / fps   # Calculating Bent Time

                    # If bent time is grater than or equal to 8 sec then adding reps and making list of angles
                    if bent_time == 8:
                        reps_count += 1
                        angles_list.append(angle)

                    # If bent time less than 8 sec and more than 2 sec then printing feedback on video
                    if bent_time > 2 and bent_time < 8:
                        cv2.rectangle(shapes, (int((width/2)-260), int(height-85)),  (int((width/2)+260), int(height-20)), (2, 2, 2), cv2.FILLED)
                        cv2.putText(image, "Keep Your Knee Bent", (int((width/2)-255), int(height-35)), cv2.FONT_ITALIC, 1.5, (0, 255, 0), 4, cv2.LINE_AA)

                    # Printing timer on video
                    cv2.circle(shapes, (int((width)-60), 60), 50, (2, 2, 2), cv2.FILLED)
                    cv2.putText(image, 'Timer:', (int((width)-95), 55), cv2.FONT_ITALIC, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, str(np.round(bent_time, 1)), (int((width)-90), 90), cv2.FONT_ITALIC, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

                    # Printing reps on video
                    cv2.circle(shapes, (int((width)-60), 170), 50, (2, 2, 2), cv2.FILLED)
                    cv2.putText(image, str(reps_count), (int((width)-75), 170), cv2.FONT_ITALIC, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
                    cv2.putText(image, 'REP(s)', (int((width)-90), 200), cv2.FONT_ITALIC, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

                    #  Taking bent time and adding to list
                    if bent_time >= 8:
                        old_bent_time = bent_time
                    if old_bent_time >= 8 and bent_time == 0:
                        bent_times.append(old_bent_time)
                        old_bent_time = 0

                    # Mask for make visualization
                    mask = shapes.astype(bool)
                    image[mask] = cv2.addWeighted(shapes, 0.5, image, 1 - 0.5, 0)[mask]

                except Exception as e:
                    print(e)

                out.write(image)
                cv2.imshow("Checking Bend", image)

                if cv2.waitKey(20) & 0xFF == 27:
                    break

            #  Adding 1 to i for next frame
            i += 1

        video.release()
        cv2.destroyAllWindows()

    # Making txt file for stats_of_bendness
    f = open(os.path.join(os.getcwd(), "stats_of_bendness.txt"), "a")
    f.write("Total Reps Done: " + str(reps_count) + "\n")
    for i in range(reps_count):
        f.write(str(i+1) + " Rep was done in " + str(round(bent_times[i], 2)) + " secs and the average angle was " + str(round(angles_list[i], 2)) + "°.\n")
    f.close()


if __name__ == "__main__":
    main()
