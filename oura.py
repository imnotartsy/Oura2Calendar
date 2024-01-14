import requests
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# Get Secrets
with open("secrets.json") as f:
    secrets = json.load(f)
access_token = secrets["oura_access_token"]


# * Control Vars
getINFO = False
plotPhases = False

DEBUG = False


# * Headers + Base URL
headers = {
    "Authorization": f"Bearer {access_token}"
}

base = "api.ouraring.com/"
personal_info_url = "v2/usercollection/personal_info"
sleep_url = "v2/usercollection/sleep"



# * General Personal Info
if getINFO:
    response = requests.get(f"https://{base}{personal_info_url}", headers=headers)
    print(json.dumps(response.json(), indent=2))


# * Sleep
# Get all sleep blocks since day
def getSleep(day):
    response = requests.get(f"https://{base}{sleep_url}?start_date={day}", headers=headers)
    if response.status_code != 200 or response.json()["data"] == []:
        print("No data for today")
        exit(0)
    return response.json()

# Takes in a sleep block and plots the sleep phases
def plotPhases(eep):
    print("Plotting sleep phases...")

    day = eep["day"]
    bedtime_start = datetime.fromisoformat(eep["bedtime_start"][:-6])
    total_sleep_duration = eep["total_sleep_duration"] / 60  # convert to hours
    sleep_phase_5_min = eep["sleep_phase_5_min"]

    # Prepare data for plotting
    timestamps = [bedtime_start + timedelta(minutes=i) for i in range(0, len(sleep_phase_5_min))]
    sleep_states = [int(state) for state in sleep_phase_5_min]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(timestamps, sleep_states, label="Sleep State")

    # Format x-axis as date and y-axis as 24-hour clock
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_yticklabels(["", "Deep Sleep", "Light Sleep", "REM Sleep", "Awake"])

    # Set labels and title
    plt.xlabel("Time")
    plt.ylabel("Sleep State")
    plt.title(f"Sleep Pattern for {day}")
    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45)
    # Show the plot
    plt.show()


def getSleepEvents(range_start):
    events = []
    data = getSleep(range_start)
    # print(json.dumps(data, indent=2))

    # Print each sleep block data
    for eep in data["data"]:
        day = eep["day"]

        timezone_offset = eep["bedtime_start"][-6:]
        timezone = f'GMT{timezone_offset}'

        # Convert to datetime object
        bedtime_start_datetime = datetime.fromisoformat(eep["bedtime_start"][:-6])

        # Calculate end datetime
        total_sleep_duration = eep["total_sleep_duration"]/60
        end_datetime = bedtime_start_datetime + timedelta(hours=total_sleep_duration/60)

        # Format datetimes
        start_datetime_formatted = bedtime_start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        end_datetime_formatted = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        if DEBUG:
            print("Sleep Block:", day)
            print("\tTimezone:", timezone)
            print("\tStart Datetime:", start_datetime_formatted)
            print("\tEnd Datetime:", end_datetime_formatted)
            print("\tTotal Sleep Duration:", total_sleep_duration, "minutes; or", int(total_sleep_duration/60), "hours and", int(total_sleep_duration%60), "minutes")

        event = {
            "end": {
                "dateTime": end_datetime_formatted,
                "timeZone": timezone,
            },
            "start": {
                "dateTime": start_datetime_formatted,
                "timeZone": timezone,
            },
            "creator": {
                "displayName": "sleep2calendar"
            },
            "summary": f"sleep block {int(total_sleep_duration/60)}:{int(total_sleep_duration%60)}",
        }

        events.append(event)
    
    return events


if DEBUG:
    # today = datetime.today().strftime("%Y-%m-%d")
    # get sleep from range_start to today
    range_start = "2024-1-13"
    print("Getting sleep data... for", range_start)

    events = getSleepEvents(range_start)
    for event in events:
        print(event)
        


