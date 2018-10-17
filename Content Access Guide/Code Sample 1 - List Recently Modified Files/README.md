# Code Sample: List recently modified files

Listing file and folder content is a very common task, for this code sample, we’re going to find the 10 most recently modified files within a user’s Dropbox. For this script we’ll use the Python SDK to simplify access to the Dropbox API.

First we need to collect a list of all the files for the user. We’ll use `files/list_folder` and `files/list_folder/continue` to do this. An important implementation detail to consider when listing content in Dropbox is that you are connected to a live filesystem. This means that is changes are made between iterations of calls to `files/list_folder/continue` those changes will be reflected in the results. While in this specific example we aren’t worried about folders or additional files being added between calls, we do care about any file deletions that may have occurred during our collection as if we don’t remove them our output will reflect files that no longer exist in Dropbox. Further, in a more complex example, tying to operate on file or folder content that was deleted during the collection phase would be inefficient and could lead to errors or confusion for the end user. Let’s create a function to handle this processing:

```python
def process_folder_entries(current_state, entries):
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None) # ignore KeyError if missing
    return current_state
```

This simple implementation uses a dictionary to hold each `FileMetadata` entry (remember we’re not concerned with `FolderMetadata` for this task) keyed by it’s path. If we receive metadata for the same entry it’ll be overwritten with the new data. We then check for `DeletedMetadata` instances and remove those items from the dictionary. `DeletedMetadata` can refer to either files or folders so if a folder entry or a file entry for a file we have not seen yet is processed, we silently ignore the error from `pop()` as the intent is for those entries to not be present.

Now that we have a function to ensure proper content state, let’s make the calls to build our list of content:

```python
import dropbox

def process_folder_entries(current_state, entries):
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None) # ignore KeyError if missing
    return current_state

dbx = dropbox.Dropbox(<ACCESS TOKEN>)

# Build a list of all files from the Dropbox root
print("Scanning for files...")
result = dbx.files_list_folder(path="", recursive=True)
files = process_folder_entries({}, result.entries)
while result.has_more:
    print("Collecting additional files...")
    result = dbx.files_list_folder_continue(result.cursor)
    files = process_folder_entries(files, result.entries)
```

Here we make out initial call to `files/list_folder` and process any entries. If we have more content to retrieve the while loop will take care of making those additional calls using `files/list_folder/continue` and processing those results to update the `files` dictionary.

Now that we have a list of all of the current user’s files, we can simply sort them by modified time and then keep the 10 most recent entries:

```python
recent_files = sorted(files.values(), key=lambda x: x.server_modified, reverse=True)[:10]
for f in recent_files:
    print(f.path_lower + " - " + str(f.server_modified))
```

Let’s put it all together:

```python
import dropbox

def process_folder_entries(current_state, entries):
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None) # ignore KeyError if missing
    return current_state

dbx = dropbox.Dropbox(<ACCESS TOKEN>)

# Build a list of all files from the Dropbox root
print("Scanning for files...")
result = dbx.files_list_folder(path="", recursive=True)
files = process_folder_entries({}, result.entries)
while result.has_more:
    print("Collecting additional files...")
    result = dbx.files_list_folder_continue(result.cursor)
    files = process_folder_entries(files, result.entries)

# sort files by last modified time and output 10 most recently updated
recent_files = sorted(files.values(), key=lambda x: x.server_modified, reverse=True)[:10]
for f in recent_files:
    print(f.path_lower + " - " + str(f.server_modified))
```