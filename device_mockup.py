import io

import cv2
from PIL import Image, ImageDraw


def find_inner_rectangle(frame_path):
    # Read the frame image
    frame = cv2.imread(frame_path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get binary image
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and get the second largest (largest is the whole image)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    inner_contour = contours[1]

    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(inner_contour)

    return x, y, w, h


def create_rounded_mask(size, radius):
    """Create a rounded rectangle mask"""
    width, height = size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw the main rectangle
    draw.rectangle([radius, radius, width - radius, height - radius], fill=255)

    # Draw the four corners
    draw.pieslice([0, 0, radius * 2, radius * 2], 180, 270, fill=255)
    draw.pieslice([width - radius * 2, 0, width, radius * 2], 270, 360, fill=255)
    draw.pieslice([0, height - radius * 2, radius * 2, height], 90, 180, fill=255)
    draw.pieslice([width - radius * 2, height - radius * 2, width, height], 0, 90, fill=255)

    # Fill in the gaps
    draw.rectangle([radius, 0, width - radius, height], fill=255)
    draw.rectangle([0, radius, width, height - radius], fill=255)

    return mask


def frame_image(frame):
    if frame == 'iPhone 15 pro':
        frame_path = 'images/frames/iphone_15_pro_frame.png'
        corner_radius = 120
    elif frame == 'Pixel 7':
        frame_path = 'images/frames/pixel_7_frame.png'
        corner_radius = 30
    else:
        raise ValueError('Invalid frame')
    return frame_path, corner_radius


def embed_image_in_frame_by_fit(image, frame, corner_radius, x, y, w, h):
    # Resize the image to fit the inner rectangle
    image = image.resize((w, h), Image.Resampling.LANCZOS)

    # Create a mask for rounded corners
    mask = create_rounded_mask(image.size, corner_radius)

    # Create a new image with the same size as the frame
    result = Image.new('RGBA', frame.size, (0, 0, 0, 0))

    # Paste the resized and rounded image onto the result
    result.paste(image, (x, y), mask)

    # Paste the frame on top
    result = Image.alpha_composite(result, frame.convert('RGBA'))

    return result


def embed_image_in_frame_by_contain(image, frame, corner_radius, x, y, w, h):
    # Calculate scaling factors
    scale_x = image.width / w
    scale_y = image.height / h

    # Calculate new frame size
    new_frame_width = int(frame.width * scale_x)
    new_frame_height = int(frame.height * scale_y)

    # Resize the frame
    frame = frame.resize((new_frame_width, new_frame_height), Image.Resampling.LANCZOS)

    # Create a mask for rounded corners
    mask = create_rounded_mask(image.size, corner_radius)

    # Create a new image with the same size as the frame
    result = Image.new('RGBA', frame.size, (0, 0, 0, 0))

    # Calculate new position of the inner rectangle
    new_x = int(x * scale_x)
    new_y = int(y * scale_y)

    # Paste the resized and rounded image onto the result
    result.paste(image, (new_x, new_y), mask)

    # Paste the frame on top
    result = Image.alpha_composite(result, frame.convert('RGBA'))

    return result


def embed_image_in_frame(image, frame, option):
    frame_path, corner_radius = frame_image(frame)
    x, y, w, h = find_inner_rectangle(frame_path)

    # Open the images
    frame = Image.open(frame_path)
    image = Image.open(image)

    # Embed the image in the frame
    if option == 'fit':
        result = embed_image_in_frame_by_fit(image, frame, corner_radius, x, y, w, h)
    elif option == 'contain':
        result = embed_image_in_frame_by_contain(image, frame, corner_radius, x, y, w, h)
    else:
        raise ValueError('Invalid option')

    # Save the result
    result_io = io.BytesIO()
    result.save(result_io, format='PNG')
    result_io.seek(0)
    return result_io
