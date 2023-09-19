from datetime import datetime, timedelta
import re

def parse_slurm_duration(input_str):
    """
    Parse a slurm-formatted duration '[DD-[HH:]]MM:SS' into a timedelta object 
    """
    # Define regular expressions for the optional components
    day_pattern = r'(\d+)-'  # Matches "DD-" and captures DD as a group
    hour_pattern = r'(\d+):'  # Matches "HH:" and captures HH as a group

    # Combine the optional patterns with the main pattern
    main_pattern = r'(\d+):(\d+):(\d+)'

    # Try to match the entire pattern
    match = re.match(fr'^{day_pattern}?{hour_pattern}?{main_pattern}$', input_str)

    if not match:
        raise ValueError("Invalid datetime format")
    
    # Extract the captured groups
    day = int(match.group(1)) if match.group(1) else 1
    hour = int(match.group(2)) if match.group(2) else 0
    minute = int(match.group(3))
    second = int(match.group(4))

    # Create a timedelta object with the extracted values
    delta = timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    return delta

def calculate_timedelta_offset_from_now(offset: timedelta):   
    current_datetime = datetime.now()

    result_datetime = current_datetime - offset

    return result_datetime