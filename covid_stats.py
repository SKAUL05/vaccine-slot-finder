import requests
import os
import json
import time
from twilio.rest import Client
from datetime import datetime, timedelta

CASES = "https://api.covid19india.org/data.json"


def prepare_case_json(data, case=""):
    msg = (
        "*India Daily Tally*\n*Date: "
        + datetime.now().strftime("%d-%m-%Y")
        + "*\n*----------------*\n"
    )
    if case == "State":
        msg = (
            "*J&K Daily Tally*\n*Date: "
            + datetime.now().strftime("%d-%m-%Y")
            + "*\n*----------------*\n"
        )
    for row in data:
        msg += (
            "Confirmed Today:- "
            + row["Confirmed Today"]
            + "\n"
            + "Deaths Today:- "
            + row["Deaths Today"]
            + "\n"
            + "Recovered Today:- "
            + row["Recovered Today"]
            + "\n"
            + "-------------\n"
        )
    return msg


def send_whatsapp(pr_json, check):

    account_sid = os.environ.get("ACC_SID")
    auth_token = os.environ.get("TOKEN")
    client = Client(account_sid, auth_token)
    msg_body = prepare_case_json(pr_json, check)
    print(os.environ.get("RECEIVER"))
    print(type(os.environ.get("RECEIVER")))
    return
    for num in os.environ.get("RECEIVER"):
        stri = "whatsapp:" + num
        message = client.messages.create(
            from_="whatsapp:" + os.environ.get("SENDER"), body=msg_body, to=stri
        )

        print(message.sid)


def find_total_cases(cases_json, st_json):
    req_json = requests.get(CASES)
    daily_json = []
    state_json = []
    dt_india = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d")
    dt_state = datetime.now().strftime("%d/%m/%Y")

    if req_json.status_code == 200:
        case_json = req_json.json()
        if case_json["cases_time_series"][-1]["dateymd"] == dt_india:
            daily_json.append(
                {
                    "Confirmed Today": case_json["cases_time_series"][-1][
                        "dailyconfirmed"
                    ],
                    "Deaths Today": case_json["cases_time_series"][-1]["dailydeceased"],
                    "Recovered Today": case_json["cases_time_series"][-1][
                        "dailyrecovered"
                    ],
                }
            )
        st = case_json["statewise"]
        for a_state in st:
            if (
                a_state["statecode"] == "JK"
                and a_state["lastupdatedtime"].split(" ")[0] == dt_state
            ):
                state_json.append(
                    {
                        "Confirmed Today": a_state["deltaconfirmed"],
                        "Deaths Today": a_state["deltadeaths"],
                        "Recovered Today": a_state["deltarecovered"],
                    }
                )
    if daily_json and dt_india not in cases_json:
        print("Cases Found")
        send_whatsapp(daily_json, "Cases")
        cases_json.append(dt_india)
    if state_json and dt_state not in st_json:
        print("State Found")
        send_whatsapp(state_json, "State")
        st_json.append(dt_state)

    return cases_json, st_json



if __name__ == "__main__":
    with open("database.json", "r") as openfile:
        json_object = json.load(openfile)
    ret_cs_json, ret_st_json = find_total_cases(
        json_object["INDIA"], json_object["JK"]
    )
    with open("database.json", "w") as outfile:
        send_json = {
            "INDIA": ret_cs_json,
            "JK": ret_st_json
        }
        json.dump(send_json, outfile)
