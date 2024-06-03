import os
import time
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

json_file = 'PATH TO expiry.json (should probably change to a db)'


def add_food(food, date, count=1):
    if not os.path.exists("path that is value):
        raise FileNotFoundError(f"Can't find the json file, {json_file}!")
    
    # Make sure date has the right # of digits(8)
    if len(date) != 8:
        raise ValueError("Date must have 8 digits, 4 for year, 2 for month and 2 for date!")
    # Change date from 20210101-> 2021-01-01
    date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(json_file, 'r') as file:
        data = json.load(file)

    # If the same food type with the same expiration date exists, increase the count of that item
    if food in data.keys():
        if data[food]['date'] == date:
            count += data[food]['count']
        
        # If the dates don't match, create a new entry for it, but add a suffix
        else:
            food += "-" + date
    
    new_entry = {
        food: {
            "date": date,
            "count": count,
            "timestamp": timestamp
        }
    }

    # Append the new entry to the data
    data[food] = new_entry[food]
    # Write the updated data back to the CSV file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

    return new_entry


def list_all():
    with open(json_file, 'r') as file:
        data = json.load(file)

    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['date']))
    return sorted_data


def remove_food(food, date, count=1):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Make sure targeted food exists
    target = data.get(food)
    if not target:
        for entry in data.keys():
            if data[entry]['date'] == f"{date[:4]}-{date[4:6]}-{date[6:]}":
                return f"No food by name: {food} found. Did you mean to delete this food: {entry}?"
        raise ValueError(f"No food by name {food} recorded!")

    # Handle the count difference
    # Remove the entry if final count is < 1. Else reduce the count and update record
    new_count = target['count'] - count
    if new_count < 1:
        del data[food]
        message = f"Deleted food: {food.title()}"
    else:
        data[food]['count'] = new_count
        message = ["New count", data[food]]

    with open(json_file, 'w') as file:
        data = json.dump(data, file, indent=4)

    return message


def send_report():
    data = list_all()
    current_date = int(datetime.now().strftime("%Y%m%d"))
    expired = {}
    will_expire_in_a_week = {}
    will_expire_in_a_month = {}
    
    for key, value in data.items():
        date = int(value['date'].replace("-", ""))
    
        # if date - current_date = 
        if date - current_date < 0:
            expired[key] = value
            
        elif date - current_date <= 7:
            will_expire_in_a_week[key] = value
        
        elif date - current_date <= 30:
            will_expire_in_a_month[key] = value

    # Email credentials
    sender_email = string
    receiver_emails = [list of strings]
    password = string

    for receiver in receiver_emails:
        # Create a multipart message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver
        message["Subject"] = "Status of Edible Goods"

        # Add body to email
        # expired
        body = "The following is expired:\n\n"
        if not expired:
            body += "-------------"
        for key, value in expired.items():
            body += f"{key}: {value['date']} x {value['count']}\n"
        
        body += "\nThe following will expire in a week:\n\n"
        if not will_expire_in_a_week:
            body += "-------------"
        # expires in a week
        for key, value in will_expire_in_a_week.items():
            body += f"{key}: {value['date']} x {value['count']}\n"

        # expires in a month
        body += "\n The following will expire in a month:\n\n"
        if not will_expire_in_a_month:
            body += "-------------"
        for key, value in will_expire_in_a_month.items():
            body += f"{key}: {value['date']} x {value['count']}"


        message.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server (for Gmail, use port 587)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver, message.as_string())

