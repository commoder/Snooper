"""Contains all classes related to the processing of data received from supported Weedmaps APIs

    List of Objects
        1. regions
            - A list of strings representing each region available in WeedMaps that is supported by
                snooper.

    List of Classes
        1. WMRegions
        2. WMSubRegions
        3. WMDispensaries
        4. WMDeals
        5. WMMenus
"""
from time import sleep
from collections import OrderedDict
from lib import common

regions = ["alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware",
"florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana",
"maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana",
"nebraska","nevada","new-hampshire","new-jersey","new-mexico","new-york","north-carolina",
"north-dakota","ohio","oklahoma","oregon","pennsylvania","rhode-island","south-carolina",
"south-dakota","tennessee","texas","utah","vermont","virginia","washington","washington-dc",
"west-virginia","wisconsin","wyoming"]

class WMRegions:
    """
    A class used to represent the primary application of the snooper package.

    Attributes
    ----------
    None

    Methods
    -------
    __init__()
        Creates a controller object for communicating with the parent Snooper app.

    """
    def __init__(self, controller):
        self.controller = controller
        self.SubRegions = WMSubRegions(controller)

    def list(self, show=False):
        if show:
            print("Region List")
            for region in regions:
                print(f"- {region}")
            print(f"Region Count: {len(regions)}")
        return regions

    def get_listings(self):
        for region in regions:
            try:
                for subregion in self.controller.data_lib[region]:
                    print(f"Downloading all listings for {subregion}")
                    subregion = self.controller.data_lib[region][subregion]
                    self.SubRegions.get_listings(subregion)
            except KeyError:
                print(f"{region} has not been initialized, skipping!")

    def load_listings(self, region):
        return self.controller.data_lib[region]

    def get_deals(self):
        print("""Note: You are now downloading ALL deals from ALL subregions in ALL regions.
        This is very rest call intensive, and could result in a temporary or even permanent ban!
        Snooper and its contributors are not responsible for this. Use at your own risk!""") # DEBUG

        for region in self.controller.data_lib:
            print(f"Region: {region}")
            subregions = self.controller.data_lib[region]
            for subregion in subregions:
                print(f"Resetting deals in {subregion}")
                self.controller.data_lib[region][subregion]['deals']=[]

            for subregion in subregions:
                print(f"\nParsing deals downloaded from {subregion}")
                sr_str = subregion
                deals = self.SubRegions.get_deals(subregions[subregion])
                for deal in deals:
                    try:
                        subregion_slug = deal['listing']['region']['slug']
                        # if 'deals' not in self.controller.data_lib[region][subregion_slug].keys():
                        #     self.controller.data_lib[region][subregion_slug]['deals']=[]

                        if not any(d['id'] == deal['id'] for d in \
                            self.controller.data_lib[region][subregion_slug]['deals']):
                            self.controller.data_lib[region][subregion_slug]['deals'].append(deal)
                            print(f"- Added deal from {sr_str} to {subregion_slug}") # DEBUG
                    except KeyError:
                        print("Uh Oh! It appears that there is a deal with corrupted json!\
                            \nDon't worry, we just skipped it for you ;)")
                        sleep(2)
            for subregion in subregions:
                print(f"Sorting deals for {subregion}")
                new_deals = {}
                for deal in self.controller.data_lib[region][subregion]['deals']:
                    new_deals[deal['slug']] = deal
                new_deals = OrderedDict(sorted(new_deals.items(), key=lambda t: t[0]))
                self.controller.data_lib[region][subregion]['deals'] = new_deals

    def get_subregions(self, region):
        url = common.url_construct(common.url_library['subregions']['url'], region)
        # self.controller.data_lib[region] = common.get_request(url)['data']['subregions']
        if region not in self.controller.data_lib.keys():
            self.controller.data_lib[region] = {}
        subregions = common.get_request(url)['data']['subregions']
        print(f"Downloading subregions for {region}...")
        sleep(common.rest_call_delay)
        for subregion in subregions:
            subregion['region'] = region
            self.controller.data_lib[region][subregion['slug']] = subregion

    def get_menus(self):
        for region in regions:
            try:

                for subregion in self.controller.data_lib[region]:
                    subregion = self.controller.data_lib[region][subregion]
                    self.controller.SubRegions.get_menus(subregion)
            except KeyError:
                print(f"{region} has no subregions loaded")

class WMSubRegions:
    def __init__(self, controller):
        self.controller = controller
        self.Dispensaries = WMDispensaries(controller)
    def list(self, region, show=False):
        try:
            if show:
                print("Subregion List")
                for subregion in self.controller.data_lib[region]:
                    print(subregion)
            sr_list = list(self.controller.data_lib[region].keys())
        except KeyError:
            sr_list = None
        return sr_list

    def get_menus(self, subregion):
        try:
            listings = subregion['listings']
            print(f"Getting all menus for {subregion['slug']}")
            for listing in listings:
                listing = subregion['listings'][listing]
                self.Dispensaries.get_menu(listing)
        except KeyError:
            print(f"Sorry, but no listings have been loaded for {subregion['slug']}")

    def get_deals(self, subregion):
        self.controller.data_lib[subregion['region']][subregion['slug']]['deals']=[]
        url = common.url_construct(common.url_library["deals"]['url'], subregion['id'])
        rest_return = common.get_request(url)
        sleep(common.rest_call_delay)
        return rest_return['data']['deals']

    def get_listings(self, subregion):
        region = subregion['region']
        listings_processed = 0
        total_listings = None
        rest_return = None
        self.controller.data_lib[region][subregion['slug']]['listings']=[]
        print(f"Downloading listings for {subregion['slug']}")
        while True:
            url = common.url_construct(common.url_library['dispensaries']['url'],
                listings_processed, subregion['slug'])
            if rest_return is None:
                rest_return = common.get_request(url)
                sleep(common.rest_call_delay)
            if total_listings is None:
                total_listings = rest_return['meta']['total_listings']
            elif total_listings == 0 or listings_processed == total_listings:
                for listing in self.controller.data_lib[region][subregion['slug']]['listings']:
                    listing['region']=region
                    listing['subregion']=subregion['slug']
                break
            elif total_listings > 0:
                self.controller.data_lib[region][subregion['slug']]['listings'].extend(
                    rest_return['data']['listings'])
                listings_processed+=len(rest_return['data']['listings'])
                if listings_processed != total_listings:
                    rest_return = None
        new_listings = {}
        for listing in self.controller.data_lib[region][subregion['slug']]['listings']:
            new_listings[listing['slug']] = listing

        # Sort the dictionary
        new_listings = OrderedDict(sorted(new_listings.items(), key=lambda t: t[0]))
        self.controller.data_lib[region][subregion['slug']]['listings'] = new_listings
    def load_listings(self, subregion):
        return self.controller.data_lib[subregion['region']][subregion['slug']]['listings']

class WMDispensaries:
    def __init__(self, controller):
        self.controller = controller
    def list(self, subregion, menu_filter=False):
        total = 0
        for listing in subregion['listings']:
            if menu_filter and subregion['listings'][listing]['menu_items_count']>0:
                print(listing)
                total+=1
            elif not menu_filter:
                print(listing)
                total+=1
        print(f"Total Listings: {total}")

    def get_menu(self, listing):
        print(listing)
        print(f"Downloading menu for {listing['slug']}")
        region = listing['region']
        subregion = listing['subregion']
        items_processed = 0
        total_menu_items = None
        rest_return = None
        page=1
        self.controller.data_lib[region][subregion]['listings'][listing['slug']]['menu']=[]
        while True:
            url = common.url_construct(common.url_library['menu']['url'], listing['slug'], page)
            if rest_return is None:
                rest_return = common.get_request(url)
                print(f"Current Page: {page}")
                sleep(common.rest_call_delay)
            if total_menu_items is None:
                total_menu_items = rest_return['meta']['total_menu_items']
            elif total_menu_items == 0 or items_processed == total_menu_items:
                break
            elif total_menu_items > 0:
                self.controller.data_lib[region][subregion]['listings'][listing['slug']]\
                    ['menu'].extend(rest_return['data']['menu_items'])
                items_processed+=len(rest_return['data']['menu_items'])
                if items_processed != total_menu_items:
                    page+=1
                    rest_return = None
        new_menu = {}
        for item in self.controller.data_lib[region]\
            [subregion]['listings'][listing['slug']]['menu']:
            new_menu[item['slug']] = item
        new_menu = OrderedDict(sorted(new_menu.items(), key=lambda t: t[0]))
        self.controller.data_lib[region][subregion]['listings'][listing['slug']]['menu'] = new_menu

class WMDeals:
    def __init__(self, controller):
        self.controller = controller

    def list(self):
        data_lib = self.controller.data_lib
        for region in data_lib:
            region = data_lib[region]
            for subregion in region:
                subregion = region[subregion]
                if 'deals' in subregion.keys():
                    print(f"{subregion['slug']}: {len(subregion['deals'])}")
                else:
                    print(f"{subregion['slug']}: 0")

class WMMenus:
    def __init__(self, controller):
        self.controller = controller

    def list_subregion_menus(self, subregion, show=False):
        menu_dict = {}
        for listing in subregion['listings']:
            listing = subregion['listings'][listing]
            if "menu" in listing.keys():
                if len(listing['menu']) > 0:
                    menu_dict[listing['slug']] = listing['menu']

        if show:
            print(f"Menus found for {subregion['slug']}")
            for item in menu_dict:
                print(f"- {item}")
            print(f"Item Count: {len(menu_dict)}")
        return menu_dict

    def list_items(self, listing, show=False):
        if show:
            print(f"{listing['slug']} Menu")
            for item in listing['menu']:
                print(f"- {item}")
            print(f"Item Count: {len(listing['menu'])}")
        return listing['menu']
