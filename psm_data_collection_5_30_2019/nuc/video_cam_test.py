import numpy as np
import cv2

def capture_image():
	cam = 1
	try:
		cap = cv2.VideoCapture(cam)
	except Exeception as err:
		print (err)

	while(cap.isOpened()):
		cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
		cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
		ret, frame = cap.read()
		gray = cv2.cvtColor(frame, 1)

		cv2.imshow('frame',gray)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()

capture_image()
