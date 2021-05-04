import requests
import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta


URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=230&date="

st_date = datetime.now() + timedelta(days=-(datetime.today().weekday() - 0))
st_date_str = datetime.now().strftime("%d-%m-%Y")
en_date = st_date + timedelta(days=+7)
en_date_str = en_date.strftime("%d-%m-%Y")

dates = [st_date_str, en_date_str]
pr_json = []

for d in dates:
    URL_HIT = URL + d
    x = requests.get(URL_HIT)
    jret = list(x.json().values())[0]

    for acent in jret:
        app_json = {"Name": "", "PinCode": "", "Capacity": [], "Date": []}
        try:
            for sess in acent["sessions"]:
                if sess["available_capacity"] > 0 and sess["min_age_limit"] == 45:
                    # print(sess)
                    app_json["Name"] = acent["name"]
                    app_json["PinCode"] = acent["pincode"]
                    app_json["Capacity"].append(sess["available_capacity"])
                    app_json["Date"].append(sess["date"])

            if app_json["Name"]:
                pr_json.append(app_json)
        except Exception as e:
            print(e)
print(pr_json)

if pr_json:
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": "kaul.sarath@gmail.com",
                        }
                    ]
                }
            ],
            "from": {"email": "kaul.sarath@gmail.com", "name": "Vaccine Bot"},
            "subject": "Vaccine Slot Available",
            "content": [{"type": "text/html", "value": json.dumps(pr_json)}],
        }
        response = sg.client.mail.send.post(request_body=data)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
