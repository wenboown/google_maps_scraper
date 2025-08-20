# -*- coding: utf-8 -*-

"""
Production main script using the focused Google Maps scraper
Priority: 1) Text from Google Maps, 2) Menu photos for OCR, 3) External links
"""

import asyncio
import os
import sys
from threading import Thread
from focused_google_maps_scraper import FocusedGoogleMapsScraper
from restaurant_exporter import RestaurantDataExporter


def split_list(a, n):
    """Split list into n chunks for parallel processing"""
    k, m = divmod(len(a), n)
    return list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))


async def scrape_restaurants_async(restaurant_list, output_folder, thread_id):
    """Async function to scrape restaurants"""
    scraper = FocusedGoogleMapsScraper(output_folder=output_folder, debug=False)
    extracted_restaurants = []
    
    try:
        if not await scraper.init_browser():
            print(f"Thread {thread_id}: Failed to initialize browser")
            return []
        
        for i, search_query in enumerate(restaurant_list):
            print(f"\nThread {thread_id}: Processing {i+1}/{len(restaurant_list)}")
            print(f"Restaurant: {search_query}")
            
            restaurant = await scraper.extract_restaurant_data(search_query)
            
            if restaurant:
                extracted_restaurants.append(restaurant)
                
                # Print summary
                menu_items = len(restaurant.menu_items) if restaurant.menu_items else 0
                menu_photos = len(restaurant.menu_photo_urls) if hasattr(restaurant, 'menu_photo_urls') and restaurant.menu_photo_urls else 0
                external_links = len(restaurant.external_links) if hasattr(restaurant, 'external_links') and restaurant.external_links else 0
                
                print(f"✅ {restaurant.name}")
                print(f"   📋 Menu items: {menu_items}")
                print(f"   📸 Menu photos: {menu_photos}")
                print(f"   🔗 External links: {external_links}")
            else:
                print(f"❌ Failed to extract: {search_query}")
    
    except Exception as e:
        print(f"Thread {thread_id}: Error - {e}")
    
    finally:
        await scraper.close_browser()
    
    return extracted_restaurants


def scrape_restaurants_sync(restaurant_list, output_folder, results, thread_id):
    """Sync wrapper for async scraping"""
    try:
        restaurants = asyncio.run(scrape_restaurants_async(restaurant_list, output_folder, thread_id))
        results[thread_id] = restaurants
    except Exception as e:
        print(f"Thread {thread_id}: Sync wrapper error - {e}")
        results[thread_id] = []


def main_focused_scraper(keywords_file, output_folder, num_threads=2):
    """Main function for focused restaurant scraping"""
    
    # Read keywords file
    try:
        with open(keywords_file, 'r', encoding='utf-8') as file:
            search_queries = [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading keywords file: {e}")
        return
    
    if not search_queries:
        print("No search queries found in the file")
        return
    
    print(f"🏪 FOCUSED GOOGLE MAPS RESTAURANT EXTRACTION")
    print(f"=" * 60)
    print(f"Restaurants to process: {len(search_queries)}")
    print(f"Threads: {num_threads}")
    print(f"Output folder: {output_folder}")
    print(f"Strategy: 1) Google Maps text → 2) Menu photos → 3) External links")
    print("=" * 60)
    
    # Create output folder if needed
    os.makedirs(output_folder, exist_ok=True)
    
    # Split work among threads (use fewer threads for async work)
    divided_lists = split_list(search_queries, num_threads)
    threads = [None] * num_threads
    results = [None] * num_threads
    
    # Start threads
    for i in range(num_threads):
        if divided_lists[i]:  # Only start thread if there are items to process
            threads[i] = Thread(
                target=scrape_restaurants_sync, 
                args=(divided_lists[i], output_folder, results, i)
            )
            threads[i].start()
    
    # Wait for all threads to complete
    for i in range(num_threads):
        if threads[i]:
            threads[i].join()
    
    # Combine results
    all_restaurants = []
    for i in range(num_threads):
        if results[i]:
            all_restaurants.extend(results[i])
    
    if not all_restaurants:
        print("\n❌ No restaurant data was extracted successfully")
        return
    
    print(f"\n" + "=" * 60)
    print("🎉 EXTRACTION COMPLETED! Generating reports...")
    
    # Export data using enhanced exporter
    exporter = RestaurantDataExporter(output_folder, all_restaurants)
    
    # Export in multiple formats
    excel_file = exporter.export_to_excel("focused_extraction_results.xls")
    csv_file = exporter.export_to_csv("focused_extraction_results.csv")
    json_file = exporter.export_to_json("focused_extraction_results.json")
    
    # Print detailed summary
    print_extraction_summary(all_restaurants)
    
    print(f"\n📁 FILES GENERATED:")
    print(f"- Excel: {excel_file}")
    print(f"- CSV: {csv_file}")
    print(f"- JSON: {json_file}")
    print(f"- Menu Photos: {os.path.join(output_folder, 'menu_photos')}")


def print_extraction_summary(restaurants):
    """Print detailed extraction summary"""
    total_restaurants = len(restaurants)
    restaurants_with_menu_text = sum(1 for r in restaurants if r.menu_items)
    restaurants_with_menu_photos = sum(1 for r in restaurants if hasattr(r, 'menu_photo_urls') and r.menu_photo_urls)
    restaurants_with_external_links = sum(1 for r in restaurants if hasattr(r, 'external_links') and r.external_links)
    
    total_menu_items = sum(len(r.menu_items) for r in restaurants if r.menu_items)
    total_menu_photos = sum(len(r.menu_photo_urls) for r in restaurants if hasattr(r, 'menu_photo_urls') and r.menu_photo_urls)
    total_external_links = sum(len(r.external_links) for r in restaurants if hasattr(r, 'external_links') and r.external_links)
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"Total restaurants processed: {total_restaurants}")
    print(f"\n📋 MENU TEXT EXTRACTION:")
    print(f"- Restaurants with menu text: {restaurants_with_menu_text} ({restaurants_with_menu_text/total_restaurants*100:.1f}%)")
    print(f"- Total menu items extracted: {total_menu_items}")
    
    print(f"\n📸 MENU PHOTO EXTRACTION:")
    print(f"- Restaurants with menu photos: {restaurants_with_menu_photos} ({restaurants_with_menu_photos/total_restaurants*100:.1f}%)")
    print(f"- Total menu photos downloaded: {total_menu_photos}")
    
    print(f"\n🔗 EXTERNAL LINKS:")
    print(f"- Restaurants with external links: {restaurants_with_external_links} ({restaurants_with_external_links/total_restaurants*100:.1f}%)")
    print(f"- Total external links collected: {total_external_links}")
    
    print(f"\n🎯 SUCCESS METRICS:")
    success_rate = (restaurants_with_menu_text + restaurants_with_menu_photos + restaurants_with_external_links) / total_restaurants * 100
    print(f"- Overall success rate: {success_rate:.1f}%")
    print(f"  (restaurants with at least one form of menu data)")


def validate_input(prompt, validation_func, error_msg):
    """Helper function to validate user input"""
    while True:
        user_input = input(prompt)
        if validation_func(user_input):
            return user_input
        else:
            print(error_msg)


def create_sample_file():
    """Create a sample keywords file"""
    sample_keywords = [
        "Szechuan Royale, 470 Schooleys Mountain Rd #3, Hackettstown, NJ 07840",
        "Pizza Hut Times Square New York",
        "McDonald's 42nd Street Manhattan",
        "Olive Garden Brooklyn NY",
        "Chipotle Mexican Grill Union Square NYC"
    ]
    
    with open("sample_focused_restaurants.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_keywords))
    
    print(f"Sample keywords file created: sample_focused_restaurants.txt")
    return "sample_focused_restaurants.txt"


def main():
    """Interactive main function"""
    print("🏪 FOCUSED GOOGLE MAPS RESTAURANT SCRAPER")
    print("Strategy: Text → Photos → External Links")
    print("=" * 60)
    
    # Keywords file
    keywords_file = validate_input(
        '\n[1] Restaurant keywords file (.txt) or "sample" to create example: ',
        lambda x: x == "sample" or (os.path.isfile(x) and x.lower().endswith('.txt')),
        "** Error ** File not found or not a .txt file (or type 'sample')"
    )
    
    if keywords_file == "sample":
        keywords_file = create_sample_file()
    
    # Output folder
    output_folder = input('[2] Output folder (default: ./output/): ').strip()
    if not output_folder:
        output_folder = './output/'
    
    # Ensure output folder ends with separator
    if not output_folder.endswith(os.sep):
        output_folder += os.sep
    
    # Number of threads (fewer for async operations)
    num_threads = input('[3] Number of parallel threads (1-3, default 2): ').strip()
    try:
        num_threads = int(num_threads) if num_threads else 2
        if not 1 <= num_threads <= 3:
            num_threads = 2
    except:
        num_threads = 2
    
    print(f"\nConfiguration:")
    print(f"- Keywords file: {keywords_file}")
    print(f"- Output folder: {output_folder}")
    print(f"- Threads: {num_threads}")
    
    confirmation = input("\nStart extraction? (y/n): ")
    if confirmation.lower() != 'y':
        print("Extraction cancelled")
        return
    
    # Start extraction
    main_focused_scraper(keywords_file, output_folder, num_threads)


if __name__ == "__main__":
    main()