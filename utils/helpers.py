from datetime import datetime
import re
import logging
import phonenumbers
def standardize_cname(name):
    # Capitalize the first letter of each word
    name = name.title()
    # Remove punctuation except hyphens
    name = re.sub(r'[^\w\s-]', '', name)
    # Remove extra spaces
    name = name.strip()
    return name



def format_phone_number(number, country="CA"):  # Default to Canada
    parsed = phonenumbers.parse(number, country)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
