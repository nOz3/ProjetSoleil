from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import copy
import time


fps = 40
_tick2_frame=0
_tick2_fps=20000000 # real raw FPS
_tick2_t0=time.time()

def tick(fps=60):
    global _tick2_frame,_tick2_fps,_tick2_t0
    n=_tick2_fps/fps
    _tick2_frame+=n
    while n>0:
        n-=1
        if time.time()-_tick2_t0>1:
            _tick2_t0=time.time()
            _tick2_fps=_tick2_frame
            _tick2_frame=0





ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())


OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}


trackers = []
cpt_frame = 0
frame_list = []
reverse_frame_list = []
liste_points = []
vs = cv2.VideoCapture(args["video"])
state_var = 0
dico_cpt_frame = {}

def reset_dico(ind):
	global dico_cpt_frame
	print("BEFORE: ")
	print(dico_cpt_frame)
	keys = list(dico_cpt_frame.keys())
	for key in keys:
		if ind in key:
			dico_cpt_frame.pop(key)
	print("AFTER: ")
	print("Index: ")
	print(ind)
	print("\nDico :")
	print(dico_cpt_frame)

def verif_fus(point1, tracker):
	global cpt_frame, trackers, dico_cpt_frame

	trac_ind = trackers.index(tracker)
	for point2 in liste_points:
		pt2_ind = liste_points.index(point2)
		if (point2 != None) and (pt2_ind != trac_ind):
			if abs(point1[0] - point2[0]) < 40 and abs(point1[1] - point2[1]) < 40:

				if not dico_cpt_frame.__contains__((trac_ind, pt2_ind)):
					dico_cpt_frame[(trac_ind, pt2_ind)] = 0
					print("Contains")
				dico_cpt_frame[(trac_ind, pt2_ind)] += 1

				if dico_cpt_frame[(trac_ind, pt2_ind)] >= 20:
					trackers[trac_ind] = None
					liste_points[trac_ind] = None
					print("LOL")
					reset_dico(trac_ind)
					if state_var == 0:
						print("Fusion detectee")
						return(1)
					else:
						print("Separation detectee")
						return(1)
			else:
				dico_cpt_frame[(trac_ind, pt2_ind)] = 0


def stock_frame(frame_list, var):
	vs2 = cv2.VideoCapture(var)
	while True:
		frame = vs2.read()
		frame = frame[1] if args.get("video", False) else frame
		if frame is None:
			break

		frame = imutils.resize(frame, width=600)
		frame_list.append(frame)

stock_frame(frame_list, args["video"])

reverse_frame_list = copy.deepcopy(frame_list)
reverse_frame_list.reverse()


print(len(frame_list))

for frame in frame_list:

	i=0
	while (i < len(trackers)):
		if (trackers[i] != None):
			(success, boxe) = trackers[i].update(frame)
			if success:
				(x, y, w, h) = [int(v) for v in boxe]
				point = [x+(w//2), y+(h//2)]
				cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
				cv2.putText(frame, "Filament "+str(i) , (x, y-2), cv2.FONT_HERSHEY_SIMPLEX,
							0.3, (255,255,255), 1, cv2.LINE_AA)

				liste_points[i] = point
				if (verif_fus(point, trackers[i]) == 1):
					i = 0
				else:
					i+=1
		else:
			i +=1

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("s"):
		liste_points.append(None)
		box = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)

		tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
		tracker.init(frame, box)
		trackers.append(tracker)
	elif key == ord("q"):
		break
	tick(fps)

trackers = []
state_var = 1
time.sleep(2)
z = []
counter = 0
liste_points = []
dico_cpt_frame = {}

for frame in reverse_frame_list:

	i = 0
	while (i < len(trackers)):
		if (trackers[i] != None):
			(success, boxe) = trackers[i].update(frame)
			if success:
				(x, y, w, h) = [int(v) for v in boxe]
				point = [x+(w//2), y+(h//2)]
				cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
				cv2.putText(frame, "Filament "+str(i) , (x, y-2), cv2.FONT_HERSHEY_SIMPLEX,
							0.3, (255,255,255), 1, cv2.LINE_AA)

				liste_points[i] = point
				if (verif_fus(point, trackers[i]) == 1):
					z = copy.deepcopy(reverse_frame_list[:counter])
					i = 0
				else:
					i += 1
		else:
			i+=1

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("s"):
		liste_points.append(None)
		box = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)

		tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
		tracker.init(frame, box)
		trackers.append(tracker)
	elif key == ord("q"):
		break
	tick(fps)
	counter +=1

z.reverse()
taille = len(z)
frame_list_size = len(frame_list)
final_list = frame_list[:frame_list_size - taille]
final_list += z


#print(final_list)

video = cv2.VideoWriter("sortie.avi", 0, 30, (600, 600))



for frame in final_list:
	cv2.imshow("Frame", frame)
	#time.sleep(0.1)
	cv2.waitKey(25)
	video.write(frame)

video.release()

cv2.destroyAllWindows()
