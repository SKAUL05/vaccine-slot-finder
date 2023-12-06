import requests
import os
import json
import time
from twilio.rest import Client
from datetime import datetime, timedelta

STATE = "https://api.covid19india.org/data.json"
CASES = "https://www.mohfw.gov.in/data/datanew.json"

def prepare_case_json(data, case=""):
    msg = (
        "\n*India Daily Tally*\n*Date: "
        + datetime.now().strftime("%d-%m-%Y")
        + "*\n*----------------*\n"
    )
    if case == "State":
        msg = (
            "\n*J&K Daily Tally*\n*Date: "
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
            + "-------------\n\n"
        )
    msg += "Note: If you want to continue receiving messages please send following message.\n" + "*join friend-generally*"
    return msg


def send_whatsapp(pr_json, check):

    account_sid = os.environ.get("ACC_SID")
    auth_token = os.environ.get("TOKEN")
    client = Client(account_sid, auth_token)
    msg_body = prepare_case_json(pr_json, check)
    rec = os.environ.get("RECEIVER").strip('][').split(',')
    for num in rec:
        stri = f"whatsapp:{num}"
        message = client.messages.create(
            from_="whatsapp:" + os.environ.get("SENDER"), body=msg_body, to=stri
        )

        print(message.sid)


def find_total_cases(cases_json, st_json):
    req_json = requests.get(CASES)
    req_s_json = requests.get(CASES)
    daily_json = []
    state_json = []
    dt_state = datetime.now().strftime("%d/%m/%Y")

    if req_json.status_code == 200:
        case_json = req_json.json()
        if (
            int(case_json[-1]["new_active"]) - int(case_json[-1]["active"])
        ) not in cases_json:
            daily_json.append(
                {
                    "Confirmed Today": str(int(case_json[-1]["new_positive"])
                    - int(case_json[-1]["positive"])),
                    "Deaths Today": str(int(case_json[-1]["new_death"])
                    - int(case_json[-1]["death"])),
                    "Recovered Today": str(int(case_json[-1]["new_cured"])
                    - int(case_json[-1]["cured"])),
                    "Active": int(case_json[-1]["new_active"]),
                }
            )
        case_json = req_s_json.json()
        for a_state in case_json:
            if (
                a_state["state_code"] == "01"
            ):
                dt_state = str(int(a_state["new_positive"]))
                state_json.append(
                    {
                        "Confirmed Today": str(int(a_state["new_positive"]) - int(a_state["positive"])),
                        "Deaths Today": str(int(a_state["new_death"]) - int(a_state["death"])),
                        "Recovered Today": str(int(a_state["new_cured"]) - int(a_state["cured"])),
                        "Active": int(a_state["new_active"])
                    }
                )
    if daily_json and daily_json[0]["Active"] not in cases_json:
        print("Cases Found")
        send_whatsapp(daily_json, "Cases")
        cases_json.append(daily_json[0]["Active"])
    if state_json and dt_state not in st_json:
        print("State Found")
        send_whatsapp(state_json, "State")
        st_json.append(dt_state)

    return cases_json, st_json



if __name__ == "__main__":
    with open("database.json", "r") as openfile:
        json_object = json.load(openfile)
    print("JSON OBJECT FETCHED-----", json_object)
    ret_cs_json, ret_st_json = find_total_cases(
        json_object["INDIA"], json_object["JK"]
    )
    with open("database.json", "w") as outfile:
        send_json = {
            "INDIA": ret_cs_json,
            "JK": ret_st_json
        }
        json.dump(send_json, outfile)
