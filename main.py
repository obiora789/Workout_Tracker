from datetime import datetime
import dotenv
import requests
import os

k_cal_to_kg = 0.00013
kilo_calories = 0
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

GENDER = os.environ.get("GENDER")
weight_kg = os.getenv("WEIGHT_KG")
print(weight_kg)
HEIGHT_CM = os.getenv("HEIGHT_CM")
AGE = os.environ.get("AGE")
NUTRITIONIX_ENDPOINT = os.environ.get("NUTRITIONIX_ENDPOINT")
SHEETY_ENDPOINT = os.getenv("SHEETY_ENDPOINT")
NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID")
NUTRITIONIX_APP_KEY = os.environ.get("NUTRITIONIX_APP_KEY")
SHEETY_AUTH = "Bearer "+os.environ.get("SHEETY_AUTH")
BASIC_AUTH = "Basic "+os.environ.get("BASIC_AUTH")
workout_upload = {}

header = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_APP_KEY,
    "x-remote-user-id": "0",
}

headers = {"Authorization": SHEETY_AUTH}
exercise_parameters = {
    "query": input("How much did you exercise today?\n"),
    "gender": GENDER,
    "weight_kg": weight_kg,
    "height_cm": HEIGHT_CM,
    "age": AGE
}

workout_response = requests.post(url=NUTRITIONIX_ENDPOINT, json=exercise_parameters, headers=header)
workout_response.raise_for_status()
exercises = workout_response.json()["exercises"]
current_datetime = datetime.now()
current_date = current_datetime.strftime("%d/%m/%Y")
current_time = current_datetime.strftime("%H:%M:%S")

sheety_response = requests.get(url=SHEETY_ENDPOINT, headers=headers)
sheety_response.raise_for_status()
workouts = sheety_response.json()
row_id = len(workouts["workouts"]) + 2

nice = [{"date": current_date, "time": current_time, "exercise": exercise["name"].title(),
         "duration": exercise["duration_min"], "calories": exercise["nf_calories"], "id": row_id,
         } for exercise in exercises]

for niceness in nice:
    kilo_calories += niceness["calories"]
    workout_upload["workout"] = niceness
    sheety_post = requests.post(url=SHEETY_ENDPOINT, json=workout_upload, headers=headers)
    sheety_post.raise_for_status()
    print(sheety_post.json())

# Now to update the value of kg burned because I don't weigh the same anymore.
kg_burned = kilo_calories * k_cal_to_kg
remaining_weight = float(weight_kg) - kg_burned
os.environ["WEIGHT_KG"] = str(remaining_weight)
dotenv.set_key(dotenv_file, "WEIGHT_KG", os.environ["WEIGHT_KG"])
