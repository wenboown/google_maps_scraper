# -*- coding: utf-8 -*-

import xlwt
import json
import csv
import re
from datetime import datetime


class RestaurantDataExporter:
    """Enhanced exporter for restaurant data including menu items"""
    
    def __init__(self, output_folder, restaurants_list):
        self.output_folder = output_folder
        self.restaurants_list = restaurants_list
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _extract_zipcode(self, address):
        """Extract zipcode from address string"""
        if not address:
            return "00000"
        
        # Look for 5-digit zipcode (optionally followed by 4-digit extension)
        zipcode_match = re.search(r'\b(\d{5})(?:-\d{4})?\b', address)
        if zipcode_match:
            return zipcode_match.group(1)
        
        # Fallback for 3-4 digit postal codes (but only if they look like postal codes)
        # Look for patterns at the end of the address
        end_match = re.search(r'\b(\d{3,4})\s*$', address)
        if end_match:
            return end_match.group(1).zfill(5)  # Pad with zeros to 5 digits
        
        # If no numeric postal code found, return default
        return "00000"
    
    def _sanitize_filename(self, filename):
        """Sanitize filename by removing invalid characters"""
        # Handle common cases first
        filename = filename.replace("'s", "s")  # McDonald's -> McDonalds
        filename = filename.replace("'", "")    # Remove other apostrophes
        
        # Remove or replace invalid filename characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces and other characters with underscores
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        # Remove multiple consecutive underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores and limit length
        filename = filename.strip('_')[:50]
        return filename
    
    def _generate_filename_base(self, restaurant=None):
        """Generate a base filename for a single restaurant"""
        if restaurant is None:
            return f"restaurants_{self.timestamp}"
        
        name = restaurant.name or "restaurant"
        zipcode = self._extract_zipcode(restaurant.address)
        base = f"{name}_{zipcode}"
        
        return self._sanitize_filename(base)
    
    def _generate_bulk_filename_base(self):
        """Generate a base filename for bulk export of all restaurants"""
        if not self.restaurants_list:
            return f"restaurants_{self.timestamp}"
        
        if len(self.restaurants_list) == 1:
            return self._generate_filename_base(self.restaurants_list[0])
        else:
            # Multiple restaurants - use first and last restaurant info
            first_restaurant = self.restaurants_list[0]
            last_restaurant = self.restaurants_list[-1]
            
            first_name = (first_restaurant.name or "restaurant").split()[0]  # First word only
            first_zip = self._extract_zipcode(first_restaurant.address)
            
            last_name = (last_restaurant.name or "restaurant").split()[0]  # First word only  
            last_zip = self._extract_zipcode(last_restaurant.address)
            
            if first_zip == last_zip:
                base = f"{first_name}_to_{last_name}_{first_zip}"
            else:
                base = f"{first_name}_{first_zip}_to_{last_name}_{last_zip}"
            
            return self._sanitize_filename(base)
    
    def export_to_excel(self, filename=None, single_file=False):
        """Export restaurant data to Excel format - one file per restaurant by default"""
        if single_file:
            return self._export_to_excel_bulk(filename)
        
        exported_files = []
        for restaurant in self.restaurants_list:
            if filename is None:
                base_name = self._generate_filename_base(restaurant)
                file_name = f"{base_name}.xls"
            else:
                # If specific filename provided, add restaurant identifier
                name_part, ext = filename.rsplit('.', 1) if '.' in filename else (filename, 'xls')
                restaurant_id = self._sanitize_filename(restaurant.name or 'restaurant')[:20]
                file_name = f"{name_part}_{restaurant_id}.{ext}"
            
            filepath = self._export_single_restaurant_to_excel(restaurant, file_name)
            exported_files.append(filepath)
        
        print(f"Exported {len(exported_files)} Excel files")
        return exported_files
    
    def _export_to_excel_bulk(self, filename=None):
        """Export all restaurant data to a single Excel file"""
        if filename is None:
            base_name = self._generate_bulk_filename_base()
            filename = f"{base_name}.xls"
        
        filepath = f"{self.output_folder}{filename}"
        
        writeBook = xlwt.Workbook(encoding='utf-8')
        
        # Create main restaurant info sheet
        self._create_restaurant_sheet(writeBook)
        
        # Create menu items sheet
        self._create_menu_sheet(writeBook)
        
        # Create amenities sheet
        self._create_amenities_sheet(writeBook)
        
        # Create opening hours sheet
        self._create_opening_hours_sheet(writeBook)
        
        # Create about information sheet
        self._create_about_sheet(writeBook)
        
        writeBook.save(filepath)
        print(f"Excel file saved: {filepath}")
        return filepath
    
    def _export_single_restaurant_to_excel(self, restaurant, filename):
        """Export a single restaurant to Excel format"""
        filepath = f"{self.output_folder}{filename}"
        
        writeBook = xlwt.Workbook(encoding='utf-8')
        
        # Create main restaurant info sheet
        self._create_single_restaurant_sheet(writeBook, restaurant)
        
        # Create menu items sheet
        self._create_single_menu_sheet(writeBook, restaurant)
        
        # Create amenities sheet
        self._create_single_amenities_sheet(writeBook, restaurant)
        
        # Create opening hours sheet
        self._create_single_opening_hours_sheet(writeBook, restaurant)
        
        # Create about information sheet
        self._create_single_about_sheet(writeBook, restaurant)
        
        writeBook.save(filepath)
        print(f"Excel file saved: {filepath}")
        return filepath
    
    def _create_restaurant_sheet(self, workbook):
        """Create the main restaurant information sheet"""
        sheet = workbook.add_sheet("Restaurants", cell_overwrite_ok=True)
        
        # Headers
        headers = [
            'SEARCH_KEYWORD', 'NAME', 'CATEGORY', 'ADDRESS', 
            'PHONE', 'WEBSITE', 'RATING', 'OPENING_HOURS', 
            'HAS_ONLINE_MENU', 'MENU_URL', 'TOTAL_MENU_ITEMS', 
            'ABOUT_SECTIONS', 'EXTERNAL_LINKS'
        ]
        
        # Write headers
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # Write data
        for row, restaurant in enumerate(self.restaurants_list, 1):
            col = 0
            sheet.write(row, col, restaurant.keyword); col += 1
            sheet.write(row, col, restaurant.name); col += 1
            sheet.write(row, col, restaurant.category); col += 1
            sheet.write(row, col, restaurant.address); col += 1
            sheet.write(row, col, restaurant.phone); col += 1
            sheet.write(row, col, restaurant.website); col += 1
            sheet.write(row, col, restaurant.rating); col += 1
            
            # Format opening hours
            opening_hours = getattr(restaurant, 'opening_hours', {})
            if opening_hours:
                hours_text = '; '.join([f"{day}: {hours}" for day, hours in opening_hours.items()])
            else:
                hours_text = ''
            sheet.write(row, col, hours_text); col += 1
            
            sheet.write(row, col, 'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No'); col += 1
            sheet.write(row, col, getattr(restaurant, 'menu_url', '')); col += 1
            sheet.write(row, col, len(getattr(restaurant, 'menu_items', []))); col += 1
            
            # Format about sections summary
            about_info = getattr(restaurant, 'about', {})
            if about_info:
                about_sections = list(about_info.keys())
                sheet.write(row, col, '; '.join(about_sections))
            else:
                sheet.write(row, col, '')
            col += 1
            
            # External links
            external_links = getattr(restaurant, 'external_links', [])
            if external_links:
                links_text = '; '.join([f"{link.get('type', 'unknown')}: {link.get('url', '')}" for link in external_links])
                sheet.write(row, col, links_text)
            else:
                sheet.write(row, col, '')
    
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
        headers = ['RESTAURANT_NAME', 'DINING_OPTIONS', 'AMENITIES']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        for row, restaurant in enumerate(self.restaurants_list, 1):
            sheet.write(row, 0, restaurant.name)
            
            # Get dining options from about info
            dining_options = restaurant.get_dining_options() if hasattr(restaurant, 'get_dining_options') else []
            sheet.write(row, 1, '; '.join(dining_options))
            
            # Get amenities from about info
            amenities = restaurant.get_amenities() if hasattr(restaurant, 'get_amenities') else []
            sheet.write(row, 2, '; '.join(amenities))
    
    def _create_opening_hours_sheet(self, workbook):
        """Create the opening hours sheet"""
        sheet = workbook.add_sheet("Opening_Hours", cell_overwrite_ok=True)
        
        # Headers
        headers = ['RESTAURANT_NAME', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        for row, restaurant in enumerate(self.restaurants_list, 1):
            sheet.write(row, 0, restaurant.name)
            
            opening_hours = getattr(restaurant, 'opening_hours', {})
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for col, day in enumerate(days, 1):
                hours = opening_hours.get(day, '')
                sheet.write(row, col, hours)
    
    def _create_about_sheet(self, workbook):
        """Create the about information sheet"""
        sheet = workbook.add_sheet("About_Information", cell_overwrite_ok=True)
        
        # Headers
        headers = ['RESTAURANT_NAME', 'SECTION', 'ITEM', 'AVAILABLE', 'TYPE']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        row = 1
        for restaurant in self.restaurants_list:
            about_info = getattr(restaurant, 'about', {})
            if about_info:
                for section_name, section_data in about_info.items():
                    if isinstance(section_data, list):
                        # Section with items (e.g., amenities, dining options)
                        for item in section_data:
                            sheet.write(row, 0, restaurant.name)
                            sheet.write(row, 1, section_name)
                            sheet.write(row, 2, str(item))
                            sheet.write(row, 3, 'Yes')
                            sheet.write(row, 4, 'Item')
                            row += 1
                    else:
                        # Single value (e.g., description)
                        sheet.write(row, 0, restaurant.name)
                        sheet.write(row, 1, section_name)
                        sheet.write(row, 2, str(section_data))
                        sheet.write(row, 3, 'Yes')
                        sheet.write(row, 4, 'Description')
                        row += 1
            else:
                # Write a row even if no about data to maintain restaurant reference
                sheet.write(row, 0, restaurant.name)
                sheet.write(row, 1, 'No about data available')
                sheet.write(row, 2, '')
                sheet.write(row, 3, '')
                sheet.write(row, 4, '')
                row += 1
    
    def _create_single_restaurant_sheet(self, workbook, restaurant):
        """Create the main restaurant information sheet for a single restaurant"""
        sheet = workbook.add_sheet("Restaurant_Info", cell_overwrite_ok=True)
        
        # Headers
        headers = [
            'SEARCH_KEYWORD', 'NAME', 'CATEGORY', 'ADDRESS', 
            'PHONE', 'WEBSITE', 'RATING', 'OPENING_HOURS', 
            'HAS_ONLINE_MENU', 'MENU_URL', 'TOTAL_MENU_ITEMS', 
            'ABOUT_SECTIONS', 'EXTERNAL_LINKS'
        ]
        
        # Write headers
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # Write data
        col = 0
        sheet.write(1, col, restaurant.keyword); col += 1
        sheet.write(1, col, restaurant.name); col += 1
        sheet.write(1, col, restaurant.category); col += 1
        sheet.write(1, col, restaurant.address); col += 1
        sheet.write(1, col, restaurant.phone); col += 1
        sheet.write(1, col, restaurant.website); col += 1
        sheet.write(1, col, restaurant.rating); col += 1
        
        # Format opening hours
        opening_hours = getattr(restaurant, 'opening_hours', {})
        if opening_hours:
            hours_text = '; '.join([f"{day}: {hours}" for day, hours in opening_hours.items()])
        else:
            hours_text = ''
        sheet.write(1, col, hours_text); col += 1
        
        sheet.write(1, col, 'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No'); col += 1
        sheet.write(1, col, getattr(restaurant, 'menu_url', '')); col += 1
        sheet.write(1, col, len(getattr(restaurant, 'menu_items', []))); col += 1
        
        # Format about sections summary
        about_info = getattr(restaurant, 'about', {})
        if about_info:
            about_sections = list(about_info.keys())
            sheet.write(1, col, '; '.join(about_sections))
        else:
            sheet.write(1, col, '')
        col += 1
        
        # External links
        external_links = getattr(restaurant, 'external_links', [])
        if external_links:
            links_text = '; '.join([f"{link.get('type', 'unknown')}: {link.get('url', '')}" for link in external_links])
            sheet.write(1, col, links_text)
        else:
            sheet.write(1, col, '')
    
    def _create_single_menu_sheet(self, workbook, restaurant):
        """Create the menu items sheet for a single restaurant"""
        sheet = workbook.add_sheet("Menu_Items", cell_overwrite_ok=True)
        
        # Headers
        headers = ['MENU_SECTION', 'ITEM_NAME', 'PRICE', 'DESCRIPTION']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        row = 1
        menu_items = getattr(restaurant, 'menu_items', [])
        if menu_items:
            for item in menu_items:
                sheet.write(row, 0, item.get('section', ''))
                sheet.write(row, 1, item.get('name', ''))
                sheet.write(row, 2, item.get('price', ''))
                sheet.write(row, 3, item.get('description', ''))
                row += 1
        else:
            # Write a row even if no menu items
            sheet.write(row, 0, 'No menu data available')
            sheet.write(row, 1, '')
            sheet.write(row, 2, '')
            sheet.write(row, 3, '')
    
    def _create_single_amenities_sheet(self, workbook, restaurant):
        """Create the amenities and features sheet for a single restaurant"""
        sheet = workbook.add_sheet("Amenities", cell_overwrite_ok=True)
        
        # Headers
        headers = ['DINING_OPTIONS', 'AMENITIES']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # Get dining options from about info
        dining_options = restaurant.get_dining_options() if hasattr(restaurant, 'get_dining_options') else []
        sheet.write(1, 0, '; '.join(dining_options))
        
        # Get amenities from about info
        amenities = restaurant.get_amenities() if hasattr(restaurant, 'get_amenities') else []
        sheet.write(1, 1, '; '.join(amenities))
    
    def _create_single_opening_hours_sheet(self, workbook, restaurant):
        """Create the opening hours sheet for a single restaurant"""
        sheet = workbook.add_sheet("Opening_Hours", cell_overwrite_ok=True)
        
        # Headers
        headers = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        opening_hours = getattr(restaurant, 'opening_hours', {})
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for col, day in enumerate(days):
            hours = opening_hours.get(day, '')
            sheet.write(1, col, hours)
    
    def _create_single_about_sheet(self, workbook, restaurant):
        """Create the about information sheet for a single restaurant"""
        sheet = workbook.add_sheet("About_Information", cell_overwrite_ok=True)
        
        # Headers
        headers = ['SECTION', 'ITEM', 'AVAILABLE', 'TYPE']
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        row = 1
        about_info = getattr(restaurant, 'about', {})
        if about_info:
            for section_name, section_data in about_info.items():
                if isinstance(section_data, list):
                    # Section with items (e.g., amenities, dining options)
                    for item in section_data:
                        sheet.write(row, 0, section_name)
                        sheet.write(row, 1, str(item))
                        sheet.write(row, 2, 'Yes')
                        sheet.write(row, 3, 'Item')
                        row += 1
                else:
                    # Single value (e.g., description)
                    sheet.write(row, 0, section_name)
                    sheet.write(row, 1, str(section_data))
                    sheet.write(row, 2, 'Yes')
                    sheet.write(row, 3, 'Description')
                    row += 1
        else:
            # Write a row even if no about data
            sheet.write(row, 0, 'No about data available')
            sheet.write(row, 1, '')
            sheet.write(row, 2, '')
            sheet.write(row, 3, '')
    
    def export_to_csv(self, filename=None, single_file=False):
        """Export restaurant data to CSV format - one file per restaurant by default"""
        if single_file:
            return self._export_to_csv_bulk(filename)
        
        exported_files = []
        for restaurant in self.restaurants_list:
            if filename is None:
                base_name = self._generate_filename_base(restaurant)
                file_name = f"{base_name}.csv"
            else:
                # If specific filename provided, add restaurant identifier
                name_part, ext = filename.rsplit('.', 1) if '.' in filename else (filename, 'csv')
                restaurant_id = self._sanitize_filename(restaurant.name or 'restaurant')[:20]
                file_name = f"{name_part}_{restaurant_id}.{ext}"
            
            filepath = self._export_single_restaurant_to_csv(restaurant, file_name)
            exported_files.append(filepath)
        
        print(f"Exported {len(exported_files)} CSV files")
        return exported_files
    
    def _export_to_csv_bulk(self, filename=None):
        """Export all restaurant data to a single CSV file"""
        if filename is None:
            base_name = self._generate_bulk_filename_base()
            filename = f"{base_name}.csv"
        
        filepath = f"{self.output_folder}{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            headers = [
                'search_keyword', 'name', 'category', 'address', 
                'phone', 'website', 'rating', 'opening_hours', 'opening_hours_json', 
                'has_online_menu', 'menu_url', 'total_menu_items', 'about_sections', 'about_json', 
                'menu_items_json', 'external_links_json'
            ]
            writer.writerow(headers)
            
            # Data
            for restaurant in self.restaurants_list:
                menu_items_json = json.dumps(getattr(restaurant, 'menu_items', []), ensure_ascii=False)
                opening_hours_json = json.dumps(getattr(restaurant, 'opening_hours', {}), ensure_ascii=False)
                about_json = json.dumps(getattr(restaurant, 'about', {}), ensure_ascii=False)
                external_links_json = json.dumps(getattr(restaurant, 'external_links', []), ensure_ascii=False)
                
                # Format opening hours as readable text
                opening_hours = getattr(restaurant, 'opening_hours', {})
                if opening_hours:
                    hours_text = '; '.join([f"{day}: {hours}" for day, hours in opening_hours.items()])
                else:
                    hours_text = restaurant.hours.replace('\n', '; ') if restaurant.hours else ''
                
                # Format about sections list
                about_info = getattr(restaurant, 'about', {})
                about_sections = '; '.join(about_info.keys()) if about_info else ''
                
                row = [
                    restaurant.keyword,
                    restaurant.name,
                    restaurant.category,
                    restaurant.address,
                    restaurant.phone,
                    restaurant.website,
                    restaurant.rating,
                    hours_text,
                    opening_hours_json,
                    'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No',
                    getattr(restaurant, 'menu_url', ''),
                    len(getattr(restaurant, 'menu_items', [])),
                    about_sections,
                    about_json,
                    menu_items_json,
                    external_links_json
                ]
                writer.writerow(row)
        
        print(f"CSV file saved: {filepath}")
        return filepath
    
    def _export_single_restaurant_to_csv(self, restaurant, filename):
        """Export a single restaurant to CSV format"""
        filepath = f"{self.output_folder}{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            headers = [
                'search_keyword', 'name', 'category', 'address', 
                'phone', 'website', 'rating', 'opening_hours', 'opening_hours_json', 
                'has_online_menu', 'menu_url', 'total_menu_items', 'about_sections', 'about_json', 
                'menu_items_json', 'external_links_json'
            ]
            writer.writerow(headers)
            
            # Data
            menu_items_json = json.dumps(getattr(restaurant, 'menu_items', []), ensure_ascii=False)
            opening_hours_json = json.dumps(getattr(restaurant, 'opening_hours', {}), ensure_ascii=False)
            about_json = json.dumps(getattr(restaurant, 'about', {}), ensure_ascii=False)
            external_links_json = json.dumps(getattr(restaurant, 'external_links', []), ensure_ascii=False)
            
            # Format opening hours as readable text
            opening_hours = getattr(restaurant, 'opening_hours', {})
            if opening_hours:
                hours_text = '; '.join([f"{day}: {hours}" for day, hours in opening_hours.items()])
            else:
                hours_text = restaurant.hours.replace('\n', '; ') if restaurant.hours else ''
            
            # Format about sections list
            about_info = getattr(restaurant, 'about', {})
            about_sections = '; '.join(about_info.keys()) if about_info else ''
            
            row = [
                restaurant.keyword,
                restaurant.name,
                restaurant.category,
                restaurant.address,
                restaurant.phone,
                restaurant.website,
                restaurant.rating,
                hours_text,
                opening_hours_json,
                'Yes' if getattr(restaurant, 'has_online_menu', False) else 'No',
                getattr(restaurant, 'menu_url', ''),
                len(getattr(restaurant, 'menu_items', [])),
                about_sections,
                about_json,
                menu_items_json,
                external_links_json
            ]
            writer.writerow(row)
        
        print(f"CSV file saved: {filepath}")
        return filepath
    
    def export_to_json(self, filename=None, single_file=False):
        """Export restaurant data to JSON format - one file per restaurant by default"""
        if single_file:
            return self._export_to_json_bulk(filename)
        
        exported_files = []
        for restaurant in self.restaurants_list:
            if filename is None:
                base_name = self._generate_filename_base(restaurant)
                file_name = f"{base_name}.json"
            else:
                # If specific filename provided, add restaurant identifier
                name_part, ext = filename.rsplit('.', 1) if '.' in filename else (filename, 'json')
                restaurant_id = self._sanitize_filename(restaurant.name or 'restaurant')[:20]
                file_name = f"{name_part}_{restaurant_id}.{ext}"
            
            filepath = self._export_single_restaurant_to_json(restaurant, file_name)
            exported_files.append(filepath)
        
        print(f"Exported {len(exported_files)} JSON files")
        return exported_files
    
    def _export_to_json_bulk(self, filename=None):
        """Export all restaurant data to a single JSON file"""
        if filename is None:
            base_name = self._generate_bulk_filename_base()
            filename = f"{base_name}.json"
        
        filepath = f"{self.output_folder}{filename}"
        
        restaurants_data = []
        
        for restaurant in self.restaurants_list:
            restaurant_dict = {
                'search_keyword': restaurant.keyword,
                'name': restaurant.name,
                'category': restaurant.category,
                'address': restaurant.address,
                'phone': restaurant.phone,
                'website': restaurant.website,
                'rating': restaurant.rating,
                'opening_hours': getattr(restaurant, 'opening_hours', {}),
                'has_online_menu': getattr(restaurant, 'has_online_menu', False),
                'menu_url': getattr(restaurant, 'menu_url', ''),
                'menu_items': getattr(restaurant, 'menu_items', []),
                'about': getattr(restaurant, 'about', {}),
                'external_links': getattr(restaurant, 'external_links', []),
                'has_menu_photos': getattr(restaurant, 'has_menu_photos', False),
                'menu_photo_urls': getattr(restaurant, 'menu_photo_urls', [])
            }
            restaurants_data.append(restaurant_dict)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(restaurants_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"JSON file saved: {filepath}")
        return filepath
    
    def _export_single_restaurant_to_json(self, restaurant, filename):
        """Export a single restaurant to JSON format"""
        filepath = f"{self.output_folder}{filename}"
        
        restaurant_dict = {
            'search_keyword': restaurant.keyword,
            'name': restaurant.name,
            'category': restaurant.category,
            'address': restaurant.address,
            'phone': restaurant.phone,
            'website': restaurant.website,
            'rating': restaurant.rating,
            'opening_hours': getattr(restaurant, 'opening_hours', {}),
            'has_online_menu': getattr(restaurant, 'has_online_menu', False),
            'menu_url': getattr(restaurant, 'menu_url', ''),
            'menu_items': getattr(restaurant, 'menu_items', []),
            'about': getattr(restaurant, 'about', {}),
            'external_links': getattr(restaurant, 'external_links', []),
            'has_menu_photos': getattr(restaurant, 'has_menu_photos', False),
            'menu_photo_urls': getattr(restaurant, 'menu_photo_urls', [])
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(restaurant_dict, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"JSON file saved: {filepath}")
        return filepath
    
    def export_menu_summary(self, filename=None):
        """Export a summary of menu items across all restaurants"""
        if filename is None:
            base_name = self._generate_bulk_filename_base()
            filename = f"{base_name}_menu_summary.csv"
        
        filepath = f"{self.output_folder}{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            writer.writerow(['restaurant_name', 'total_menu_items', 'menu_sections', 'sample_items'])
            
            for restaurant in self.restaurants_list:
                menu_items = getattr(restaurant, 'menu_items', [])
                about_info = getattr(restaurant, 'about', {})
                
                # Get unique menu sections from menu items
                sections = list(set(item.get('section', '') for item in menu_items if item.get('section')))
                sample_items = [item.get('name', '') for item in menu_items[:5]]  # First 5 items
                
                writer.writerow([
                    restaurant.name,
                    len(menu_items),
                    '; '.join(sections),
                    '; '.join(sample_items)
                ])
        
        print(f"Menu summary saved: {filepath}")
        return filepath
    
    def export_all_formats(self, base_filename=None, single_file=False):
        """Export restaurant data in all formats (Excel, CSV, JSON)"""
        exported_files = {}
        
        # Export Excel
        excel_files = self.export_to_excel(
            f"{base_filename}.xls" if base_filename else None, 
            single_file=single_file
        )
        exported_files['excel'] = excel_files
        
        # Export CSV
        csv_files = self.export_to_csv(
            f"{base_filename}.csv" if base_filename else None, 
            single_file=single_file
        )
        exported_files['csv'] = csv_files
        
        # Export JSON
        json_files = self.export_to_json(
            f"{base_filename}.json" if base_filename else None, 
            single_file=single_file
        )
        exported_files['json'] = json_files
        
        return exported_files
    
    def print_summary(self):
        """Print a summary of the extracted data"""
        total_restaurants = len(self.restaurants_list)
        restaurants_with_menus = sum(1 for r in self.restaurants_list if getattr(r, 'menu_items', []))
        total_menu_items = sum(len(getattr(r, 'menu_items', [])) for r in self.restaurants_list)
        restaurants_with_about = sum(1 for r in self.restaurants_list if getattr(r, 'about', {}))
        
        print(f"\n=== EXTRACTION SUMMARY ===")
        print(f"Total restaurants processed: {total_restaurants}")
        print(f"Restaurants with menu data: {restaurants_with_menus}")
        print(f"Restaurants with about data: {restaurants_with_about}")
        print(f"Total menu items extracted: {total_menu_items}")
        
        if total_restaurants > 0:
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