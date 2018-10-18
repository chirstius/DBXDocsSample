import dropbox
import datetime

dbx = dropbox.Dropbox("<ACCESS TOKEN>")

result = dbx.sharing_list_received_files()
shared_files = result.entries
while result.cursor:
    result = dbx.sharing_list_received_files_continue(result.cursor)
    shared_files.extend(result.entries)

# filter only to files shared with us, exclude files we own
shared_files = list(filter(lambda entry: entry.access_type.is_viewer(), shared_files))
    
for entry in shared_files:
    # collect file metadata to acquire modified timestamps
    file_metadata = dbx.sharing_get_shared_link_metadata(entry.preview_url)
    
    # create a previously modified timestamp of 5 days ago
    prev_modified_time = datetime.datetime.now() - datetime.timedelta(days=5)
    # check if server modified time is newer (greater) than our previous timestamp
    # and if so, we will download the file
    if file_metadata.server_modified > prev_modified_time:
        dbx.sharing_get_shared_link_file_to_file("MY/LOCAL/PATH/" + entry.name, entry.preview_url)