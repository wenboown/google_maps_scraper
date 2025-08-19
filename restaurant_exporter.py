# -*- coding: utf-8 -*-

import xlwt
import json
import csv
from datetime import datetime


class RestaurantDataExporter:
    """Enhanced exporter for restaurant data including menu items"""
    
    def __init__(self, output_folder, restaurants_list):
        self.output_folder = output_folder
        self.restaurants_list = restaurants_list
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_to_excel(self, filename=None):
        """Export restaurant data to Excel format"""
        if filename is None:
            filename = f"restaurant_data_{self.timestamp}.xls"
        
        filepath = f"{self.output_folder}{filename}"
        
        writeBook = xlwt.Workbook(encoding='utf-8')
        
        # Create main restaurant info sheet
        self._create_restaurant_sheet(writeBook)
        
        # Create menu items sheet
        self._create_menu_sheet(writeBook)
        
        # Create amenities sheet
        self._create_amenities_sheet(writeBook)
        
        writeBook.save(filepath)
        print(f"Excel file saved: {filepath}")
        return filepath
    
    def _create_restaurant_sheet(self, workbook):
        """Create the main restaurant information sheet"""
        sheet = workbook.add_sheet("Restaurants", cell_overwrite_ok=True)
        
        # Headers
        headers = [
            'SEARCH_KEYWORD', 'NAME', 'CATEGORY', 'CUISINE_TYPE', 'ADDRESS', 
            'PHONE', 'WEBSITE', 'PLUS_CODE', 'PRICE_RANGE', 'RATING', 'REVIEWS', 
            'OPENING_HOURS', 'DINING_OPTIONS', 'HAS_ONLINE_MENU', 'MENU_URL', 
            'POPULAR_TIMES', 'TOTAL_MENU_ITEMS', 'EXTERNAL_LINKS', 'ORDERING_LINKS'
        ]
        
        # Write headers
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # Write data
        for row, restaurant in enumerate(self.restaurants_list, 1):
            sheet.write(row, 0, restaurant.keyword)
            sheet.write(row, 1, restaurant.name)
            sheet.write(row, 2, restaurant.category)
            sheet.write(row, 3, getattr(restaurant, 'cuisine_type', ''))
            sheet.write(row, 4, restaurant.address)
            sheet.write(row, 5, restaurant.phone)
            sheet.write(row, 6, restaurant.website)
            sheet.write(row, 7, restaurant.pluscode)
            sheet.write(row, 8, getattr(restaurant, 'price_range', ''))
            sheet.write(row, 9, restaurant.rating)
            sheet.write(row, 10, restaurant.reviews)
            sheet.write(row, 11, restaurant.hours.replace('\n', '; ') if restaurant.hours else '')
            sheet.write(row, 12, '; '.join(getattr(restaurant, 'dining_options', [])))
            sheet.write(row, 13, 'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No')
            sheet.write(row, 14, getattr(restaurant, 'menu_url', ''))
            sheet.write(row, 15, getattr(restaurant, 'popular_times', ''))
            sheet.write(row, 16, len(getattr(restaurant, 'menu_items', [])))
    
    def _create_menu_sheet(self, workbook):
        """Create the menu items sheet"""
        sheet = workbook.add_sheet("Menu_Items", cell_overwrite_ok=True)
        
        # Headers
        headers = ['RESTAURANT_NAME', 'MENU_SECTION', 'ITEM_NAME', 'PRICE', 'DESCRIPTION']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        row = 1
        for restaurant in self.restaurants_list:
            menu_items = getattr(restaurant, 'menu_items', [])
            if menu_items:
                for item in menu_items:
                    sheet.write(row, 0, restaurant.name)
                    sheet.write(row, 1, item.get('section', ''))
                    sheet.write(row, 2, item.get('name', ''))
                    sheet.write(row, 3, item.get('price', ''))
                    sheet.write(row, 4, item.get('description', ''))
                    row += 1
            else:
                # Write a row even if no menu items to maintain restaurant reference
                sheet.write(row, 0, restaurant.name)
                sheet.write(row, 1, 'No menu data available')
                sheet.write(row, 2, '')
                sheet.write(row, 3, '')
                sheet.write(row, 4, '')
                row += 1
    
    def _create_amenities_sheet(self, workbook):
        """Create the amenities and features sheet"""
        sheet = workbook.add_sheet("Amenities", cell_overwrite_ok=True)
        
        # Headers
        headers = ['RESTAURANT_NAME', 'AMENITIES', 'DINING_OPTIONS', 'MENU_SECTIONS']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        for row, restaurant in enumerate(self.restaurants_list, 1):
            sheet.write(row, 0, restaurant.name)
            sheet.write(row, 1, '; '.join(getattr(restaurant, 'amenities', [])))
            sheet.write(row, 2, '; '.join(getattr(restaurant, 'dining_options', [])))
            
            # Menu sections
            menu_sections = getattr(restaurant, 'menu_sections', [])
            section_names = [section.get('name', '') for section in menu_sections]
            sheet.write(row, 3, '; '.join(section_names))
    
    def export_to_csv(self, filename=None):
        """Export restaurant data to CSV format"""
        if filename is None:
            filename = f"restaurant_data_{self.timestamp}.csv"
        
        filepath = f"{self.output_folder}{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            headers = [
                'search_keyword', 'name', 'category', 'cuisine_type', 'address', 
                'phone', 'website', 'plus_code', 'price_range', 'rating', 'reviews', 
                'opening_hours', 'dining_options', 'has_online_menu', 'menu_url', 
                'popular_times', 'amenities', 'total_menu_items', 'menu_items_json'
            ]
            writer.writerow(headers)
            
            # Data
            for restaurant in self.restaurants_list:
                menu_items_json = json.dumps(getattr(restaurant, 'menu_items', []), ensure_ascii=False)
                
                row = [
                    restaurant.keyword,
                    restaurant.name,
                    restaurant.category,
                    getattr(restaurant, 'cuisine_type', ''),
                    restaurant.address,
                    restaurant.phone,
                    restaurant.website,
                    restaurant.pluscode,
                    getattr(restaurant, 'price_range', ''),
                    restaurant.rating,
                    restaurant.reviews,
                    restaurant.hours.replace('\n', '; ') if restaurant.hours else '',
                    '; '.join(getattr(restaurant, 'dining_options', [])),
                    'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No',
                    getattr(restaurant, 'menu_url', ''),
                    getattr(restaurant, 'popular_times', ''),
                    '; '.join(getattr(restaurant, 'amenities', [])),
                    len(getattr(restaurant, 'menu_items', [])),
                    menu_items_json
                ]
                writer.writerow(row)
        
        print(f"CSV file saved: {filepath}")
        return filepath
    
    def export_to_json(self, filename=None):
        """Export restaurant data to JSON format"""
        if filename is None:
            filename = f"restaurant_data_{self.timestamp}.json"
        
        filepath = f"{self.output_folder}{filename}"
        
        restaurants_data = []
        
        for restaurant in self.restaurants_list:
            restaurant_dict = {
                'search_keyword': restaurant.keyword,
                'name': restaurant.name,
                'category': restaurant.category,
                'cuisine_type': getattr(restaurant, 'cuisine_type', ''),
                'address': restaurant.address,
                'phone': restaurant.phone,
                'website': restaurant.website,
                'plus_code': restaurant.pluscode,
                'price_range': getattr(restaurant, 'price_range', ''),
                'rating': restaurant.rating,
                'reviews': restaurant.reviews,
                'opening_hours': restaurant.hours,
                'dining_options': getattr(restaurant, 'dining_options', []),
                'amenities': getattr(restaurant, 'amenities', []),
                'has_online_menu': getattr(restaurant, 'has_online_menu', False),
                'menu_url': getattr(restaurant, 'menu_url', ''),
                'popular_times': getattr(restaurant, 'popular_times', ''),
                'menu_items': getattr(restaurant, 'menu_items', []),
                'menu_sections': getattr(restaurant, 'menu_sections', [])
            }
            restaurants_data.append(restaurant_dict)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(restaurants_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"JSON file saved: {filepath}")
        return filepath
    
    def export_menu_summary(self, filename=None):
        """Export a summary of menu items across all restaurants"""
        if filename is None:
            filename = f"menu_summary_{self.timestamp}.csv"
        
        filepath = f"{self.output_folder}{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            writer.writerow(['restaurant_name', 'total_menu_items', 'menu_sections', 'sample_items'])
            
            for restaurant in self.restaurants_list:
                menu_items = getattr(restaurant, 'menu_items', [])
                menu_sections = getattr(restaurant, 'menu_sections', [])
                
                section_names = [section.get('name', '') for section in menu_sections]
                sample_items = [item.get('name', '') for item in menu_items[:5]]  # First 5 items
                
                writer.writerow([
                    restaurant.name,
                    len(menu_items),
                    '; '.join(section_names),
                    '; '.join(sample_items)
                ])
        
        print(f"Menu summary saved: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print a summary of the extracted data"""
        total_restaurants = len(self.restaurants_list)
        restaurants_with_menus = sum(1 for r in self.restaurants_list if getattr(r, 'menu_items', []))
        total_menu_items = sum(len(getattr(r, 'menu_items', [])) for r in self.restaurants_list)
        
        print(f"\n=== EXTRACTION SUMMARY ===")
        print(f"Total restaurants processed: {total_restaurants}")
        print(f"Restaurants with menu data: {restaurants_with_menus}")
        print(f"Total menu items extracted: {total_menu_items}")
        print(f"Average menu items per restaurant: {total_menu_items/total_restaurants:.1f}")
        
        if restaurants_with_menus > 0:
            print(f"Average menu items per restaurant with menus: {total_menu_items/restaurants_with_menus:.1f}")
        
        # Show restaurants with most menu items
        restaurants_by_menu_count = sorted(
            self.restaurants_list, 
            key=lambda r: len(getattr(r, 'menu_items', [])), 
            reverse=True
        )
        
        print(f"\nTop restaurants by menu items:")
        for i, restaurant in enumerate(restaurants_by_menu_count[:5]):
            menu_count = len(getattr(restaurant, 'menu_items', []))
            print(f"{i+1}. {restaurant.name}: {menu_count} items")