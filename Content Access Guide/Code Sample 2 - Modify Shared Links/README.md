# Code Sample: Shared link modification

Sometimes we may need to limit access to certain content. Shared links can have many different policies applied to limit access, one of which is an expiration date. For this code sample, we have been tasked with collecting all of the shared links for a user, and adding an expiration to any file-based links that will remove the links 30 days from now. Using the Python SDK, let’s build a script to solve this scenario.

To begin, we need to build a list of all shared links for our user:


    import dropbox
    
    dbx = dropbox.Dropbox(<ACCESS TOKEN>)
    # Collect all shared links for our user
    result = dbx.sharing_list_shared_links()
    shared_links = result.links
    while result.has_more:
        result = dbx.sharing_list_shared_links(cursor=result.cursor)
        shared_links.extend(result.links)

Once we’ve assembled this list we need to filter for only `FileLinkMetadata` instances which have no expiration configured. We can perform this check as follows:


    for link in shared_links:
        # test if the link points to a file and has no expiration
        if isinstance(link, dropbox.sharing.FileLinkMetadata) and link.expires is None:

After identifying file-based links with no expiration, we can use `/sharing/modify_shared_link_settings` to add an expiration to these links:


    import datetime
    ...
    if isinstance(link, dropbox.sharing.FileLinkMetadata) and link.expires is None:
        # create updated link settings to add an expiration 30 days from now
        expires = datetime.datetime.now() + datetime.timedelta(days=30)
        link_settings = SharedLinkSettings(expires=expires)
        # modify the link to add the expiration date
        link = dbx.sharing_modify_shared_link_settings(link.url, settings=link_settings)
        print("Link " + link.path_lower + " now expires on " + link.expires.strftime("%Y-%m-%d %H:%M:%S"))

And our completed script would look like this:


    import dropbox
    import datetime
    
    dbx = dropbox.Dropbox(<ACCESS TOKEN>)
    
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
            link = dbx.sharing_modify_shared_link_settings(link.url, settings=link_settings)
            print("Link " + link.path_lower + " now expires on " + link.expires.strftime("%Y-%m-%d %H:%M:%S"))