# Code Sample: Explicit file sharing access

Say we are presented with a scenario where we need to locally download the content of files explicitly shared with us if they have been recently updated. Let’s step through how to solve this scenario:

First, we need to get a list of explicitly shared files. We can do this with a call to the `sharing/list_received_files` endpoint. Using the Python SDK we can gather all explicitly shared files as follows:

```python
import dropbox

dbx = dropbox.Dropbox(<ACCESS TOKEN>)

# list all files explicitly shared with our user
result = dbx.sharing_list_received_files()
shared_files = result.entries
while result.cursor:
    result = dbx.sharing_list_received_files_continue(result.cursor)
    shared_files.extend(result.entries)
```

This collects all explicitly shared files into the `shared_files` list, calling the `sharing/list_received_files_continue` endpoint as required until the list is fully populated.

The `shared_files` list will contain all files explicitly shared with us, but it will also contain all files we have explicitly shared to others. Since we don’t want to download content we already own we need to filter our list to contain only files shared to us. We can do this by filtering the list on the access type property where we are not tagged as the owner of the file:

```python
shared_files = list(filter(lambda entry: entry.access_type.is_viewer(),shared_files))
```

This line builds a new list selecting only the entries where we are listed as a viewer of the file and filtering out any entries where we are listed as the owner. We now have a list of only the files explicitly shared with us.

Next we need to examine the modified time of each of these files. Looking back at the output from `sharing/list_received_files` we see a field for `time_invited`, but nothing for when the file was modified. To get this information we need to call another endpoint `sharing/get_shared_link_metadata` which will return additional metadata about the file. The response from this endpoint can be found in the [HTTP reference documentation](https://www.dropbox.com/developers/documentation/http/documentation#sharing-get_shared_link_metadata).

The returned metadata contains both a `client_modified` and `server_modified` timestamp. We’ll use the `server_modified` timestamp to determine if the file has been updated and we need to download it. `sharing/get_shared_link_metadata` expects a link URL as it’s parameter. We can use the `preview_url` field returned from `sharing/list_received_files` to provide this value. Let’s add the code to get the metadata and test for the newness of the shared file:

```python
import datetime
...
for entry in shared_files:
    file_metadata = dbx.sharing_get_shared_link_metadata(entry.preview_url)
    # create a sample previously modified timestamp of 5 days ago
    prev_modified_time = datetime.datetime.now() - datetime.timedelta(days=5)
    # check if server modified time is newer (greater) than our previous timestamp
    # and if so, we will download the file
    if file_metadata.server_modified > prev_modified_time:
```

Now we’re ready to download the content of the shared file. We can do this by using the SDK convenience method `sharing_get_shared_link_file_to_file()` which wraps the endpoint `sharing/get_shared_link_file` and automatically handles creating and saving the contents to a local file. Once again, we’ll use the `preview_url` field to specify the content we want to download:

```python
if file_metadata.server_modified > prev_modified_time:
    dbx.sharing_get_shared_link_file_to_file("MY/LOCAL/PATH/" + entry.name, entry.preview_url)
```

`sharing_get_shared_link_file_to_file()` takes a few parameters:

- The download path where you want to file content to be stored locally which we create here by providing a folder, and then using the `name` field for the current shared file
- The link URL that points to the file to be downloaded
- An optional sub-path parameter to identify a specific file if the link you are providing is to a shared folder
- An optional password for the link if the link you are accessing is password protected

For our example here, we need only to worry about a local path, and the link URL itself.

Putting everything together our completed script should look like this:

```python
import dropbox
import datetime

dbx = dropbox.Dropbox(<ACCESS TOKEN>)

# list all files explicitly shared with our user
result = dbx.sharing_list_received_files()
shared_files = result.entries
while result.cursor:
    result = dbx.sharing_list_received_files_continue(result.cursor)
    shared_files.extend(result.entries)

# filter only to files shared with us, exclude files we own
shared_files = list(filter(lambda entry: entry.access_type.is_viewer(),shared_files))

for entry in shared_files:
    # collect file metadata to acquire modified timestamps
    file_metadata = dbx.sharing_get_shared_link_metadata(entry.preview_url)

    # create a previously modified timestamp of 5 days ago
    prev_modified_time = datetime.datetime.now() - datetime.timedelta(days=5)
    # check if server modified time is newer (greater) than our previous timestamp
    # and if so, we will download the file
    if file_metadata.server_modified > prev_modified_time:
        dbx.sharing_get_shared_link_file_to_file("MY/LOCAL/PATH/" + entry.name, entry.preview_url)
```