# -*- coding: utf-8 -*-

import json
import re
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from maps_data_scraper import GoogleMapsDataScraper
from lugar_maps import RestaurantMaps


class RestaurantDataScraper(GoogleMapsDataScraper):
    """Enhanced scraper specifically for restaurant data including menu items"""
    
    def __init__(self, idioma, imgOutput):
        super().__init__(idioma, imgOutput)
        # Add restaurant-specific configuration
        self.menu_selectors = {
            'menu_button': [
                '//button[contains(text(), "Menu")]',
                '//button[contains(text(), "Menú")]',
                '//a[contains(@data-value, "Menu")]',
                '//div[contains(text(), "Menu") and @role="button"]'
            ],
            'menu_items': [
                '//div[contains(@class, "menu")]//div[contains(@class, "item")]',
                '//div[@data-section-id]//div[contains(@class, "name")]',
                '.menu-item',
                '[data-item-id]'
            ],
            'menu_sections': [
                '//div[contains(@class, "section-header")]',
                '//h3[contains(@class, "menu")]',
                '.menu-section-header'
            ]
        }
    
    def scrapear_restaurant_data(self, search_query):
        """Enhanced scraping specifically for restaurants"""
        try:
            restaurant = RestaurantMaps()
            restaurant.keyword = search_query
            
            # Perform initial search and basic data extraction
            if not self._perform_search(search_query):
                return None
            
            if not self.isLoaded(search_query):
                return None
            
            # Extract basic information (using parent class methods)
            self._extract_basic_info(restaurant)
            
            # Extract restaurant-specific information
            self._extract_restaurant_specific_info(restaurant)
            
            # Extract structured data (JSON-LD)
            self._extract_structured_data(restaurant)
            
            # Try to extract menu information
            self._extract_menu_information(restaurant)
            
            # Extract additional business details
            self._extract_additional_details(restaurant)
            
            return restaurant
            
        except Exception as e:
            print(f"Error scraping restaurant data: {e}")
            self.errorCont += 1
            return None
    
    def _perform_search(self, search_query):
        """Perform search with better error handling"""
        try:
            if self.errorCont == 5:
                self.errorCont = 0
                time.sleep(1)
                self.driver.get('https://www.google.com/maps/')
                time.sleep(2)
            
            time.sleep(random.randint(1, 3))
            inputBox = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]'))
            )
            inputBox.click()
            inputBox.clear()
            inputBox.click()
            time.sleep(1)
            inputBox.send_keys(search_query)
            time.sleep(1)
            inputBox.send_keys(Keys.ENTER)
            time.sleep(4)
            
            return True
        except Exception as e:
            print(f"Error performing search: {e}")
            return False
    
    def _extract_basic_info(self, restaurant):
        """Extract basic business information"""
        try:
            # Get the main content div
            divImg = self.driver.find_element(By.XPATH, '//*[@id="pane"]/following-sibling::div')
            
            # Restaurant name
            try:
                titulo = divImg.find_element(By.TAG_NAME, 'h1').text
                restaurant.nombre = titulo
            except:
                restaurant.nombre = ''
            
            # Rating and reviews
            try:
                val = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "' +
                                                    self.configuracion['textoEstrellas'] + '") and @role="img"]'))
                )
                if '(' in val.text and ')' in val.text:
                    dividido = val.text.replace(')', '').split('(')
                    restaurant.estrellas = dividido[0]
                    restaurant.resenas = dividido[1]
                else:
                    valoraciones = val.get_attribute("aria-label")
                    restaurant.estrellas = valoraciones.replace(self.configuracion['textoEstrellas'], '').replace(' ', '')
                    
                    val = self.driver.find_element(By.XPATH, '//*[contains(@aria-label, "' + self.configuracion['textoReviews'] + '")]')
                    valoraciones = val.get_attribute("aria-label")
                    restaurant.resenas = valoraciones.replace(self.configuracion['textoReviews'], '').replace(' ', '')
            except:
                pass
            
            # Category
            try:
                restaurant.categoria = self.buscar_xpath('//button[contains(@jsaction, "pane.") and contains(@jsaction, ".category")]')
            except:
                restaurant.categoria = ''
            
            # Address
            try:
                direccion_label = self.driver.find_element(
                    By.XPATH, '//*[contains(@aria-label, "' + self.configuracion['textoDireccion'] + '")]'
                ).get_attribute('aria-label')
                restaurant.direccion = direccion_label.replace(self.configuracion['textoDireccion'], "").strip()
            except:
                restaurant.direccion = ''
            
            # Website
            try:
                web_label = self.driver.find_element(
                    By.XPATH, '//*[contains(@aria-label, "' + self.configuracion['textoWeb'] + '")]'
                ).get_attribute('aria-label')
                restaurant.web = web_label.replace(self.configuracion['textoWeb'], "").strip()
            except:
                restaurant.web = ''
            
            # Phone
            try:
                telefono_label = self.driver.find_element(
                    By.XPATH, '//*[contains(@aria-label, "' + self.configuracion['textoTelefono'] + '")]'
                ).get_attribute('aria-label')
                restaurant.telefono = telefono_label.replace(self.configuracion['textoTelefono'], "").strip()
            except:
                restaurant.telefono = ''
            
            # Plus code
            try:
                pluscode_label = self.driver.find_element(
                    By.XPATH, '//*[contains(@aria-label, "' + self.configuracion['textoPlusCode'] + '")]'
                ).get_attribute('aria-label')
                restaurant.pluscode = pluscode_label.replace(self.configuracion['textoPlusCode'], "").strip()
            except:
                restaurant.pluscode = ''
            
            # Hours
            restaurant.horario = self.getHorario()
            
        except Exception as e:
            print(f"Error extracting basic info: {e}")
    
    def _extract_restaurant_specific_info(self, restaurant):
        """Extract restaurant-specific information"""
        try:
            # Price range - look for $ symbols
            try:
                price_elements = self.driver.find_elements(By.XPATH, '//*[contains(text(), "$") and string-length(text()) <= 10]')
                for element in price_elements:
                    text = element.text.strip()
                    if text in ['$', '$$', '$$$', '$$$$']:
                        restaurant.price_range = text
                        break
                    # Also check for "Inexpensive", "Moderate", "Expensive", etc.
                    if any(word in text.lower() for word in ['inexpensive', 'moderate', 'expensive', 'cheap', 'costly']):
                        restaurant.price_range = text
                        break
            except:
                pass
            
            # Cuisine type - often in category or nearby text
            try:
                # Try to find cuisine type from category or nearby elements
                category_elements = self.driver.find_elements(By.XPATH, '//button[contains(@jsaction, "category")]')
                for element in category_elements:
                    text = element.text.lower()
                    cuisines = ['italian', 'mexican', 'chinese', 'indian', 'thai', 'japanese', 'french', 'american', 
                               'mediterranean', 'greek', 'spanish', 'korean', 'vietnamese', 'pizza', 'burger', 'seafood']
                    for cuisine in cuisines:
                        if cuisine in text:
                            restaurant.cuisine_type = cuisine.capitalize()
                            break
            except:
                pass
            
            # Dining options - look for delivery, takeout, dine-in indicators
            try:
                dining_indicators = self.driver.find_elements(By.XPATH, '//*[contains(text(), "Dine-in") or contains(text(), "Takeout") or contains(text(), "Delivery") or contains(text(), "Drive-through")]')
                for element in dining_indicators:
                    text = element.text.lower()
                    if 'dine-in' in text or 'dine in' in text:
                        restaurant.dining_options.append('Dine-in')
                    if 'takeout' in text or 'take-out' in text:
                        restaurant.dining_options.append('Takeout')
                    if 'delivery' in text:
                        restaurant.dining_options.append('Delivery')
                    if 'drive-through' in text or 'drive through' in text:
                        restaurant.dining_options.append('Drive-through')
            except:
                pass
            
        except Exception as e:
            print(f"Error extracting restaurant-specific info: {e}")
    
    def _extract_structured_data(self, restaurant):
        """Extract JSON-LD structured data"""
        try:
            # Look for JSON-LD structured data
            script_elements = self.driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
            
            for script in script_elements:
                try:
                    json_content = script.get_attribute('innerHTML')
                    data = json.loads(json_content)
                    
                    # Handle both single objects and arrays
                    if isinstance(data, list):
                        data = data[0] if data else {}
                    
                    # Extract restaurant/business data
                    if data.get('@type') in ['Restaurant', 'LocalBusiness', 'FoodEstablishment']:
                        # Opening hours
                        if 'openingHours' in data and not restaurant.horario:
                            restaurant.horario = '\n'.join(data['openingHours'])
                        
                        # Price range
                        if 'priceRange' in data and not restaurant.price_range:
                            restaurant.price_range = data['priceRange']
                        
                        # Cuisine
                        if 'servesCuisine' in data and not restaurant.cuisine_type:
                            if isinstance(data['servesCuisine'], list):
                                restaurant.cuisine_type = ', '.join(data['servesCuisine'])
                            else:
                                restaurant.cuisine_type = data['servesCuisine']
                        
                        # Menu information
                        if 'hasMenu' in data:
                            menu_data = data['hasMenu']
                            if isinstance(menu_data, dict) and 'url' in menu_data:
                                restaurant.menu_url = menu_data['url']
                                restaurant.has_online_menu = True
                        
                        break
                        
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error parsing JSON-LD: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting structured data: {e}")
    
    def _extract_menu_information(self, restaurant):
        """Extract menu information using multiple strategies"""
        try:
            # Strategy 1: Look for menu button and click it
            menu_found = False
            for selector in self.menu_selectors['menu_button']:
                try:
                    menu_button = self.driver.find_element(By.XPATH, selector)
                    if menu_button and menu_button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", menu_button)
                        time.sleep(3)
                        menu_found = True
                        break
                except:
                    continue
            
            if menu_found:
                self._extract_menu_items_from_page(restaurant)
            
            # Strategy 2: Look for menu in the overview/about section
            if not restaurant.menu_items:
                self._extract_menu_from_overview(restaurant)
            
            # Strategy 3: Check for menu images in photos
            if not restaurant.menu_items:
                self._extract_menu_from_photos(restaurant)
                
        except Exception as e:
            print(f"Error extracting menu information: {e}")
    
    def _extract_menu_items_from_page(self, restaurant):
        """Extract menu items from dedicated menu page/section"""
        try:
            # Look for menu sections first
            section_elements = []
            for selector in self.menu_selectors['menu_sections']:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    section_elements.extend(elements)
                except:
                    continue
            
            # Extract menu items
            item_elements = []
            for selector in self.menu_selectors['menu_items']:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    item_elements.extend(elements)
                except:
                    continue
            
            # Process menu sections
            current_section = "General"
            for section in section_elements:
                try:
                    section_name = section.text.strip()
                    if section_name:
                        restaurant.add_menu_section(section_name)
                        current_section = section_name
                except:
                    continue
            
            # Process menu items
            for item in item_elements:
                try:
                    item_text = item.text.strip()
                    if item_text and len(item_text) > 0:
                        # Try to extract price from item text
                        price_match = re.search(r'\$[\d,]+\.?\d*', item_text)
                        price = price_match.group() if price_match else ''
                        
                        # Clean item name (remove price)
                        item_name = re.sub(r'\$[\d,]+\.?\d*', '', item_text).strip()
                        
                        if item_name:
                            restaurant.add_menu_item(item_name, price, '', current_section)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error extracting menu items from page: {e}")
    
    def _extract_menu_from_overview(self, restaurant):
        """Look for menu information in the overview section"""
        try:
            # Scroll through the overview to find menu-related content
            overview_content = self.driver.find_elements(By.XPATH, '//div[contains(@class, "section")]//span[contains(text(), "menu") or contains(text(), "Menu")]')
            
            for content in overview_content:
                try:
                    parent = content.find_element(By.XPATH, './..')
                    text = parent.text
                    
                    # Look for menu items mentioned in text
                    lines = text.split('\n')
                    for line in lines:
                        # Simple heuristic: lines with $ are likely menu items
                        if '$' in line and len(line) < 100:
                            price_match = re.search(r'\$[\d,]+\.?\d*', line)
                            price = price_match.group() if price_match else ''
                            item_name = re.sub(r'\$[\d,]+\.?\d*', '', line).strip()
                            
                            if item_name:
                                restaurant.add_menu_item(item_name, price, '', 'Overview')
                                
                except:
                    continue
                    
        except Exception as e:
            print(f"Error extracting menu from overview: {e}")
    
    def _extract_menu_from_photos(self, restaurant):
        """Check if there are menu photos and note their existence"""
        try:
            # Look for photos button
            photos_button = self.driver.find_elements(By.XPATH, '//button[contains(text(), "Photos") or contains(text(), "Fotos")]')
            
            if photos_button:
                # For now, just note that menu photos might be available
                # Full OCR extraction would require additional libraries
                restaurant.has_online_menu = True
                
        except Exception as e:
            print(f"Error checking menu photos: {e}")
    
    def _extract_additional_details(self, restaurant):
        """Extract additional restaurant details"""
        try:
            # Look for amenities/features
            amenity_keywords = ['wifi', 'parking', 'wheelchair', 'outdoor', 'reservation', 'credit card', 'cash only']
            
            # Search in all text content for amenities
            all_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            for keyword in amenity_keywords:
                if keyword in all_text:
                    restaurant.amenities.append(keyword.replace('_', ' ').title())
            
            # Popular times - look for busy hours information
            try:
                popular_elements = self.driver.find_elements(By.XPATH, '//*[contains(text(), "popular") or contains(text(), "busy") or contains(text(), "peak")]')
                for element in popular_elements:
                    text = element.text
                    if len(text) < 200:  # Avoid getting too much text
                        restaurant.popular_times = text
                        break
            except:
                pass
                
        except Exception as e:
            print(f"Error extracting additional details: {e}")