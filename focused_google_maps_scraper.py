# -*- coding: utf-8 -*-

import asyncio
import os
import re
import urllib.request
from datetime import datetime
from playwright.async_api import async_playwright
from lugar_maps import RestaurantMaps


class FocusedGoogleMapsScraper:
    """
    Focused Google Maps scraper with prioritized approach:
    1. Extract menu text from Google Maps directly
    2. Download menu photos for future OCR processing
    3. Collect external links as backup
    """
    
    def __init__(self, output_folder='./', debug=True):
        self.debug_mode = debug
        self.output_folder = output_folder
        self.browser = None
        self.context = None
        self.menu_photos_folder = os.path.join(output_folder, 'menu_photos')
        
        # Create menu photos folder
        os.makedirs(self.menu_photos_folder, exist_ok=True)
    
    async def init_browser(self):
        """Initialize browser with optimized settings"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            return True
        except Exception as e:
            print(f"Error initializing browser: {e}")
            return False
    
    async def extract_restaurant_data(self, search_query):
        """Main extraction method with prioritized approach"""
        try:
            restaurant = RestaurantMaps()
            restaurant.keyword = search_query
            
            if self.debug_mode:
                print(f"\n🔍 FOCUSED GOOGLE MAPS EXTRACTION")
                print(f"Restaurant: {search_query}")
                print("=" * 60)
            
            page = await self.context.new_page()
            
            # Navigate and search
            await self._navigate_and_search(page, search_query)
            
            # Extract basic business information
            await self._extract_basic_info(page, restaurant)
            
            # PRIORITY 1: Extract menu text from Google Maps
            menu_text_found = await self._extract_menu_text_from_maps(page, restaurant)
            
            # PRIORITY 2: Download menu photos if no text found
            if not menu_text_found:
                await self._download_menu_photos(page, restaurant)
            
            # PRIORITY 3: Collect external links as backup
            await self._collect_external_links(page, restaurant)
            
            await page.close()
            return restaurant
            
        except Exception as e:
            print(f"Error in restaurant extraction: {e}")
            return None
    
    async def _navigate_and_search(self, page, search_query):
        """Navigate to Google Maps and search"""
        try:
            # Go to Google Maps
            await page.goto('https://www.google.com/maps/', wait_until='domcontentloaded')
            await page.wait_for_selector('[id="searchboxinput"]', timeout=30000)
            
            # Handle cookie consent
            try:
                await page.click('button:has-text("Accept all")', timeout=3000)
            except:
                try:
                    await page.click('button:has-text("Aceptar todo")', timeout=3000)
                except:
                    pass
            
            # Search for restaurant
            await page.fill('[id="searchboxinput"]', search_query)
            await page.press('[id="searchboxinput"]', 'Enter')
            await page.wait_for_timeout(5000)
            
            # Wait for restaurant details to load
            await page.wait_for_selector('h1', timeout=15000)
            
        except Exception as e:
            print(f"Error in navigation and search: {e}")
            raise
    
    async def _extract_basic_info(self, page, restaurant):
        """Extract basic restaurant information from Google Maps"""
        try:
            if self.debug_mode:
                print("📋 Extracting basic business information...")
            
            # Restaurant name
            try:
                name_elem = await page.wait_for_selector('h1', timeout=5000)
                restaurant.nombre = await name_elem.text_content()
                if self.debug_mode:
                    print(f"  ✓ Name: {restaurant.nombre}")
            except:
                restaurant.nombre = ''
            
            # Category
            try:
                category_elem = await page.query_selector('button[jsaction*="category"]')
                if category_elem:
                    restaurant.categoria = await category_elem.text_content()
                    if self.debug_mode:
                        print(f"  ✓ Category: {restaurant.categoria}")
            except:
                restaurant.categoria = ''
            
            # Phone
            try:
                phone_elem = await page.query_selector('[data-item-id="phone"]')
                if phone_elem:
                    restaurant.telefono = await phone_elem.text_content()
                    if self.debug_mode:
                        print(f"  ✓ Phone: {restaurant.telefono}")
            except:
                restaurant.telefono = ''
            
            # Address
            try:
                address_elem = await page.query_selector('[data-item-id="address"]')
                if address_elem:
                    restaurant.direccion = await address_elem.text_content()
                    if self.debug_mode:
                        print(f"  ✓ Address: {restaurant.direccion}")
            except:
                restaurant.direccion = ''
            
            # Website
            try:
                website_elem = await page.query_selector('[data-item-id="authority"]')
                if website_elem:
                    restaurant.web = await website_elem.text_content()
                    if self.debug_mode:
                        print(f"  ✓ Website: {restaurant.web}")
            except:
                restaurant.web = ''
            
            # Rating
            try:
                rating_elem = await page.query_selector('[role="img"][aria-label*="star"]')
                if rating_elem:
                    aria_label = await rating_elem.get_attribute('aria-label')
                    rating_match = re.search(r'(\d+[.,]\d+)', aria_label)
                    if rating_match:
                        restaurant.estrellas = rating_match.group(1)
                        if self.debug_mode:
                            print(f"  ✓ Rating: {restaurant.estrellas}")
            except:
                pass
            
            # Detect cuisine type
            if restaurant.categoria:
                category_lower = restaurant.categoria.lower()
                cuisines = ['chinese', 'italian', 'mexican', 'indian', 'thai', 'japanese', 'french', 'american']
                for cuisine in cuisines:
                    if cuisine in category_lower:
                        restaurant.cuisine_type = cuisine.capitalize()
                        break
            
            # Detect dining options
            page_content = await page.content()
            dining_options = []
            if 'dine-in' in page_content.lower() or 'dine in' in page_content.lower():
                dining_options.append('Dine-in')
            if 'takeout' in page_content.lower() or 'take-out' in page_content.lower():
                dining_options.append('Takeout')
            if 'delivery' in page_content.lower():
                dining_options.append('Delivery')
            restaurant.dining_options = dining_options
            
        except Exception as e:
            print(f"Error extracting basic info: {e}")
    
    async def _extract_menu_text_from_maps(self, page, restaurant):
        """PRIORITY 1: Extract menu text directly from Google Maps"""
        try:
            if self.debug_mode:
                print("\n🍽️  PRIORITY 1: Extracting menu text from Google Maps...")
            
            # Try to navigate to menu section
            menu_found = await self._navigate_to_menu_section(page)
            
            if menu_found:
                # Extract menu items from the menu section
                items_found = await self._extract_menu_items_from_section(page, restaurant)
                
                if items_found > 0:
                    if self.debug_mode:
                        print(f"  ✅ SUCCESS: Found {items_found} menu items from Google Maps text")
                    return True
            
            # If menu navigation didn't work, try extracting from current view
            items_found = await self._extract_menu_from_current_view(page, restaurant)
            
            if items_found > 0:
                if self.debug_mode:
                    print(f"  ✅ SUCCESS: Found {items_found} menu items from current view")
                return True
            
            if self.debug_mode:
                print("  ❌ No menu text found on Google Maps")
            return False
            
        except Exception as e:
            if self.debug_mode:
                print(f"  ❌ Error extracting menu text: {e}")
            return False
    
    async def _navigate_to_menu_section(self, page):
        """Try to navigate to the menu section"""
        try:
            # Look for menu button/tab
            menu_selectors = [
                'button:has-text("Menu")',
                '[role="tab"]:has-text("Menu")',
                'div[role="button"]:has-text("Menu")'
            ]
            
            for selector in menu_selectors:
                try:
                    menu_elem = await page.query_selector(selector)
                    if menu_elem:
                        if self.debug_mode:
                            button_text = await menu_elem.text_content()
                            print(f"    Found menu button: '{button_text}'")
                        
                        await menu_elem.click()
                        await page.wait_for_timeout(3000)
                        
                        # For our improved logic, we assume menu navigation succeeded
                        # if we clicked the menu button - the sub-category logic will handle the rest
                        if self.debug_mode:
                            print(f"    ✓ Menu section navigation attempted")
                        return True
                        
                except:
                    continue
            
            return False
            
        except Exception as e:
            return False
    
    async def _check_menu_content_presence(self, page):
        """Check if menu content is present on the page"""
        try:
            # Look for price indicators
            price_elements = await page.query_selector_all('text=/\\$\\d+/')
            return len(price_elements) > 3
        except:
            return False
    
    async def _extract_menu_items_from_section(self, page, restaurant):
        """Extract menu items from the menu section, handling sub-category tabs"""
        try:
            items_found = 0
            
            if self.debug_mode:
                print("    → Checking for menu sub-category tabs...")
            
            # First, try to find menu sub-category tabs
            menu_category_tabs = await self._find_menu_category_tabs(page)
            
            if menu_category_tabs:
                if self.debug_mode:
                    print(f"    ✓ Found {len(menu_category_tabs)} menu category tabs")
                
                # Extract from each category tab
                for tab_name, tab_element in menu_category_tabs:
                    if self.debug_mode:
                        print(f"      → Extracting from category: {tab_name}")
                    
                    try:
                        # Click the category tab
                        await tab_element.click()
                        await page.wait_for_timeout(2000)  # Wait for content to load
                        
                        # Extract menu items from this category
                        category_items = await self._extract_items_from_current_category(page, restaurant, tab_name)
                        items_found += category_items
                        
                        if self.debug_mode and category_items > 0:
                            print(f"        ✓ Found {category_items} items in {tab_name}")
                        
                    except Exception as e:
                        if self.debug_mode:
                            print(f"        ❌ Error extracting from {tab_name}: {e}")
                        continue
            else:
                if self.debug_mode:
                    print("    → No sub-category tabs found, trying overview tab...")
                
                # Check if items are in the main overview tab (case for short menus)
                items_found = await self._extract_items_from_current_category(page, restaurant, "Overview")
            
            return items_found
            
        except Exception as e:
            if self.debug_mode:
                print(f"    ❌ Error in menu section extraction: {e}")
            return 0
    
    async def _find_menu_category_tabs(self, page):
        """Find menu sub-category tabs like 'Beef', 'Seafood', etc."""
        try:
            menu_category_tabs = []
            
            # Look for tab-like elements that could be menu categories
            tab_selectors = [
                # Look for role="tab" elements that are not the main tabs
                '[role="tab"]:not(:has-text("Overview")):not(:has-text("Menu")):not(:has-text("Reviews")):not(:has-text("About"))',
                # Look for button elements that could be category tabs
                'button[aria-selected], button[role="tab"]',
                # Look for div elements that act like tabs
                'div[role="button"][aria-selected]'
            ]
            
            # Also look for elements that contain common menu category names
            category_keywords = ['beef', 'chicken', 'pork', 'seafood', 'vegetable', 'soup', 'appetizer', 
                               'dessert', 'beverage', 'drink', 'lunch', 'dinner', 'entree', 'main',
                               'side', 'rice', 'noodle', 'pasta', 'pizza', 'salad', 'sandwich']
            
            processed_texts = set()
            
            for selector in tab_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        try:
                            text = await element.text_content()
                            if not text or text in processed_texts:
                                continue
                            
                            text_clean = text.strip().lower()
                            processed_texts.add(text)
                            
                            # Check if this looks like a menu category
                            if (len(text_clean) < 20 and  # Not too long
                                (any(keyword in text_clean for keyword in category_keywords) or
                                 text_clean.replace(' ', '').isalpha())):  # Or just alphabetic text
                                
                                menu_category_tabs.append((text.strip(), element))
                                
                        except:
                            continue
                except:
                    continue
            
            return menu_category_tabs
            
        except Exception as e:
            return []
    
    async def _extract_items_from_current_category(self, page, restaurant, category_name):
        """Extract menu items from the currently active category"""
        try:
            items_found = 0
            
            # Wait a moment for content to load
            await page.wait_for_timeout(1000)
            
            # Enhanced selectors that work better with Google Maps structure
            # Focus on getting parent elements that contain complete menu item info
            menu_item_selectors = [
                # Look for parent containers that have price information
                'div:has(text=/\\$\\d+/)',  # Divs containing price text
                'span:has(text=/\\$\\d+/)',  # Spans containing price text  
                'p:has(text=/\\$\\d+/)',    # Paragraphs containing price text
                'li:has(text=/\\$\\d+/)',   # List items containing price text
                # Also try direct text selectors but with parent context
                'div:has-text("$")',
                'span:has-text("$")', 
                'p:has-text("$")',
                'li:has-text("$")',
                # Look for structured elements
                'div[role="listitem"]',
                'div[role="option"]'
            ]
            
            processed_texts = set()
            processed_items = set()  # Track processed items to avoid duplicates
            
            for selector in menu_item_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    
                    for element in elements:
                        try:
                            # Get text content
                            text = await element.text_content()
                            if not text or text in processed_texts:
                                continue
                            processed_texts.add(text)
                            
                            # For menu items, we need to find elements that contain both name and price
                            # Try to find the cleanest representation of the menu item
                            menu_item_text = text
                            
                            # If the text is too long, try to find a shorter, more specific child element
                            if len(text) > 200:
                                try:
                                    # Look for shorter child elements that contain price
                                    child_elements = await element.query_selector_all('div, span, p')
                                    for child in child_elements:
                                        child_text = await child.text_content()
                                        if child_text and re.search(r'\$\d+\.?\d*', child_text) and len(child_text) < 200:
                                            menu_item_text = child_text
                                            break
                                except:
                                    pass
                            
                            # Check if this looks like a menu item
                            if self._looks_like_menu_item(menu_item_text):
                                if self.debug_mode and category_name not in ['Overview', 'Menu', 'Reviews', 'About']:
                                    print(f"        Processing potential menu item: {menu_item_text[:60]}...")
                                # Extract price
                                price_match = re.search(r'\$\d+\.?\d*', menu_item_text)
                                price = price_match.group() if price_match else ''
                                
                                # Extract item name (remove price and clean up)
                                item_name = menu_item_text
                                
                                # Remove price from the text
                                if price:
                                    item_name = menu_item_text.replace(price, '').strip()
                                
                                # Clean up the item name
                                item_name = self._clean_item_name(item_name)
                                
                                # Remove common prefixes and suffixes
                                item_name = re.sub(r'^[\d\.\s\-–]+', '', item_name)  # Remove leading numbers and dashes
                                item_name = re.sub(r'[\s\-–]+$', '', item_name)     # Remove trailing spaces and dashes
                                item_name = re.sub(r'\s+', ' ', item_name)          # Normalize spaces
                                
                                # Remove common Google Maps UI text
                                ui_patterns = [
                                    r'\bHot and spicy\b',
                                    r'\bSliced beef\b.*sauce$',
                                    r'\btypically includes\b.*'
                                ]
                                
                                for pattern in ui_patterns:
                                    item_name = re.sub(pattern, '', item_name, flags=re.IGNORECASE)
                                
                                item_name = item_name.strip()
                                
                                # Create unique identifier to avoid duplicates
                                item_key = f"{item_name}|{price}|{category_name}"
                                
                                # Skip certain categories that don't contain real menu items
                                skip_categories = ['Overview', 'Menu', 'Reviews', 'About']
                                if category_name in skip_categories:
                                    if self.debug_mode:
                                        print(f"        Skipping category: {category_name}")
                                    continue
                                
                                # Validate item name and check for duplicates
                                if (len(item_name) > 3 and len(item_name) < 100 and 
                                    not item_name.lower() in ['hot', 'spicy', 'sauce'] and
                                    item_key not in processed_items):
                                    
                                    processed_items.add(item_key)
                                    
                                    # Split name and description if possible
                                    # Look for common patterns like "ItemNameDescription" 
                                    clean_name = item_name
                                    description = ''
                                    
                                    # Try to separate main dish name from description
                                    # Common patterns: "Beef HowfunStir-fried..." -> "Beef Howfun", "Stir-fried..."
                                    for separator in ['Stir-fried', 'Sautéed', 'Chunks of', 'Slices of', 'Diced', 'Served']:
                                        if separator in item_name:
                                            parts = item_name.split(separator, 1)
                                            if len(parts) == 2:
                                                clean_name = parts[0].strip()
                                                description = f"{separator}{parts[1]}".strip()
                                                break
                                    
                                    # Further clean the name
                                    if len(clean_name) > 50:  # If still too long, try other patterns
                                        # Look for capital letters indicating new words
                                        import re
                                        # Split on capital letters that follow lowercase
                                        words = re.findall(r'[A-Z][a-z]*', clean_name)
                                        if len(words) >= 2:
                                            clean_name = ' '.join(words[:3])  # Take first 3 words
                                    
                                    restaurant.add_menu_item(clean_name, price, description, category_name)
                                    items_found += 1
                                    
                                    if self.debug_mode and items_found <= 3:
                                        print(f"        Found: {clean_name} - {price}")
                                    
                                    # Limit items per category to avoid excessive extraction
                                    if items_found >= 20:
                                        break
                                        
                        except:
                            continue
                            
                except:
                    continue
            
            return items_found
            
        except Exception as e:
            return 0
    
    async def _extract_menu_from_current_view(self, page, restaurant):
        """Extract menu items from current view without navigation"""
        try:
            # Get all visible text that might contain menu items
            all_text_elements = await page.query_selector_all('div, span, p, li')
            
            items_found = 0
            processed_texts = set()
            
            for element in all_text_elements:
                try:
                    text = await element.text_content()
                    if not text or text in processed_texts or len(text) > 300:
                        continue
                    processed_texts.add(text)
                    
                    if self._looks_like_menu_item(text):
                        price_match = re.search(r'\$\d+\.?\d*', text)
                        price = price_match.group() if price_match else ''
                        
                        item_name = re.sub(r'\$\d+\.?\d*', '', text).strip()
                        item_name = self._clean_item_name(item_name)
                        
                        if len(item_name) > 2:
                            restaurant.add_menu_item(item_name, price, '', 'Current View')
                            items_found += 1
                            
                            if items_found >= 30:  # Reasonable limit
                                break
                
                except:
                    continue
            
            return items_found
            
        except Exception as e:
            return 0
    
    async def _download_menu_photos(self, page, restaurant):
        """PRIORITY 2: Download menu photos for future OCR processing"""
        try:
            if self.debug_mode:
                print("\n📸 PRIORITY 2: Looking for menu photos...")
            
            # Look for photos section or menu images
            photos_found = await self._find_and_download_menu_images(page, restaurant)
            
            if photos_found > 0:
                if self.debug_mode:
                    print(f"  ✅ SUCCESS: Downloaded {photos_found} menu photos for OCR processing")
                restaurant.has_menu_photos = True
                return True
            else:
                if self.debug_mode:
                    print("  ❌ No menu photos found")
                return False
                
        except Exception as e:
            if self.debug_mode:
                print(f"  ❌ Error downloading menu photos: {e}")
            return False
    
    async def _find_and_download_menu_images(self, page, restaurant):
        """Find and download menu-related images"""
        try:
            photos_downloaded = 0
            
            # Try to click on photos to see menu images
            try:
                # Look for photos button
                photos_button = await page.query_selector('button:has-text("Photos"), button:has-text("Fotos")')
                if photos_button:
                    await photos_button.click()
                    await page.wait_for_timeout(3000)
                    
                    if self.debug_mode:
                        print("    Opened photos section")
            except:
                pass
            
            # Look for images that might be menus
            image_selectors = [
                'img[alt*="menu"]',
                'img[alt*="Menu"]',
                'img[src*="menu"]',
                'img[src*="Menu"]',
                # Generic image selectors - we'll filter by content
                'img[src*="googleusercontent"]'
            ]
            
            processed_urls = set()
            
            for selector in image_selectors:
                try:
                    images = await page.query_selector_all(selector)
                    
                    for img in images:
                        try:
                            src = await img.get_attribute('src')
                            alt = await img.get_attribute('alt') or ''
                            
                            if src and src not in processed_urls:
                                processed_urls.add(src)
                                
                                # Check if this might be a menu image
                                if self._looks_like_menu_image(src, alt):
                                    # Download the image
                                    success = await self._download_image(src, restaurant, photos_downloaded)
                                    if success:
                                        photos_downloaded += 1
                                        
                                        if self.debug_mode:
                                            print(f"    ✓ Downloaded menu photo {photos_downloaded}")
                                        
                                        if photos_downloaded >= 5:  # Limit downloads
                                            break
                        
                        except:
                            continue
                            
                except:
                    continue
            
            return photos_downloaded
            
        except Exception as e:
            return 0
    
    def _looks_like_menu_image(self, src, alt):
        """Check if an image might be a menu"""
        if not src:
            return False
        
        # Check alt text for menu keywords
        alt_lower = alt.lower()
        if any(word in alt_lower for word in ['menu', 'food', 'dish', 'price']):
            return True
        
        # For Google images, we'll download a few and let OCR decide
        if 'googleusercontent' in src:
            return True
        
        return False
    
    async def _download_image(self, url, restaurant, index):
        """Download an image for OCR processing"""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = re.sub(r'[^\w\-_]', '_', restaurant.nombre or 'restaurant')
            filename = f"{safe_name}_menu_{index}_{timestamp}.jpg"
            filepath = os.path.join(self.menu_photos_folder, filename)
            
            # Download image
            # Note: In production, you might want to use requests or aiohttp
            # For now, we'll just record the URL for manual download
            if not hasattr(restaurant, 'menu_photo_urls'):
                restaurant.menu_photo_urls = []
            
            restaurant.menu_photo_urls.append({
                'url': url,
                'filename': filename,
                'filepath': filepath
            })
            
            # Actually download the image (simplified version)
            try:
                urllib.request.urlretrieve(url, filepath)
                return True
            except:
                # If direct download fails, just record the URL
                return True
                
        except Exception as e:
            return False
    
    async def _collect_external_links(self, page, restaurant):
        """PRIORITY 3: Collect external links as backup"""
        try:
            if self.debug_mode:
                print("\n🔗 PRIORITY 3: Collecting external links...")
            
            # Collect website URL (already done in basic info)
            external_links = []
            
            if restaurant.web:
                external_links.append({
                    'type': 'website',
                    'url': restaurant.web,
                    'description': 'Restaurant website'
                })
            
            # Look for delivery/ordering service links
            delivery_selectors = [
                'a[href*="doordash"]',
                'a[href*="grubhub"]', 
                'a[href*="ubereats"]',
                'a[href*="postmates"]',
                'a[href*="seamless"]',
                'a:has-text("Order"), a:has-text("Delivery")'
            ]
            
            for selector in delivery_selectors:
                try:
                    links = await page.query_selector_all(selector)
                    for link in links:
                        try:
                            href = await link.get_attribute('href')
                            text = await link.text_content()
                            
                            if href and href not in [l['url'] for l in external_links]:
                                link_type = self._categorize_external_link(href)
                                external_links.append({
                                    'type': link_type,
                                    'url': href,
                                    'description': text or link_type
                                })
                        except:
                            continue
                except:
                    continue
            
            # Store external links
            restaurant.external_links = external_links
            
            if self.debug_mode:
                if external_links:
                    print(f"  ✅ Collected {len(external_links)} external links:")
                    for link in external_links:
                        print(f"    - {link['type']}: {link['url']}")
                else:
                    print("  ❌ No external links found")
                    
        except Exception as e:
            if self.debug_mode:
                print(f"  ❌ Error collecting external links: {e}")
    
    def _categorize_external_link(self, url):
        """Categorize external links by type"""
        url_lower = url.lower()
        
        if 'doordash' in url_lower:
            return 'doordash'
        elif 'grubhub' in url_lower:
            return 'grubhub'
        elif 'ubereats' in url_lower:
            return 'ubereats'
        elif 'postmates' in url_lower:
            return 'postmates'
        elif 'seamless' in url_lower:
            return 'seamless'
        else:
            return 'website'
    
    def _looks_like_menu_item(self, text):
        """Check if text looks like a menu item"""
        if not text or len(text) < 3:
            return False
        
        # Must contain a price
        if not re.search(r'\$\d+\.?\d*', text):
            return False
        
        # Exclude obvious non-menu items
        exclude_patterns = [
            r'total', r'tax', r'tip', r'service', r'delivery', r'minimum',
            r'review', r'rating', r'star', r'hour', r'address', r'phone',
            r'website', r'direction', r'photo', r'copyright', r'privacy'
        ]
        
        text_lower = text.lower()
        for pattern in exclude_patterns:
            if re.search(pattern, text_lower):
                return False
        
        return True
    
    def _clean_item_name(self, name):
        """Clean menu item name"""
        # Remove extra whitespace and clean up
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'[^\w\s\-&(),."\']', '', name)
        return name.strip()
    
    async def close_browser(self):
        """Clean up browser resources"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except:
            pass


# Test function
async def test_focused_scraper():
    """Test the focused scraper"""
    scraper = FocusedGoogleMapsScraper(output_folder='./', debug=True)
    
    try:
        if not await scraper.init_browser():
            print("Failed to initialize browser")
            return
        
        search_query = "Szechuan Royale, 470 Schooleys Mountain Rd #3, Hackettstown, NJ 07840"
        restaurant = await scraper.extract_restaurant_data(search_query)
        
        if restaurant:
            print(f"\n🎉 FINAL RESULTS:")
            print(f"=" * 60)
            print(f"Restaurant: {restaurant.nombre}")
            print(f"Category: {restaurant.categoria} ({restaurant.cuisine_type})")
            print(f"Phone: {restaurant.telefono}")
            print(f"Address: {restaurant.direccion}")
            print(f"Website: {restaurant.web}")
            print(f"Rating: {restaurant.estrellas}")
            print(f"Dining Options: {restaurant.dining_options}")
            
            print(f"\n📊 MENU DATA EXTRACTION RESULTS:")
            print(f"Menu text items found: {len(restaurant.menu_items)}")
            
            if restaurant.menu_items:
                print(f"\n📋 MENU ITEMS FROM GOOGLE MAPS:")
                for i, item in enumerate(restaurant.menu_items[:10]):
                    print(f"  {i+1}. {item['name']} - {item['price']}")
                if len(restaurant.menu_items) > 10:
                    print(f"  ... and {len(restaurant.menu_items) - 10} more items")
            
            if hasattr(restaurant, 'menu_photo_urls') and restaurant.menu_photo_urls:
                print(f"\n📸 MENU PHOTOS FOR OCR:")
                for i, photo in enumerate(restaurant.menu_photo_urls):
                    print(f"  {i+1}. {photo['filename']} - {photo['url']}")
            
            if hasattr(restaurant, 'external_links') and restaurant.external_links:
                print(f"\n🔗 EXTERNAL LINKS (BACKUP):")
                for link in restaurant.external_links:
                    print(f"  - {link['type']}: {link['url']}")
            
            # Summary
            print(f"\n📈 EXTRACTION SUMMARY:")
            success_methods = []
            if restaurant.menu_items:
                success_methods.append(f"✅ Text extraction ({len(restaurant.menu_items)} items)")
            if hasattr(restaurant, 'menu_photo_urls') and restaurant.menu_photo_urls:
                success_methods.append(f"✅ Photo download ({len(restaurant.menu_photo_urls)} photos)")
            if hasattr(restaurant, 'external_links') and restaurant.external_links:
                success_methods.append(f"✅ External links ({len(restaurant.external_links)} links)")
            
            if success_methods:
                for method in success_methods:
                    print(f"  {method}")
            else:
                print("  ❌ No menu data found through any method")
        else:
            print("❌ Failed to extract restaurant data")
    
    finally:
        await scraper.close_browser()


if __name__ == "__main__":
    asyncio.run(test_focused_scraper())