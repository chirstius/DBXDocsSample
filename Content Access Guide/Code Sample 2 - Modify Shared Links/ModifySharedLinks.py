import dropbox
import datetime
from dropbox.sharing import SharedLinkSettings
from dropbox.exceptions import ApiError

dbx = dropbox.Dropbox("<ACCESS TOKEN>")

# Collect all shared links for our user
result = dbx.sharing_list_shared_links()
shared_links = result.links
while result.has_more:
    result = dbx.sharing_list_shared_links(cursor=result.cursor)
    shared_links.extend(result.links)

for link in shared_links:
    # test if the link points to a file and has no expiration
    if isinstance(link, dropbox.sharing.FileLinkMetadata) and link.expires is None:
        # create updated link settings to add an expiration 30 days from now
        expires = datetime.datetime.now() + datetime.timedelta(days=30)
        link_settings = SharedLinkSettings(expires=expires)
        # modify the link to add the expiration date
        try:
            link = dbx.sharing_modify_shared_link_settings(link.url, settings=link_settings)
            print("Link " + link.path_lower + " now expires on " + link.expires.strftime("%Y-%m-%d %H:%M:%S"))
        except ApiError as e:
            if e.error.is_settings_error():
                if e.error.get_settings_error().is_not_authorized():
                    print("This user, or Dropbox account type, is not authorized to modify shared link settings")
                elif e.error.get_settings_error().is_invalid_settings():
                    print("One or more shared link settings are invalid. The attempted settings were:\n" + str(link_settings))