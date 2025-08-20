# -*- coding: utf-8 -*-

class LocationMaps:
    
    def __init__(self):
        self.keyword = ''
        self.name = ''
        self.category = ''
        self.address = ''
        self.phone = ''
        self.website = ''
        self.pluscode = ''
        self.rating = ''
        self.reviews = ''
        self.hours = ''


class RestaurantMaps(LocationMaps):
    """Enhanced class for restaurant-specific data including menu items"""
    
    def __init__(self):
        super().__init__()
        # Additional restaurant-specific fields
        self.price_range = ''  # $, $$, $$$, $$$$
        # self.cuisine_type = ''  # Italian, Mexican, etc.
        self.dining_options = []  # Dine-in, Takeout, Delivery
        self.amenities = []  # WiFi, Parking, etc.
        self.popular_times = ''  # Peak hours info
        self.menu_items = []  # List of menu items with details
        self.menu_sections = []  # Menu categories/sections
        self.has_online_menu = False
        self.menu_url = ''  # Direct link to menu if available
        # Menu photo fields for OCR processing
        self.has_menu_photos = False
        self.menu_photo_urls = []  # List of menu photo URLs and info
        self.external_links = []  # External links for backup
        # Opening hours: Dictionary of day -> hours (e.g., {"Monday": "11 AM–11 PM", "Tuesday": "Closed"})
        self.opening_hours = {}
        # About information: Dictionary with sections and their items
        # Format: {"section_name": [{"text": "item text", "available": True/False}], "Description": "restaurant description"}
        self.about = {}
        
    def add_menu_item(self, name, price='', description='', section=''):
        """Add a menu item to the restaurant"""
        menu_item = {
            'name': name,
            'price': price,
            'description': description,
            'section': section
        }
        self.menu_items.append(menu_item)
    
    def add_menu_section(self, section_name, items=None):
        """Add a menu section/category"""
        if items is None:
            items = []
        menu_section = {
            'name': section_name,
            'items': items
        }
        self.menu_sections.append(menu_section)