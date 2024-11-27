#Test file to list all colors detected in JPG images



'''
ChatGPT Code:
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import webcolors
from webcolors import *
import argparse

def closest_color(requested_color):
    """Find the closest color name for an RGB value."""
    min_colors = {}
    for key, name in webcolors.hex_to_name():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        # Compute Euclidean distance between colors
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    # Return the name with the smallest distance
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb_color):
    """Convert RGB to the closest color name."""
    try:
        # Try to get the exact color name
        name = webcolors.rgb_to_name(rgb_color, spec='css3')
    except ValueError:
        # If exact name not found, find the closest one
        name = closest_color(rgb_color)
    return name

def extract_colors(image_path, num_colors=5, resize=True, resize_max=800):
    """
    Extract dominant colors from an image.

    :param image_path: Path to the JPG image.
    :param num_colors: Number of dominant colors to extract.
    :param resize: Whether to resize the image for faster processing.
    :param resize_max: Maximum size to resize the image.
    :return: List of tuples containing color names and their RGB values.
    """
    # Load image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image at path '{image_path}' cannot be loaded.")
    
    # Convert from BGR (OpenCV) to RGB (matplotlib and webcolors)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Optionally resize the image
    if resize:
        height, width = image.shape[:2]
        max_dim = max(height, width)
        if max_dim > resize_max:
            scale = resize_max / max_dim
            image = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
    
    # Reshape the image to be a list of pixels
    pixels = image.reshape((-1, 3))
    
    # Convert to float for KMeans
    pixels = np.float32(pixels)
    
    # Define criteria for KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    
    # Apply KMeans
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    
    # Get the cluster centers (dominant colors)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Get the number of pixels in each cluster
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    
    # Sort colors by frequency
    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]
    
    # Map colors to names
    color_info = []
    for color in colors:
        name = get_color_name(tuple(color))
        color_info.append((name, tuple(color)))
    
    return color_info

def plot_colors(color_info):
    """
    Plot the detected colors as a bar.

    :param color_info: List of tuples containing color names and their RGB values.
    """
    # Number of colors
    num_colors = len(color_info)
    
    # Create a figure
    plt.figure(figsize=(8, 2))
    
    # Create a bar with each color
    for i, (name, rgb) in enumerate(color_info):
        plt.bar(i, 1, color=np.array(rgb)/255, edgecolor='none')
    
    # Remove axes
    plt.axis('off')
    
    # Show color names below the bar
    plt.xticks(range(num_colors), [name for name, _ in color_info], rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Detect and list dominant colors in a JPG image.')
    parser.add_argument('image_path', type=str, help='Path to the JPG image.')
    parser.add_argument('--num_colors', type=int, default=5, help='Number of dominant colors to detect.')
    parser.add_argument('--resize', action='store_true', help='Resize image for faster processing.')
    parser.add_argument('--resize_max', type=int, default=800, help='Maximum size to resize the image.')
    
    args = parser.parse_args()
    
    try:
        # Extract colors
        color_info = extract_colors(
            image_path=args.image_path,
            num_colors=args.num_colors,
            resize=args.resize,
            resize_max=args.resize_max
        )
        
        # Print the colors
        print(f"Detected {args.num_colors} colors in '{args.image_path}':\n")
        for i, (name, rgb) in enumerate(color_info, 1):
            print(f"{i}. {name} - RGB{rgb}")
        
        # Plot the colors
        plot_colors(color_info)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

'''