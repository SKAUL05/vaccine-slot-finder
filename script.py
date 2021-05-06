import requests
import os
import json
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta


URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=230&date="

st_date = datetime.now() + timedelta(days=-(datetime.today().weekday() - 0))
st_date_str = datetime.now().strftime("%d-%m-%Y")
en_date = st_date + timedelta(days=+7)
en_date_str = en_date.strftime("%d-%m-%Y")

dates = [st_date_str, en_date_str]
res_json = []
request_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 "
    "Firefox/88.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5 --compressed",
    "Origin": "https://selfregistration.cowin.gov.in",
    "Connection": "keep-alive",
    "Referer": "https://selfregistration.cowin.gov.in/",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "Trailers",
}
proxy_list = ["http://15.206.86.160:8080","http://136.232.243.142:3128","http://59.94.176.111:3128"]
proxies = {"https": proxy_list[random.randint(0, 2)]}


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
    table_html += """</table></html>"""
    return table_style + table_html


for date in dates:
    URL_HIT = URL + date
    response = requests.get(URL_HIT, headers=request_header, proxies=proxies)
    if response.status_code != 200:
        print(response.status_code)
        continue
    jret = list(response.json().values())[0]

    for acent in jret:
        app_json = {"Name": "", "PinCode": "", "Capacity": [], "Date": []}
        try:
            for sess in acent["sessions"]:
                if sess["available_capacity"] > 0 and sess["min_age_limit"] == 18:
                    # print(sess)
                    app_json["Name"] = acent["name"]
                    app_json["PinCode"] = str(acent["pincode"])
                    app_json["Capacity"].append(str(sess["available_capacity"]))
                    app_json["Date"].append(sess["date"])

            if app_json["Name"]:
                res_json.append(app_json)
        except Exception as e:
            print(e)
print(res_json)


if res_json:
    res_json = prepare_table_html(res_json)
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        data = {
            "personalizations": [
                {
                    "to": [
                        {"email": "kaul.sarath@gmail.com"},
                        {"email": "antra.kaul@gmail.com"},
                    ]
                }
            ],
            "from": {"email": "kaul.sarath@gmail.com", "name": "Vaccine Bot"},
            "subject": "Vaccine Slot Available",
            "content": [{"type": "text/html", "value": res_json}],
        }
        response = sg.client.mail.send.post(request_body=data)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
