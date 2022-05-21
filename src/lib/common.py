"""common.py contains commonly used elements for the various scripts used in Snooper.
    1. Objects
        1. data_dir
            os.path data directory used for saving / exporting data from snooper.
        2. save_file
            the primary save file for snooper to export to.
        3. export_file
            an optional test export file for snooper to export to.
    2. Classes
        None
    3. Functions
        1. clear
            Clears the screen. Used for logging in linux.
        2. url_construct
            Constructs a URL used for REST calls against WeedMaps
        3. get_request
            Performs a GET request.
"""
import os.path
import requests
clear = lambda: os.system('clear')
clear()
rest_call_delay = 5
page_size = 100
api__headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}
url_library = {
    "deals": {
        "url": "https://api-g.weedmaps.com/discovery/v1/deals?filter%5Bregion_id%5D={}&filter%5B\
            types%5D=organic&filter%5Bcategory%5D=all&page=1&page_size=100",
        "needs": "subregion_id" # Received from subregion; is contained in dict
    },
    "menu": {
        "url": "https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{}/menu_items?\
            include%5B%5D=facets.categories&page_size=100&page={}",
        "needs": "dispensary_slug"
    },
    "subregions": {
        "url": "https://api-g.weedmaps.com/wm/v1/regions/{}/subregions",
        "needs": "subregion_name" # Received from region; is contained in a list of dicts
    },
    "dispensaries": {
        "url": "https://api-g.weedmaps.com/discovery/v1/listings?offset={}&page_size=100&size=100\
            &filter[any_retailer_services][]=storefront&filter[region_slug[dispensaries]]={}",
        "needs": "subregion_name" # Received from region; is contained in a list of dicts
    }
}

def url_construct(url_dict, *args):
    """
    Constructs a URL taken from url_library and returns a formatted string using *args

    Parameters
    ----------
    url_dict : string
        A string extracted from url_library to be formatted with additional arguments

    Returns
    -------
    url_dict : string
        A string formatted using additional arguments to perform REST calls
    """
    return url_dict.format(*args)

def get_request(url):
    """
    A simple wrapper function for performing GET REST calls via the requests module

    Parameters
    ----------
    url : string
        A url for performing the GET request

    Returns
    -------
    request.response : dict / JSON
        The response object from the GET request, formatted in JSON for easy save in data_lib
    """
    return requests.get(url, headers=api__headers).json()
