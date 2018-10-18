import dropbox
import csv
import sys

# For Business Team linked apps we use a DropboxTeam instance
dbx_team = dropbox.DropboxTeam("<ACCESS TOKEN>")
# And then impersonate users as needed
dbx = dbx_team.as_user("<TEAM MEMBER ID>")

headers = ["Folder","Team", "Email", "Access Level"]
rows = []
csvwriter = csv.writer(sys.stdout, lineterminator='\n')

# Collect all shared folders for our user
result = dbx.sharing_list_folders()
shared_folders = result.entries
while result.cursor:
    result = dbx.sharing_list_folder_continue(cursor=result.cursor)
    shared_folders.extend(result.entries)
    
for folder in shared_folders:
#     print(folder)
    result = dbx.sharing_list_folder_members(folder.shared_folder_id)
    folder_members = result.users
    while result.cursor:
        result = dbx.sharing_list_folder_continue(cursor=result.cursor)
        folder_members.extend(result.users)
    
    # check for external users
    for user in folder_members:
        if not user.user.same_team:
            rows.append([
                folder.name,
                folder.owner_team.name if folder.owner_team else "Personal Account",
                user.user.email,
                user.access_type._tag
                ])

# Genrate CSV report
csvwriter.writerow(headers)
for row in rows:
    csvwriter.writerow(row)