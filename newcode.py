from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2


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

vs = cv2.VideoCapture(args["video"])


def verif_fus(point1, point2, tracker):
	global cpt_frame, trackers
	if point2 != None:
		if abs(point1[0] - point2[0]) < 50 and abs(point1[1] - point2[1]) < 50:
			cpt_frame += 1
			if cpt_frame >= 10:
				trackers.remove(tracker)
				cpt_frame = 0
		else:
			cpt_frame = 0


while True:

	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame

	if frame is None:
		break

	frame = imutils.resize(frame, width=600)

	old_point = None

	for tracker in trackers:
		(success, boxe) = tracker.update(frame)
		if success:
			(x, y, w, h) = [int(v) for v in boxe]
			point = [x+(w//2), y+(h//2)]
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
			cv2.putText(frame, "Personne "+str(trackers.index(tracker)) , (x, y-2), cv2.FONT_HERSHEY_SIMPLEX,
						0.3, (0,255,0), 1, cv2.LINE_AA)
			verif_fus(point, old_point, tracker)
			old_point = point

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("s"):
		box = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)

		tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
		tracker.init(frame, box)
		trackers.append(tracker)
	elif key == ord("q"):
		break

if not args.get("video", False):
	vs.stop()

else:
	vs.release()

cv2.destroyAllWindows()
