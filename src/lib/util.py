"""util.py contains classes needed for various jobs
    1. Objects
        None
    2. Classes
        1. SnooperToPandas
            Used for properly loading data into a Pandas Dataframe from data_lib.
    3. Functions
        None
"""
import pandas as pd

class SnooperToPandas:
    """
    A class used to represent the primary application of the snooper package.

    Attributes
    ----------
    menu_columns : array
        Array of strings representing the columns used for WeedMaps Menu Dataframes.

    listing_columns : array
        Array of strings representing the columns used for WeedMaps Dispensary Listing Dataframes.

    deal_columns : array
        Array of strings representing the columns used for WeedMaps Deal Dataframes.


    Methods
    -------
    __init__()
        Creates a controller object for communicating with the parent Snooper app.

    subregion_deals()
        Uses the selected subregion in Snooper to extract the deals from the Snooper data_lib,
        and generates a Pandas Dataframe using that data, and returns it.

    region_deals()
        Uses the selected region in Snooper to extract the deals from the Snooper data_lib for each
        subregion under the region, and returns a generated Pandas Dataframe using that data.

    listing_menu()
        Uses the selected menu in Snooper to generate a Pandas Dataframe for each menu item, then
        returns it.

    subregion_menus()
        Uses the selected subregion to iterate over each Dispensary listing in that subregion.
        During this loop it generates a Pandas Dataframe for each listings menu, and returns it.

    listings()
        Uses the selected subregion to iterate over each listing in the subregion, and return
        a Pandas Dataframe.
    """
    menu_columns = [
        'id',
        'name',
        'slug',
        'category.name',
        'edge_category.name',
        'price.price', 'price.unit', 'price.label', 'price.quantity',
        'reviews_count',
        'rating',
        'is_endorsed',
        'is_badged',
        'created_at',
        'listing'
    ]

    listing_columns = [
        "id",
        "name",
        "slug",
        "city",
        "type",
        "web_url",
        "ranking",
        "rating",
        "reviews_count",
        "has_sale_items",
        "address",
        "zip_code",
        "timezone",
        "open_now",
        "closes_in",
        "todays_hours_str",
        "menu_items_count",
        "verified_menu_items_count",
        "is_published",
        "email",
        "phone_number",
        "region",
        "subregion"
    ]

    deal_columns = [
        "id",
        "listing.slug",
        "listing.region.slug",
        "listing.web_url",
        "title",
        "body"
    ]

    special_columns = {
    }

    def __init__(self, controller):
        self.controller = controller

    def subregion_deals(self):
        """
        Loads every deal in a selected subregion.

        Parameters
        ----------
        None

        Returns
        -------
        deals_frame : Pandas.Dataframe
        """
        data = []
        subregion = self.controller.selected_subregion
        deals = self.controller.data_lib[subregion['region']][subregion['slug']]['deals']
        processed = 0
        for deal in deals:
            deal = deals[deal]
            data.append(deal)
            processed+=1
        print(f"Deals Processed: {processed}")
        print("Generating DataFrame ...")
        deals_frame = pd.json_normalize(data)[self.deal_columns]
        return deals_frame

    def region_deals(self):
        """
        Loads every deal in a selected region.

        Parameters
        ----------
        None

        Returns
        -------
        deals_frame : Pandas.Dataframe
        """
        data = []
        region = self.controller.selected_region
        total = 0
        for subregion in region:
            subregion = region[subregion]
            deals = self.controller.data_lib[subregion['region']][subregion['slug']]['deals']
            processed = 0
            for deal in deals:
                deal = deals[deal]
                data.append(deal)
                processed+=1
                total+=1
            print(f"Deals Processed for {subregion['slug']}: {processed}")
        print(f"Total deals processed: {total}")
        deals_frame = pd.json_normalize(data)[self.deal_columns]
        return deals_frame

    def listing_menu(self):
        """
        Loads every menu item in a selected listing.

        Parameters
        ----------
        None

        Returns
        -------
        menu_frame : Pandas.Dataframe
        """
        data = []

        menu = self.controller.selected_menu
        processed = 0
        for item in menu:
            item = menu[item]
            data.append(item)
            processed+=1
        print(f"Items Processed: {processed}")
        print("Generating DataFrame ...")
        menu_frame = pd.json_normalize(data)[self.menu_columns]
        return menu_frame

    def subregion_menus(self):
        """
        Loads every menu item from every listing in a selected subregion.

        Parameters
        ----------
        None

        Returns
        -------
        menu_frame : Pandas.Dataframe
        """
        data = []
        total = 0
        subregion = self.controller.selected_subregion
        for listing in subregion['listings']:
            listing = subregion['listings'][listing]

            menu = listing['menu']
            processed = 0
            for item in menu:
                item = menu[item]
                item['listing'] = listing['slug']
                data.append(item)
                processed+=1
                total+=1
            print(f"Items Processed for {listing['slug']}: {processed}")
        print(f"Total: {total}")
        menu_frame = pd.json_normalize(data)[self.menu_columns]
        return menu_frame

    def listings(self):
        """
        Loads every listing from a selected subregion.

        Parameters
        ----------
        None

        Returns
        -------
        listing_frame : Pandas.Dataframe
        """
        data = []
        subregion = self.controller.selected_subregion['listings']
        processed = 0
        for listing in subregion:
            listing = subregion[listing]
            data.append(listing)
            processed+=1
        print(f"Listings Processed: {processed}")
        print("Generating DataFrame ...")
        listing_frame = pd.json_normalize(data)[self.listing_columns]
        return listing_frame
