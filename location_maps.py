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
        # Essential restaurant-specific fields
        self.menu_items = []  # List of menu items with details
        self.has_online_menu = False
        self.menu_url = ''  # Direct link to menu if available
        # Menu photo fields for OCR processing
        self.has_menu_photos = False
        self.menu_photo_urls = []  # List of menu photo URLs and info
        self.external_links = []  # External links for backup
        # Opening hours: Dictionary of day -> hours (e.g., {"Monday": "11 AM–11 PM", "Tuesday": "Closed"})
        self.opening_hours = {}
        # About information: Dictionary with sections and their items
        # Format: {"section_name": ["item1", "item2"], "Description": "restaurant description"}
        # This replaces dining_options, amenities, etc. as they're all captured in about
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
    
    def get_dining_options(self):
        """Get dining options from about information"""
        return self.about.get('Service options', [])
    
    def get_amenities(self):
        """Get amenities from about information"""
        amenities = []
        # Combine various amenity-related sections
        for section in ['Amenities', 'Accessibility', 'Payments', 'Parking']:
            amenities.extend(self.about.get(section, []))
        return amenities