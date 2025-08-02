# -*- coding: utf-8 -*-

import os
import sys
from threading import Thread
from restaurant_scraper import RestaurantDataScraper
from restaurant_exporter import RestaurantDataExporter


def split_list(a, n):
    """Split list into n chunks for parallel processing"""
    k, m = divmod(len(a), n)
    return list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))


def scrape_restaurants(idioma, restaurant_list, output_folder, results, thread_id):
    """Scrape restaurant data in a thread"""
    scraper = RestaurantDataScraper(idioma, output_folder)
    
    if not scraper.initDriver():
        print(f"Thread {thread_id}: Failed to initialize driver")
        results[thread_id] = []
        return
    
    extracted_restaurants = []
    
    try:
        for i, search_query in enumerate(restaurant_list):
            print(f"Thread {thread_id}: Processing {i+1}/{len(restaurant_list)} - {search_query}")
            
            restaurant = scraper.scrapear_restaurant_data(search_query)
            
            if restaurant:
                extracted_restaurants.append(restaurant)
                menu_count = len(getattr(restaurant, 'menu_items', []))
                print(f"Thread {thread_id}: ✓ {search_query} - {menu_count} menu items")
            else:
                print(f"Thread {thread_id}: ✗ {search_query} - Failed")
    
    except Exception as e:
        print(f"Thread {thread_id}: Error - {e}")
    
    finally:
        results[thread_id] = extracted_restaurants
        scraper.endDriver()


def main_restaurant_scraper(idioma, keywords_file, output_folder, num_threads=3):
    """Main function for restaurant scraping"""
    
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
    
    print(f"Starting restaurant data extraction for {len(search_queries)} restaurants...")
    print(f"Using {num_threads} threads")
    print("=" * 50)
    
    # Split work among threads
    divided_lists = split_list(search_queries, num_threads)
    threads = [None] * num_threads
    results = [None] * num_threads
    
    # Start threads
    for i in range(num_threads):
        if divided_lists[i]:  # Only start thread if there are items to process
            threads[i] = Thread(
                target=scrape_restaurants, 
                args=(idioma, divided_lists[i], output_folder, results, i)
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
        print("No restaurant data was extracted successfully")
        return
    
    print("\n" + "=" * 50)
    print("Extraction completed! Exporting data...")
    
    # Export data
    exporter = RestaurantDataExporter(output_folder, all_restaurants)
    
    # Export in multiple formats
    excel_file = exporter.export_to_excel()
    csv_file = exporter.export_to_csv()
    json_file = exporter.export_to_json()
    menu_summary = exporter.export_menu_summary()
    
    # Print summary
    exporter.print_summary()
    
    print(f"\nFiles exported:")
    print(f"- Excel: {excel_file}")
    print(f"- CSV: {csv_file}")
    print(f"- JSON: {json_file}")
    print(f"- Menu Summary: {menu_summary}")


def validate_input(prompt, validation_func, error_msg):
    """Helper function to validate user input"""
    while True:
        user_input = input(prompt)
        if validation_func(user_input):
            return user_input
        else:
            print(error_msg)


def main():
    """Interactive main function"""
    print("=" * 60)
    print("    RESTAURANT DATA EXTRACTOR")
    print("    Enhanced Google Maps Scraper for Restaurants")
    print("=" * 60)
    print()
    
    # Language selection
    idioma = validate_input(
        '[1] Language (ES or EN): ',
        lambda x: x.upper() in ['ES', 'EN'],
        "** Error ** Please enter 'ES' for Spanish or 'EN' for English"
    ).upper()
    
    # Output folder
    output_folder = validate_input(
        '[2] Output folder path: ',
        lambda x: os.path.isdir(x) or os.path.isdir(os.path.dirname(x)),
        "** Error ** Invalid folder path"
    )
    
    # Ensure output folder ends with separator
    if not output_folder.endswith(os.sep):
        output_folder += os.sep
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Keywords file
    keywords_file = validate_input(
        '[3] Restaurant keywords file (.txt): ',
        lambda x: os.path.isfile(x) and x.lower().endswith('.txt'),
        "** Error ** File not found or not a .txt file"
    )
    
    # Number of threads
    num_threads = validate_input(
        '[4] Number of parallel threads (1-5, default 3): ',
        lambda x: x.isdigit() and 1 <= int(x) <= 5 if x else True,
        "** Error ** Enter a number between 1 and 5"
    )
    num_threads = int(num_threads) if num_threads else 3
    
    print(f"\nConfiguration:")
    print(f"- Language: {idioma}")
    print(f"- Output folder: {output_folder}")
    print(f"- Keywords file: {keywords_file}")
    print(f"- Threads: {num_threads}")
    
    confirmation = input("\nProceed with extraction? (y/n): ")
    if confirmation.lower() != 'y':
        print("Extraction cancelled")
        return
    
    # Start extraction
    main_restaurant_scraper(idioma, keywords_file, output_folder, num_threads)


def create_sample_keywords_file():
    """Create a sample keywords file for testing"""
    sample_file = "sample_restaurants.txt"
    sample_keywords = [
        "Pizza Hut New York",
        "McDonald's Times Square",
        "Starbucks Manhattan",
        "Chipotle Brooklyn",
        "Olive Garden Queens",
        "KFC Bronx",
        "Subway sandwiches Manhattan",
        "Domino's Pizza Brooklyn",
        "Burger King NYC",
        "Taco Bell New York"
    ]
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_keywords))
    
    print(f"Sample keywords file created: {sample_file}")
    return sample_file


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_keywords_file()
    else:
        main()