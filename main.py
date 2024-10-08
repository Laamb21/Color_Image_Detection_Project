from PIL import Image
import pytesseract
import os
from concurrent.futures import ThreadPoolExecutor


def rotate_image_based_on_ocr(image_path):
    try:
        image = Image.open(image_path)

        # Create a smaller copy for OCR to speed up processing
        ocr_image = image.copy()
        ocr_image.thumbnail((800, 800))

        # Use pytesseract to determine the orientation with additional config
        ocr_result = pytesseract.image_to_osd(ocr_image, config='--psm 0')
        rotation = int(ocr_result.split('\nRotate: ')[1].split('\n')[0])
        ocr_image.close()

        # Rotate the image based on the OCR result
        if rotation != 0:
            rotated_image = image.rotate(-rotation, expand=True)
            print(f"Rotating {image_path} by {rotation} degrees.")
            rotated_image.save(image_path)
        else:
            print(f"No rotation needed for {image_path}.")

        image.close()

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def rotate_images_in_directory(directory_path, max_workers=4):
    supported_formats = ('.jpg', '.jpeg', '.tif', '.tiff')
    image_paths = [
        os.path.join(root, file_name)
        for root, _, files in os.walk(directory_path)
        for file_name in files
        if file_name.lower().endswith(supported_formats)
    ]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(rotate_image_based_on_ocr, image_paths)


# Replace 'your_directory_path' with the path to the directory containing your images
directory_path = '/Volumes/SSD/test_date/crownsville_sample/WASTEWATER-SF-002/AAC-CV-1154'
rotate_images_in_directory(directory_path, max_workers=8)