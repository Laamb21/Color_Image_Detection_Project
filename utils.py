# utils.py

import os

def extract_last_four_digits(filename):
    """
    Extract the last four numerical digits before the file extension.
    
    Parameters:
        filename (str): The filename to extract digits from.
    
    Returns:
        str or None: The last four digits as a string, or None if extraction fails.
    """
    base, _ = os.path.splitext(filename)
    digits = ''.join(filter(str.isdigit, base))
    if len(digits) < 4:
        return None
    return digits[-4:]

def extract_first_digit(filename):
    """
    Extract the first numerical digit of the filename before the extension.
    
    Parameters:
        filename (str): The filename to extract the first digit from.
    
    Returns:
        str or None: The first digit as a string, or None if extraction fails.
    """
    base, _ = os.path.splitext(filename)
    for char in base:
        if char.isdigit():
            return char
    return None

def is_valid_jpg(filename):
    """
    Check if the filename is a valid JPG based on the second character being '1'.
    
    Parameters:
        filename (str): The JPG filename to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    base, _ = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '1'

def is_valid_tiff(filename):
    """
    Check if the filename is a valid TIFF based on the second character being '0'.
    
    Parameters:
        filename (str): The TIFF filename to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    base, _ = os.path.splitext(filename)
    if len(base) < 2 or not base[1].isdigit():
        return False
    return base[1] == '0'
