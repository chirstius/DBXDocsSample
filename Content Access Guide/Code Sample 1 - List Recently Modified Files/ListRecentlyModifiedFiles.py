import dropbox

def process_folder_entries(current_state, entries):
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None) # ignore KeyError if missing
    return current_state

dbx = dropbox.Dropbox("<ACCESS TOKEN>")

### Build a list of files from a given path - ignoring folders
print("Scanning for files...")
result = dbx.files_list_folder(path="", recursive=True)
files = process_folder_entries({}, result.entries)
while result.has_more:
    print("Collecting additional files...")
    result = dbx.files_list_folder_continue(result.cursor)
    files = process_folder_entries(files, result.entries)

# sort files by last modified time and collect 10 most recently updated
recent_files = sorted(files.values(), key=lambda x: x.server_modified, reverse=True)
for f in recent_files[:10]:
    print(f.path_lower + " - " + str(f.server_modified))