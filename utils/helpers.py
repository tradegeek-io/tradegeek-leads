from datetime import datetime
import re
import logging

def standardize_cname(name):
    # Capitalize the first letter of each word
    name = name.title()
    # Remove punctuation except hyphens
    name = re.sub(r'[^\w\s-]', '', name)
    # Remove extra spaces
    name = name.strip()
    return name
