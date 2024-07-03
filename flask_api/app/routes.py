from app import app
from flask import request
from datetime import datetime
import json

# Enhancements
#   * JSON loading logic is finnicky, at the least it expects an empty dictionary or it'll crash
#   * Code reuse
#   * Deletion, port over logic to recommend different food to delete
#   * Email report
#   * Food class object to wrap name, count, expiry, timestamp
# https://www.moesif.com/blog/technical/api-development/Building-RESTful-API-with-Flask/
# https://www.w3schools.com/python/python_classes.asp

date_format = "%Y%m%d"
json_filename = "expiry.json"

def to_date(date_string):
    try:
        return datetime.strptime(date_string, date_format).date()
    except ValueError:
        raise ValueError('{} is not a valid date in the format YYYYMMDD'.format(date_string))

def get_expiry(element):
    return element['expiry']

@app.route('/food/', methods=["GET", "POST", "DELETE"])
def manage_food():
    with open(json_filename, "r") as file:
        data = json.load(file)

    if request.method == "GET":
        data.sort(key=get_expiry)
        return data
#----------------------------------------------------------------------------------#
    request_data = request.json
    food = request_data['food']
    count = request_data['count']
    expiry = to_date(request_data['expiry']).strftime(date_format)
    timestamp = datetime.now().date().strftime(date_format)

    if request.method == "POST":
        # If the array contains "food" with the same expiration date: count += newCount
        # If the array contains "food" with a different expiration date: "{food} - {expiry}"

        for item in data:
            if item['food'] == food: # Food already exists.
                if item['expiry'] == expiry: # Food has the same expiry
                    item['count'] += count # Update the count of the existing item

                    # Do not append a new element, override existing data
                    with open(json_filename, "w") as file:
                        json.dump(data, file)

                    return "Updated {} with new count: {}".format(food, item['count'])
                else: #Implies that the food has a different expiry
                    food += "-" + expiry

        element = {
            "food": food,
            "expiry": expiry,
            "count": count,
            "timestamp": timestamp
        }

        data.append(element)
        with open(json_filename, "w") as file:
            json.dump(data, file)

        return "Added {} of {} that expires {}".format(count, food, expiry)
#----------------------------------------------------------------------------------#
    elif request.method == "DELETE":
        if food not in [item['food'] for item in data]:
            return "{} does not exist".format(food)

        for item in data:
            if item['food'] == food: # Food already exists
                new_count = item['count'] - count

                if new_count < 1:
                    data.remove(item)
                    message = "Deleted {}".format(food)
                else:
                    item['count'] = new_count
                    message = "{} of {} remaining".format(new_count, food)

        with open(json_filename, "w") as file:
            json.dump(data, file)

        return message
