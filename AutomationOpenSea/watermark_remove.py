import cv2
import numpy as np

# Load the image
img = cv2.imread("/Users/kunaljuneja/AutomationOpenSea/1690977539img_1169liMmX.jpeg")

# Convert to HSV for better color segmentation
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define the color range for the light gray watermark.
# Adjust these values to be more specific to the gray of your watermark.
lower_bound = np.array([0, 0, 210])
upper_bound = np.array([180, 50, 255])

# Create a mask where the watermark colors are
mask = cv2.inRange(hsv, lower_bound, upper_bound)

# Define a region of interest (ROI) where the watermark is located.
height, width, _ = img.shape
roi_top_left = (int(0.5 * width), int(0.4 * height))
roi_bottom_right = (width, int(0.7 * height))
roi_mask = np.zeros_like(mask)
roi_mask[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]] = 1

# Combine the watermark mask with the ROI mask
combined_mask = cv2.bitwise_and(mask, mask, mask=roi_mask)

# Expand the mask slightly
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
expanded_mask = cv2.dilate(combined_mask, kernel, iterations=1)

# Inpainting over the watermark areas
result = cv2.inpaint(img, expanded_mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)

cv2.imwrite("cleaned_image.jpg", result)
