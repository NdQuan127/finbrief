import os

# Configure upload settings
# UPLOAD_FOLDER = tempfile.gettempdir() # This might be needed if utils access it directly, or passed as arg
ALLOWED_EXTENSIONS = {'pdf'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # App specific config
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload # App specific config

def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_float(value: any) -> float | None:
    """
    Safely convert a value to float, handling various formats.

    Args:
        value (any): The value to convert. It can be a number, string, or None.
                     String values can include '$' and ',', and negative numbers
                     can be represented with '()'. Also handles 'M' (million) and
                     'B' (billion) suffixes common in financial reports.

    Returns:
        float | None: The converted float value, or None if conversion fails.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Handle common suffixes in financial reports
        original_value = str(value).strip()
        multiplier = 1.0
        
        # Check for million/billion suffixes
        if original_value.upper().endswith('M'):
            multiplier = 1000000.0
            value = original_value[:-1]
        elif original_value.upper().endswith('B'):
            multiplier = 1000000000.0
            value = original_value[:-1]
        
        # Remove currency symbols and commas
        clean_value = str(value).replace("$", "").replace(",", "").strip()
        
        # Handle parentheses notation for negative numbers
        if clean_value.startswith("(") and clean_value.endswith(")"):
            return -float(clean_value[1:-1]) * multiplier
        
        return float(clean_value) * multiplier
    except (ValueError, TypeError):
        return None
