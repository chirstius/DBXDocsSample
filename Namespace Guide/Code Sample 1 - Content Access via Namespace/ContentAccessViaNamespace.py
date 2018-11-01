
import dropbox
import sys

if sys.version.startswith('2'):
    input = raw_input  # pylint: disable=redefined-builtin,undefined-variable,useless-suppression

dbx_team = dropbox.DropboxTeam("<ACCESS_TOKEN>")

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

# Prompt for admin account email 
email = input("Enter team admin email: ")

# Select a user via email
team_member_info = dbx_team.team_members_get_info(
        [dropbox.team.UserSelectorArg.email(email)]
    ).pop()

# Verify that user is a valid team member, and also a full team admin
if  (
    team_member_info and
    team_member_info.is_member_info() and
    team_member_info.get_member_info().role.is_team_admin()
    ):
        team_member_id = team_member_info.get_member_info().profile.team_member_id
        admin_dbx = dbx_team.as_admin(team_member_id)
else:
    print("User " + email + " was not found or is not a team admin. Exiting...")
    exit()

print("Scanning for namespaces...")
result = dbx_team.team_namespaces_list()
namespaces = result.namespaces

while result.has_more:
    print("Collecting additional namespaces...")
    result = dbx_team.team_namespaces_list_continue(result.cursor)
    namespaces.extend(result.namespaces)

# NOTE: While not shown here, namespaces are an excellent unit of work for
# parallelism/threading when collecting large amounts of content
for namespace in namespaces:
    # In some cases an admin may not have permission to access a given namespace
    # directly from their account. Here we check to see if a team_member_id is
    # provided for the namespace and if so, we access it as that user, otherwise
    # we access it via our "default" admin account
    if namespace.team_member_id:
        dbx = dbx_team.as_user(namespace.team_member_id)
    else:
        dbx = admin_dbx
        
    print("Collecting files for namespace {}({})..."
        .format(namespace.name, namespace.namespace_id))    
    result = dbx.files_list_folder(
        path="ns:" + namespace.namespace_id,
        recursive=True
    )  
    files = process_entries({}, result.entries)
    
    while result.has_more:
        print("Collecting additional files for namespace {}({})..."
            .format(namespace.name, namespace.namespace_id))
        result = dbx.files_list_folder_continue(result.cursor)
        files = process_entries(files, result.entries)
    
    for entry in files.values():
        print(entry.path_lower)