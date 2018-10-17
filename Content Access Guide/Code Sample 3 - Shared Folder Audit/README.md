# Code Sample: Shared folder access audit for Business teams

Shared folders have a rich set of ACLs to control access. In some cases, content that was only intended for internal team access can get shared with an external entity. Our task for this code sample is to find shared folders for our user that have been shared with external entities. Using the Python SDK, let’s assemble a script to report on all externally accessible content.

First, we must list all shared folders for our user:

```python
import dropbox
...

# For Business Team linked apps we use a DropboxTeam instance
dbx_team = dropbox.DropboxTeam(<ACCESS TOKEN>)
# And then impersonate users as needed
dbx = dbx_team.as_user(<TEAM MEMBER ID>)
...

# Collect all shared folders for our user
result = dbx.sharing_list_folders()
shared_folders = result.entries
while result.cursor:
    result = dbx.sharing_list_folder_continue(cursor=result.cursor)
    shared_folders.extend(result.entries)
```

After collecting all shared folders, we can collect information on everyone who has access to them by making calls to `sharing/list_folder_members` and `sharing/list_folder_members_continue`. The response from these endpoints can be seen in the [HTTP reference documentation](https://www.dropbox.com/developers/documentation/http/documentation#sharing-list_folder_members).

We can call these endpoints as follows:

```python
for folder in shared_folders:
    print(folder.name + ":")
    result = dbx.sharing_list_folder_members(folder.shared_folder_id)
    folder_members = result.users
    while result.cursor:
        result = dbx.sharing_list_folder_continue(cursor=result.cursor)
        folder_members.extend(result.users)
```

This will collect all member information for each shared folder in the `folder_members` variable. Now we can begin filtering for external entities in our folder membership:

```python
for user in folder_members:
        if not user.user.same_team:
            rows.append([
                folder.name,
                folder.owner_team.name if folder.owner_team else "Personal Account",
                user.user.email,
                user.access_type._tag
                ])
```

Here we filter for any users that are not on the same Dropbox Business team as our current user and when we find one we append the folder name, the remote team name, if any, the external user’s email address, and finally, their level of access. This information will then be printed out in CSV format.

Let’s take a look at the completed script:

```python
import dropbox
import csv
import sys

# For Business Team linked apps we use a DropboxTeam instance
dbx_team = dropbox.DropboxTeam(<ACCESS TOKEN>)
# And then impersonate users as needed
dbx = dbx_team.as_user(<TEAM MEMBER ID>)

headers = ["Folder","Team", "Email", "Access Level"]
rows = []
csvwriter = csv.writer(sys.stdout, lineterminator='\n')

# Collect all shared folders for our user
result = dbx.sharing_list_folders()
shared_folders = result.entries
while result.cursor:
    result = dbx.sharing_list_folder_continue(cursor=result.cursor)
    shared_folders.extend(result.entries)

# Collect shared folder membership information    
for folder in shared_folders:
    result = dbx.sharing_list_folder_members(folder.shared_folder_id)
    folder_members = result.users
    while result.cursor:
        result = dbx.sharing_list_folder_continue(cursor=result.cursor)
        folder_members.extend(result.users)
    
    # Check for external users
    for user in folder_members:
        if not user.user.same_team:
            rows.append([
                folder.name,
                folder.owner_team.name if folder.owner_team else "Personal Account",
                user.user.email,
                user.access_type._tag
                ])

# Generate CSV report
csvwriter.writerow(headers)
for row in rows:
    csvwriter.writerow(row)
```