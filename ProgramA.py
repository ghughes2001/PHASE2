# Author: Grant Hughes
# Program A for phase2
# Uses regualr expression import to search for files matching required format in directory
# Uses system (os) import to find/access files in directory
# Uses datetime import to help keep track of valid user time in log

import os
import re
from datetime import datetime

def print_description():
    print("This program checks time log files, "
          "where X is any alphabetic string. It validates the content according "
          "to specified criteria and generates a report of valid and invalid files.")
    input("Press Enter to continue...")

def find_log_files():
    log_files = []
    pattern = re.compile(r'^[A-Za-z]+Log\.csv$', re.IGNORECASE)
    
    for filename in os.listdir():
        if pattern.match(filename):
            log_files.append(filename)
    
    return log_files

def validate_file(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    if not lines:
        return (False, "File is empty", 1)
    
    # Check the first line for LastName, FirstName
    header = lines[0].split(',')
    last_name, first_name = header[0], header[1]
    if last_name == "" or first_name == "":
        return False, "Invalid format for last and first name", 1

    # Check the second line for course code
    if lines[1].split(",")[0] != "CS 4500":
        return False, "Missing course code 'CS 4500'", 2

    # Validate time entries
    for line_num, line in enumerate(lines[2:], start=3):
        entry = line.split(',')
        if len(entry) < 5 or len(entry) > 6:
            return (False, "Invalid entry format", line_num)

        # Validate date
        date_str = entry[0]
        try:
            entry_date = datetime.strptime(date_str, '%m/%d/%Y')
            if entry_date > datetime.now():
                return (False, "Date must be today or earlier", line_num)
        except ValueError:
            return (False, "Invalid date format", line_num)

        # Validate times
        start_time = entry[1]
        end_time = entry[2]
        if not re.match(r'^\d{2}:\d{2}$', start_time) or not re.match(r'^\d{2}:\d{2}$', end_time):
            return (False, "Times must be in HH:MM format", line_num)
        
        if start_time >= end_time:
            return (False, "End time must be after start time", line_num)

        # Validate duration
        duration = (datetime.strptime(end_time, '%H:%M') - datetime.strptime(start_time, '%H:%M')).seconds // 60
        if duration >= 240:  # 4 hours
            print(f"Warning: {filename} has a long time entry at line {line_num}")
        
        # Validate number of people involved
        people = entry[3]
        if int(people) < 1:
            return (False, "Number of people must be greater than 0", line_num)
        if int(people) > 50:
            return (False, "Number of people must be 50 or less", line_num)
        
        # Validate activity code
        activity_code = entry[4]
        if activity_code not in [str(i) for i in range(10)] + ["A", "B", "C", "D"]:
            return (False, "Invalid activity code", line_num)

        # Validate note if necessary
        if activity_code == "D" and len(entry) != 6:
            return (False, "A note is required for activity code 'D'", line_num)
        if len(entry) == 6:
            note = entry[5]
            if ',' in note or len(note) > 80:
                return (False, "Note cannot contain commas and must be 80 characters or less", line_num)

    return (True, "File is valid", None)

def main():
    print_description()
    log_files = find_log_files()

    if not log_files:
        print("No valid log files found. Exiting.")
        return

    with open("ValidityChecks.txt", "w") as report_file:
        for filename in log_files:
            is_valid, message, line_number = validate_file(filename)
            report_line = f"{filename}: {'Valid' if is_valid else 'Invalid'}"
            if not is_valid:
                report_line += f" (Line {line_number}: {message})"
            print(report_line)
            report_file.write(report_line + "\n")

    print("All files have been checked. Goodbye!")

if __name__ == "__main__":
    main()
