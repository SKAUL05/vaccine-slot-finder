import requests
import os
import json
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta


URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=230&date="

st_date = datetime.now() + timedelta(days=-(datetime.now().weekday() - 0))
st_date_str = datetime.now().strftime("%d-%m-%Y")
en_date = st_date + timedelta(days=+7)
en_date_str = en_date.strftime("%d-%m-%Y")

dates = [st_date_str, en_date_str]
res_json = []
request_header = {
    "authority": "scrapeme.live",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}
proxy_list = os.environ.get("PROXY").strip("][").split(",")
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

def prepare_whatsapp_message(data):
    msg = "*Alert!*\n*Vaccine Slots Available...*\n*----------------*\n\n"
    for row in data:
        msg += (
            "Name:- "
            + row["Name"]
            + "\n"
            + "PinCode:- "
            + row["PinCode"]
            + "\n"
            + "Capacity:- "
            + ",".join(row["Capacity"])
            + "\n"
            + "Dates:- "
            + ",".join(row["Date"])
            + "\n"
            + "-------------\n"
        )
    return msg

def send_whatsapp(pr_json):

    account_sid = os.environ.get("ACC_SID")
    auth_token = os.environ.get("TOKEN")
    client = Client(account_sid, auth_token)
    msg_body = prepare_whatsapp_message(pr_json)
    rec = os.environ.get("RECEIVER").strip('][').split(',')
    for num in rec:
        stri = f"whatsapp:{num}"
        message = client.messages.create(
            from_="whatsapp:" + os.environ.get("SENDER"), body=msg_body, to=stri
        )

        print(message.sid)

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
    print(res_json)
    send_whatsapp(res_json)
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
            "content": [{"type": "text/html", "value": pr_json}],
        }
        response = sg.client.mail.send.post(request_body=data)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
