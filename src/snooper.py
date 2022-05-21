"""Snooper is a data processor created for the purpose of downloading JSON data from supported
    WeedMaps APIs to be converted into Pandas DataFrames and stored in multiple different formats.
    1. Objects
        1. data_dir
            os.path data directory used for saving / exporting data from snooper.
        2. save_file
            the primary save file for snooper to export to.
        3. export_file
            an optional test export file for snooper to export to.
    2. Classes
        1. Snooper
            the primary application class for snooper.
"""
import json
import os.path
from datetime import datetime
from pathlib import Path
from lib import actors
from lib import util

# Data directory
data_dir = os.path.dirname(os.path.abspath(__file__))+"/data"
Path(data_dir).mkdir(parents=True, exist_ok=True)

# Primary save file
save_file = data_dir+"/snooper.json"

# debug save file
export_file = data_dir+"/export.json"

class Snooper:
    """
    A class used to represent the primary application of the snooper package.

    Attributes
    ----------
    data_lib : dict
        dictionary representing data stored from converted json received from WeedMaps.

    app : Object/Snooper
        object representing the class executable of Snooper. only accessed if this file is
        ran as main.

    Regions : Object/actors.WMRegions
        Data processor for WeedMaps Regions

    SubRegions : Object/actors.WMSubRegions
        Data processor for WeedMaps SubRegions

    Dispensaries : Object/actors.WMDispensaries
        Data processor for WeedMaps dispensary listings

    Menus : Object/actors.WMMenus
        Data processor for WeedMaps listing menu items

    Deals : Object/actors.WMDeals
        Data processor for WeedMaps deals

    Pandas : Object/util.SnooperToPandas
        addon object that provides additional support via methods for pandas

    selected_region : dict
        dictionary of data extracted using matching method.

    selected_subregion : dict
        dictionary of data extracted using matching method.

    selected_listing : dict
        dictionary of data extracted using matching method.

    selected_menu : dict
        dictionary of data extracted using matching method.

    selected_item : dict
        dictionary of data extracted using matching method.


    Methods
    -------
    select_region(region_slug)
        Stores region data from data_lib in memory using region_slug as key.

    select_subregion(subregion_slug)
        Stores subregion data from data_lib in memory using subregion_slug as key.

    select_listing(listing)
        Stores listing data from data_lib in memory using listing_slug as key.

    select_menu()
        Stores menu data from data_lib in memory using the stored listing data from select_listing.

    load_json(file)
        Loads json from file into data_lib

    save_json(file)
        Saves data from data_lib as json into file

    main()
        Primary standalone executable function of snooper
    """
    data_lib = {}

    def __init__(self):
        """
        Constructs all the necessary attributes for the Snooper object.

        Parameters
        ----------
        None

        """
        self.Regions=actors.WMRegions(self)
        self.SubRegions = actors.WMSubRegions(self)
        self.Dispensaries = actors.WMDispensaries(self)
        self.Menus = actors.WMMenus(self)
        self.Deals = actors.WMDeals(self)
        self.Pandas = util.SnooperToPandas(self)
        self.selected_region = None
        self.selected_subregion = None
        self.selected_listing = None
        self.selected_menu = None
        self.selected_item = None
        print("Creating Snooper App") # DEBUG

    def select_region(self, region_slug):
        """
        Selects a region using region_slug as a key for data_lib

        Parameters
        ----------
        region_slug : str
            A string representing the key of the region to extract from data_lib.

        Returns
        -------
        None
        """
        try:
            self.selected_region = self.data_lib[region_slug]
            print(f"Selected region: {region_slug}")
        except KeyError:
            print("Sorry, but that region doesn't appear to be loaded. \
                Refresh region data and try again.")

    def select_subregion(self, subregion_slug):
        """
        Selects a subregion using subregion_slug as a key for selected_region

        Parameters
        ----------
        subregion_slug : str
            A string representing the key of the subregion to extract from selected_region.

        Returns
        -------
        None
        """
        try:
            self.selected_subregion = self.selected_region[subregion_slug]
            print(f"Selected subregion: {subregion_slug}")
        except KeyError:
            print("Sorry, but that subregion doesn't appear to be loaded. \
                Refresh subregion and try again.")
        except TypeError:
            print("Sorry, but you must select a region first before attempting to select \
                a subregion.")

    def select_listing(self, listing_slug):
        """
        Selects a dispensary listing using listing_slug as a key for selected_subregion

        Parameters
        ----------
        listing_slug : str
            A string representing the key of the listing to extract from selected_subregion.

        Returns
        -------
        None
        """
        try:
            self.selected_listing = self.selected_subregion['listings'][listing_slug]
            print(f"Selected listing: {listing_slug}")
        except KeyError:
            print("Sorry, but that listing doesn't appear to be loaded. \
                Refresh subregion listings and try again.")
        except TypeError:
            print("Sorry, but you must select a subregion first before attempting to \
                select a listing.")

    def select_menu(self):
        """
        Selects the menu listing from selected_listing

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            self.selected_menu = self.selected_listing['menu']
            print(f"Selected Menu: {self.selected_listing['slug']}")
        except KeyError:
            print("Sorry, but that listing doesn't appear to have a menu loaded. \
                Refresh menus for listing or subregion and try again.")
        except TypeError:
            print("Sorry, but you must select a listing first before attempting to select a menu.")

    # def select_item(self, item_slug):
    #     pass

    def load_json(self, file):
        """
        Loads json from file and saves into data_lib as dict.

        Parameters
        ----------
        file : str
            path to file that should be used for data export

        loaded : boolean
            boolean representing the load success state of the file

        Returns
        -------
        loaded : boolean
        """
        loaded = False
        try:
            # in_file = open(common.save_file, "r")
            with open(file, encoding="utf8") as in_file:
                print("Loading data from file...")
                self.data_lib = json.load(in_file)
                print("Data loaded!")
                loaded = True
        except FileNotFoundError:
            print("File not found: Starting from scratch!")
            self.data_lib={}
        return loaded

    def save_json(self, file, data):
        """
        Saves data_lib to a file as json.

        Parameters
        ----------
        file : str
            path to file that should be used for data export
        data
            dictionary to write to file as json

        Returns
        -------
        None
        """
        print("Saving JSON file")
        with open(file, "w", encoding="utf8") as out_file:
            out_file.truncate()
            json.dump(data, out_file)

    def main(self):
        """
        Primary executable function of Snooper

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        start_time = datetime.now()
        print("Running main()")
        # if self.load_json(save_file):
        #     # Define pandas DataFrames
        #     listings_frame = self.Pandas.listings()
        #     subregion_menus_frame = self.Pandas.subregion_menus()
        #     # subregion_deals_frame = self.Pandas.subregion_deals()
        #     region_deals_frame = self.Pandas.region_deals()

        #     # Export to CSV
        #     listings_frame.to_csv(data_dir + "/listings.csv")
        #     subregion_menus_frame.to_csv(data_dir + "/subregion_menus.csv")
        #     region_deals_frame.to_csv(data_dir + "/region_deals.csv")

        # else:
        # Download subregions for region
        self.Regions.get_subregions("oklahoma")

        # Select desired region and subregion
        self.select_region("oklahoma")
        self.select_subregion('oklahoma-city')

        # Download data for export
        self.SubRegions.get_listings(self.selected_subregion)
        self.Regions.get_menus()
        self.Regions.get_deals()

        # Define pandas DataFrames
        listings_frame = self.Pandas.listings()
        subregion_menus_frame = self.Pandas.subregion_menus()
        # subregion_deals_frame = self.Pandas.subregion_deals()
        region_deals_frame = self.Pandas.region_deals()

        # Export to CSV
        listings_frame.to_csv(data_dir + "/listings.csv")
        subregion_menus_frame.to_csv(data_dir + "/subregion_menus.csv")
        region_deals_frame.to_csv(data_dir + "/region_deals.csv")

        # Save to JSON
        self.save_json(export_file, self.data_lib)
        print(f"Time: {datetime.now() - start_time}")


if __name__ == "__main__":
    app = Snooper()
    app.main()
