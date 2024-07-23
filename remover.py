from PIL import Image
import numpy as np
import cv2
from rembg import remove


# Threshold Variables
BLUR_THRESHOLD = 100  # Variance of Laplacian threshold. Typical values: min=10, avg=100, max=200
EDGE_COUNT_THRESHOLD = 2000  # Edge count threshold. Typical values: min=500, avg=1000, max=2000
WHITE_BG_THRESHOLD = 240  # RGB threshold to consider a pixel as white. Typical values: min=200, avg=240, max=255
WHITE_BG_PERCENTAGE = 0.9  # Percentage of white pixels in the corners to consider background as white. Typical values: min=0.5, avg=0.9, max=1.0

def crop_to_content_with_alpha(image):
    """Crop image to content based on tranperancy for alpha channel"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha_channel = image.split()[3]
    if alpha_channel.getextrema()[0]<255:
        bbox = alpha_channel.getbbox()
        if bbox:
            cropped_image = image.crop(bbox)
            return cropped_image
    return image

def crop_to_content_without_alpha(image_path):
    """Crop image to content based on contours for images without alpha channel"""
    image = Image.open(image_path)
    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGRA)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray,(5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    dilated = cv2.dilate(edges, None, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        cropped_image = open_cv_image[y:y+h, x:x+w]
        cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BAYER_BG2BGR)
        pil_cropped_image = Image.fromarray(cropped_image_rgb)
        return pil_cropped_image
    return Image.open(image_path)

def is_image_vertical(image):
    """Check if the image us vertical (portrait orientation)"""
    width, height = image.size
    return height>width

def rotate_to_vertical(image):
    "Rotate image is vertical if it is not portrait oriented"
    if not is_image_vertical(image):
        image = image.rotate(90, expand=True)
    return image

def remove_background(img):
    """Remove the background from the image"""
    try:
        output = remove(img)
        return output
    except Exception as e:
        raise RuntimeError(f"Error removing background: {e}")
    
def resize_image(cropped_image, canvas_width, canvas_height, fixed_margin):
    """ Resize the image to fit within the specified canvas dimensions"""
    aspect_ratio = cropped_image.width / cropped_image.height
    max_width = canvas_width -2 * fixed_margin
    max_height = canvas_height -2 * fixed_margin
    scale_factor = min(max_width/ cropped_image.width, max_height / cropped_image.height)
    new_width = int(cropped_image.width * scale_factor)
    new_height = int(cropped_image.height * scale_factor)
    resized_image = cropped_image.resize((new_width, new_height), Image.LANCZOS)
    paste_x = (canvas_width - new_width) //2
    paste_y = (canvas_height - new_height)//2
    final_image = Image.new("RGBA", (canvas_height, canvas_width), (0,0,0,0))
    # Fixed variable names and mask handling
    mask = resized_image.split()[3] if "A" in resized_image.getbands() else None
    final_image.paste(resized_image, (paste_x, paste_y), mask=mask)
    return final_image
    
def process_image(image, canvas_width, canvas_height, fixed_margin):
    """Process a single image: removes background , crop , rotate, and resize"""
    output = remove_background(image)
    if output:
        cropped_image = crop_to_content_with_alpha(output)
        cropped_image = rotate_to_vertical(cropped_image)
        resized_image = resize_image(cropped_image, canvas_width, canvas_height, fixed_margin)
        return resized_image
    return None