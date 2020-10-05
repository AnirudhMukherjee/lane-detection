import cv2
import numpy as np

def canny_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    canny = cv2.Canny(blur, 50, 150) # TODO change values based on light levels
    return canny

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    triangle = [np.array([
        (100, height),
        (width-100, height),
        (int(width/2), int(height/4))
    ])]
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, triangle, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 15)
    return line_image

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1 * 3/5)
    x1 = int((y1 - intercept)/ slope)
    x2 = int((y2 - intercept)/ slope)
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        # ignore horizontal lines in slope range between -0.1 to 0.1
        if slope < -0.1:
            left_fit.append((slope, intercept))
        elif slope > 0.1:
            right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)

    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)
    return np.array([left_line, right_line])

image = cv2.imread('test_image.jpg')
lane_image = np.copy(image)
canny = canny_image(lane_image)
cropped_image = region_of_interest(canny)

# find lines
lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]),
        minLineLength=40, maxLineGap=5)

averaged_lines = average_slope_intercept(lane_image, lines)

print('(left, right)', averaged_lines)

# add lines to image
line_image = display_lines(lane_image, averaged_lines)
combo_image = cv2.addWeighted( lane_image, 0.7, line_image, 1, 1)

# display
cv2.imshow('result', combo_image)
cv2.waitKey(0)
#cv2.imwrite('output.jpg', combo_image)

#cap = cv2.VideoCapture("test2.mp4")
#while(cap.isOpened()):
    #_,frame  = cap.read()
    #canny_image = canny(frame)
    #cropped_image = region_of_interest(canny_image)
    #lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]),minLineLength=40,maxLineGap=5)
    #averaged_lines = average_slope_intercept(frame,lines)
    #line_image = display_lines(frame, averaged_lines)
    #combo_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    #cv2.imshow('result',combo_image)
    #if cv2.waitKey(1) == ord('q'):
    #    break
#cap.release()
#cv2.destroyAllWindows()
