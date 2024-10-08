from PIL import Image
import pytesseract
import os


def rotate_image_based_on_ocr(image_path):
    try:
        image = Image.open(image_path)

        # Use pytesseract to determine the orientation
        ocr_result = pytesseract.image_to_osd(image)
        rotation = int(ocr_result.split('\nRotate: ')[1].split('\n')[0])

        # Rotate the image based on the OCR result
        if rotation != 0:
            rotated_image = image.rotate(-rotation, expand=True)
            print(f"Rotating {image_path} by {rotation} degrees.")
            rotated_image.save(image_path)  # Overwrite the original image
        else:
            print(f"No rotation needed for {image_path} based on OCR.")

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def rotate_images_in_directory(directory_path):
    supported_formats = ('.jpg', '.jpeg', '.tif', '.tiff')
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.lower().endswith(supported_formats):
                image_path = os.path.join(root, file_name)
                rotate_image_based_on_ocr(image_path)


# Replace 'your_directory_path' with the path to the directory containing your images
directory_path = '/Volumes/SSD/test_date/crownsville_sample/WASTEWATER-SF-001/AAC-CV-1079/TIF'
rotate_images_in_directory(directory_path)