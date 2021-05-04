import requests

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=230&date="

from datetime import datetime, timedelta

st_date = datetime.now() + timedelta(days=-(datetime.today().weekday() - 0))
st_date_str = datetime.now().strftime("%d-%m-%Y")
en_date = st_date + timedelta(days=+7)
en_date_str = en_date.strftime("%d-%m-%Y")

dates = [st_date_str, en_date_str]
pr_json = []

for d in dates:
    URL_HIT = URL + d
    x = requests.get(URL_HIT)
    jret = x.json()["centers"]

    for acent in jret:
        app_json = {"Name": "", "PinCode": "", "Capacity": [], "Date": []}
        for sess in acent["sessions"]:
            if sess["available_capacity"] > 0 and sess["min_age_limit"] == 18:
                # print(sess)
                app_json["Name"] = acent["name"]
                app_json["PinCode"] = acent["pincode"]
                app_json["Capacity"].append(sess["available_capacity"])
                app_json["Date"].append(sess["date"])

        if app_json["Name"]:
            pr_json.append(app_json)

print(pr_json)
