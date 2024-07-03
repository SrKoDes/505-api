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
#   * Commit changes to Ko's repo (https://github.com/SrKoDes/505-api)
# https://www.moesif.com/blog/technical/api-development/Building-RESTful-API-with-Flask/
# https://www.w3schools.com/python/python_classes.asp

dateFormat = "%Y%m%d"
jsonFileName = "expiry.json"

def to_date(date_string):
    try:
        return datetime.strptime(date_string, dateFormat).date()
    except ValueError:
        raise ValueError('{} is not a valid date in the format YYYYMMDD'.format(date_string))

@app.route('/food/', methods=["GET", "POST", "DELETE"])
def manage_food():
    with open(jsonFileName, "r") as file:
        data = json.load(file)

    if request.method == "GET":
        return sorted(data.items(), key=lambda item: item[1]['expiry'])
#----------------------------------------------------------------------------------#
    requestData = request.json
    food = requestData['food']
    count = requestData['count']
    expiry = to_date(requestData['expiry']).strftime(dateFormat)
    timestamp = datetime.now().date().strftime(dateFormat)

    if request.method == "POST":
        # If dictionary contains "food" with the same expiration date, count += 1
        # If dictionary contains "food" with different expiration date, "food" = "food - date"

        if food in data.keys():
            savedFood = data[food]
            if savedFood['expiry'] == expiry:
                count += savedFood['count']
            else:
                food += "-" + expiry

        element = {
            food: {
                "expiry": expiry,
                "count": count,
                "timestamp": timestamp
            }
        }

        data.update(element)
        with open(jsonFileName, "w") as file:
            json.dump(data, file)

        return "Added {} of {} that expires {}".format(count, food, expiry)
#----------------------------------------------------------------------------------#
    elif request.method == "DELETE":
        if food not in data.keys():
            return "{} does not exist".format(food)

        savedFood = data.get(food)
        updatedCount = savedFood['count'] - count

        if updatedCount < 1:
            del data[food]
            message = "Deleted {}".format(food)
        else:
            data[food]['count'] = updatedCount
            message = "{} of {} remaining".format(updatedCount, food)

        with open(jsonFileName, "w") as file:
            json.dump(data, file)

        return message
