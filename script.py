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


def prepare_table_html(data):
    table_style = """<html>
	<head>
		<style>
			table {
				font-family: arial, sans-serif;
				border-collapse: collapse;
				width: 100%;
			}
			td,tr {
				border: 1px solid black;
				text-align: left;
				padding: 8px;
			}			
		</style>
	</head>"""
    table_html = """<table> <tr>
                    <td>Name</td>
                    <td>PinCode</td>
                    <td>Capacity</td>
                    <td>Dates</td></tr>
                 """
    for a_row in data:
        table_html += (
            """<tr><td>"""
            + a_row["Name"]
            + """</td><td>"""
            + a_row["PinCode"]
            + """</td><td>"""
            + ",".join(a_row["Capacity"])
            + """</td><td>"""
            + ",".join(a_row["Date"])
            + """</td></tr>"""
        )
    table_html +=  """</table></html>"""
    return table_style + table_html


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
                    app_json["PinCode"] = str(acent["pincode"])
                    app_json["Capacity"].append(str(sess["available_capacity"]))
                    app_json["Date"].append(sess["date"])

            if app_json["Name"]:
                pr_json.append(app_json)
        except Exception as e:
            print(e)
print(pr_json)


if pr_json:
    pr_json = prepare_table_html(pr_json)
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": "kaul.sarath@gmail.com",
                        },
                        {"email": "antra.kaul@gmail.com"},
                    ]
                }
            ],
            "from": {"email": "kaul.sarath@gmail.com", "name": "Vaccine Bot"},
            "subject": "Vaccine Slot Available",
            "content": [{"type": "text/html", "value": pr_json}],
        }
        response = sg.client.mail.send.post(request_body=data)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
