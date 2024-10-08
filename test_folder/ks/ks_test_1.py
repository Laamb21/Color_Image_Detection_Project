from PIL import Image
import pytesseract
import os

# Define directories
tiff_dir = '/Users/kevinshieldsjr/Desktop/sample/WASTEWATER-SF-001/AAC-CV-1079/TIF'
jpeg_dir = '/Users/kevinshieldsjr/Desktop/sample/WASTEWATER-SF-001/AAC-CV-1079/JPG'
output_dir = '/Users/kevinshieldsjr/Desktop/sample/WASTEWATER-SF-001/AAC-CV-1079/YEA'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over TIFF files
for tiff_filename in os.listdir(tiff_dir):
    if tiff_filename.startswith("10") or tiff_filename.startswith("20"):
        tiff_path = os.path.join(tiff_dir, tiff_filename)
        # Derive the color JPEG path
        color_filename = tiff_filename.replace("10", "11").replace("20", "21")
        jpeg_path = os.path.join(jpeg_dir, color_filename)

        try:
            # Open the TIFF image
            tiff_image = Image.open(tiff_path)

            # Perform OCR to check for text
            ocr_text = pytesseract.image_to_string(tiff_image)

            # Check if image contains significant non-text content (images, graphs)
            # Replace if the page is detected as containing images or if OCR content is minimal
            if 'image' in ocr_text.lower() or len(ocr_text.strip()) < 50:
                if os.path.exists(jpeg_path):
                    # Replace with color image if condition is met and color image exists
                    color_image = Image.open(jpeg_path)
                    color_image.save(os.path.join(output_dir, tiff_filename))
                    print(f'Replaced: {tiff_filename} with its color version.')
                else:
                    # Log if the corresponding color JPEG is missing
                    print(f'Color JPEG not found for: {tiff_filename}, using original TIFF.')
                    tiff_image.save(os.path.join(output_dir, tiff_filename))
            else:
                # Save the original black-and-white image if it's text-only
                tiff_image.save(os.path.join(output_dir, tiff_filename))
                print(f'Kept original TIFF for: {tiff_filename}')

        except Exception as e:
            print(f'Error processing {tiff_filename}: {e}')