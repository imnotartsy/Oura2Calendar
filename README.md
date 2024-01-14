# Oura2Calendar

This is a tool to add your sleep events to your calendar. It uses the [Oura Cloud API](https://cloud.ouraring.com/docs/) to get your sleep data and the [Google Calendar API](https://developers.google.com/calendar) to add the events to your calendar.



# Oura Cloud API
https://cloud.ouraring.com/v2/docs#section/Data-Access

# Google Calendar API
https://developers.google.com/calendar/api/quickstart/python
I'd recommend using the quickstart to get your credentials.json file. You'll need to enable the Google Calendar API for your account.


# Setup
1. Clone the repo
2. Follow the quickstart guide for the Google Calendar API to get your credentials.json file (this may require setting up a Google Cloud Platform project)
3. Get your Oura API token (https://cloud.ouraring.com/personal-access-tokens)

4. Set up your secrets.json file (with your API token + calendar ID)

4. Install the requirements
I didn't make a virtual environment for this, but you can if you want to
This project uses pretty standard dependencies like 
requests, json, matplotlib (incase you want to visualize your data), datetime, os, and a handful of google packages which are noted in the quickstart guide.

5. Set your config variables at the top of main.py

6. Run the script
```
python3 main.py
```

7. Check your calendar!



Note:
* I also created a cron job to run this script every day twice a day (once at midnight and once at noon), check out how to do it [here](
https://phoenixnap.com/kb/cron-job-mac)
```
0 0,12 * * * /YOUR PATH/Oura2Calendar/sleep2calendar-cron.sh
```
* By default, the script will only add events for the current day. If you want to add events for past days, you can set the history variable to True + set your start date. This will add events for every day from the start date to the current day.
* This script can be a little buggy if you try to run history mode multiple times, as checking for duplicates isn't perfect (by default getting past events caps out at 250 events). If you want to run history mode multiple times, I'd recommend deleting the events from your calendar first.