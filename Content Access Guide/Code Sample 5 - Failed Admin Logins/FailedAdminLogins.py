import dropbox
from dropbox.team_log import EventCategory
from dropbox.team_common import TimeRange
from datetime import datetime, timedelta
import csv
import sys

dbx = dropbox.DropboxTeam("<ACCESS TOKEN>")

headers = ["Timestamp","Email", "Login Error"]
csvwriter = csv.writer(sys.stdout, lineterminator='\n')

# Collect login events
start = datetime.utcnow() - timedelta(days=30)
result = dbx.team_log_get_events(category=EventCategory.logins, time=TimeRange(start_time=start))
events = result.events

# Collect additional events if needed
while result.has_more:
    result = dbx.team_log_get_events_continue(result.cursor)
    events.extend(result.events)

csvwriter.writerow(headers)
for event in events:
    if event.event_type.is_login_fail() and event.actor.is_admin():
        csvwriter.writerow((
            event.timestamp,
            event.actor.get_admin().email,
            event.details.get_login_fail_details().error_details.user_friendly_message)
        )