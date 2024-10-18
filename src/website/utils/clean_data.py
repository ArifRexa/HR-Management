import re
import unicodedata

def remove_emojis(text):
    """Remove emojis and other non-alphanumeric characters."""
    # Normalize text to separate out combined emojis/icons
    text = unicodedata.normalize('NFKD', text)

    # Use regex to remove emojis and non-alphanumeric characters
    return re.sub(r'[^\w\s,.!?]', '', text)  # Allowing basic punctuation