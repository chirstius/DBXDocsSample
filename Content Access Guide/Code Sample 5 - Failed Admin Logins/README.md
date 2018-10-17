# Code Sample: Detect failed admin logins

For this code sample, we’ve been presented with the task of detecting all failed logins by Dropbox admins within the past 30 days. Let’s use the Python SDK to solve this scenario.

First we need to get a listing of all events related to logins over the past 30 days. We can do this by specifying the login event category to the `team_log/get_events` endpoint, and then specifying a start time parameter of 30 days ago:

```python
import dropbox
from dropbox.team_log import EventCategory
from dropbox.team_common import TimeRange
from datetime import datetime, timedelta
import csv

start = datetime.utcnow() - timedelta(days=30)
result = dbx.team_log_get_events(
    category=EventCategory.logins,
    time=TimeRange(start_time=start)
    )
```

This will get us a listing of events stored in `results.events` but we’re not done yet, there may be more results pending so we need to check for that and call `team_log/get_events/continue` as needed to get them all. We’ll also store the events into an `events` variable for easier processing later:

```python
start = datetime.utcnow() - timedelta(days=30)
result = dbx.team_log_get_events(category=EventCategory.logins, time=TimeRange(start_time=start))
events = result.events

# Collect additional events if needed
while result.has_more:
    result = dbx.team_log_get_events_continue(result.cursor)
    events.extend(result.events)
```

At this point, we should have all of the login events from the past 30 days, now we can filter through them to find login failures, and then further test for admin level users to generate our output. Let’s tie it all together for our final script:

```python
import dropbox
from dropbox.team_log import EventCategory
from dropbox.team_common import TimeRange
from datetime import datetime, timedelta
import csv
import sys

dbx = dropbox.DropboxTeam(<ACCESS TOKEN>)

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
```