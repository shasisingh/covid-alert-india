import email
import os
import smtplib
import time
from datetime import datetime

import pytz
import requests


def create_session_info(center, session):
    return {"name": center["name"],
            "date": session["date"],
            "capacity": session["available_capacity"],
            "age_limit": session["min_age_limit"]}


def get_sessions(data):
    for center in data["centers"]:
        for session in center["sessions"]:
            yield create_session_info(center, session)


def is_available(session):
    return session["capacity"] > 0


def is_eighteen_plus(session):
    return session["age_limit"] == 18


def get_for_seven_days(start_date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    # params = {"district_id": 571, "date": start_date.strftime("%d-%m-%Y")}
    # params = {"district_id": 265, "date": start_date.strftime("%d-%m-%Y")} #banglor -urban
    # params = {"district_id": 276, "date": start_date.strftime("%d-%m-%Y")}  # banglore rural
    params = {"district_id": 193, "date": start_date.strftime("%d-%m-%Y")} #ambala
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    return [session for session in get_sessions(data) if is_eighteen_plus(session) and is_available(session)]


def get_by_pin_code(pin_code, start_date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
    params = {"pincode": pin_code, "date": start_date.strftime("%d-%m-%Y")}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    return [session for session in get_sessions(data) if is_eighteen_plus(session) and is_available(session)]


def create_output(session_info):
    return f"{session_info['date']} - {session_info['name']} ({session_info['capacity']})"


# The notifier function
def notify(title, subtitle, message):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier -sound default {}'.format(' '.join([m, t, s])))


def processor(date_search):
    print(get_for_seven_days(datetime.today()))
    # content = "\n".join([create_output(session_info) for session_info in get_by_pin_code(133001, dateSearch)])
    content = "\n".join([create_output(session_info) for session_info in get_for_seven_days(date_search)])

    username = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')

    if not content:
        print("->>>> No availability")
    else:
        # Calling the function
        notify(title='Vaccination Slot Open',
               subtitle='COVID-19:Notifications',
               message='Check your email for more information or log line')
        email_msg = email.message.EmailMessage()
        email_msg["Subject"] = "Vaccination Slot Open"
        email_msg["From"] = username
        email_msg["To"] = username
        email_msg.set_content(content)

        with smtplib.SMTP(host='smtp.gmail.com', port='587') as server:
            server.starttls()
            server.login(username, password)
            # server.send_message(email_msg, username, username)


if __name__ == '__main__':
    while 1:
        tz_India = pytz.timezone('Asia/Kolkata')
        datetime_India = datetime.now(tz_India)
        processor(datetime_India)
        dt_string = datetime_India.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)
        # print(pytz.all_timezones)
        # if datetime_India.hour == '0' \
        #         or datetime_India.hour == '1' \
        #         or datetime_India.hour == '2' \
        #         or datetime_India.hour == '3' \
        #         or datetime_India.hour == '4' \
        #         or datetime_India.hour == '5' \
        #         or datetime_India.hour == '6' \
        #         or datetime_India.hour == '7' \
        #         or datetime_India.hour == '8' \
        #         or datetime_India.hour == '9' \
        #         or datetime_India.hour == '10' \
        #         or datetime_India.hour == '11':
        processor(datetime_India)
        time.sleep(4)
        # else:
        #     exit()
