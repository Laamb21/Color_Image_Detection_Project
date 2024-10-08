# this uses document intelligence to ocr

from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os
from concurrent.futures import ThreadPoolExecutor

# Azure setup
endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
key = "18ce006f0ac44579a36bfaf01653254c"
document_intelligence_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)


def analyze_image_with_azure(image_path):
    """
    Uses Azure Document Intelligence to detect text and orientation in the image.
    """
    with open(image_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-read",  # Use the correct model ID
            document=f
        )
        result = poller.result()

    # Analyze and return rotation information (simplified example)
    try:
        # Assume the orientation is detected based on text angle (adjust as needed)
        orientation = result.pages[0].angle if result.pages else 0
        return orientation
    except Exception as e:
        print(f"Failed to analyze {image_path}: {e}")
        return 0


def rotate_image_based_on_ocr(image_path):
    try:
        rotation = analyze_image_with_azure(image_path)

        # If rotation is not zero, rotate the image accordingly
        if rotation != 0:
            image = Image.open(image_path)
            rotated_image = image.rotate(-rotation, expand=True)
            print(f"Rotating {image_path} by {rotation} degrees.")
            rotated_image.save(image_path)  # Overwrite the original image
        else:
            print(f"No rotation needed for {image_path}.")

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

    # Use ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(rotate_image_based_on_ocr, image_paths)


# Replace 'your_directory_path' with the path to the directory containing your images
directory_path = 'your_directory_path'
rotate_images_in_directory(directory_path, max_workers=8)
