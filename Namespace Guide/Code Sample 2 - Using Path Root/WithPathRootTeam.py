import dropbox
from dropbox.common import PathRoot
import sys

if sys.version.startswith('2'):
    input = raw_input  # pylint: disable=redefined-builtin,undefined-variable,useless-suppression

def process_entries(current_state, entries):
    for entry in entries:
        if (
        isinstance(entry, dropbox.files.FileMetadata) or
        isinstance(entry, dropbox.files.FolderMetadata)
        ):
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None)
    return current_state

# Initialize Dropbox API
dbx_team = dropbox.DropboxTeam("ACCESS TOKEN")

# Prompt for account email 
email = input("Enter team member email: ")

# Select a user via email
team_member_info = dbx_team.team_members_get_info(
        [dropbox.team.UserSelectorArg.email(email)]
    ).pop()
 
# Verify that user is a valid team member
if  team_member_info and team_member_info.is_member_info():
        team_member_id = team_member_info.get_member_info().profile.team_member_id
        user_dbx = dbx_team.as_user(team_member_id)
else:
    print("User " + email + " was not found. Exiting...")
    exit()
 
# get the root_namspace_id for this account
user_info = user_dbx.users_get_current_account()
root_ns = user_info.root_info.root_namespace_id

# update API client instance with new path root
user_dbx = user_dbx.with_path_root(PathRoot.root(root_ns))

print("Collecting files...")
result = user_dbx.files_list_folder(path="", recursive=True)
files = process_entries({}, result.entries)

# check for and collect any additional entries
while result.has_more:
    print("Collecting additional files...")
    result = user_dbx.files_list_folder_continue(result.cursor)
    files = process_entries(files, result.entries)

for entry in files.values():
    if isinstance(entry, dropbox.files.FolderMetadata) and entry.sharing_info:
        print("{} (Read Only: {}, Traverse Only: {}, No Access: {})"
            .format(
                entry.path_display,
                entry.sharing_info.read_only,
                entry.sharing_info.traverse_only,
                entry.sharing_info.no_access
            )
        )
    else:
        print(entry.path_lower)