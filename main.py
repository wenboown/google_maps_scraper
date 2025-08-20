# -*- coding: utf-8 -*-

"""
Production main script using the focused Google Maps scraper
Priority: 1) Text from Google Maps, 2) Menu photos for OCR, 3) External links
"""

import argparse
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


def main_focused_scraper(keywords_file, output_folder, num_threads=2, output_format='json', single_file=False):
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
    print(f"Export mode: {'Single file per restaurant' if not single_file else 'All restaurants in one file'}")
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
    
    # Export based on format selection
    generated_files = {}
    
    if output_format == 'json' or output_format == 'all':
        json_files = exporter.export_to_json(single_file=single_file)
        generated_files['JSON'] = json_files if isinstance(json_files, list) else [json_files]
    
    if output_format == 'csv' or output_format == 'all':
        csv_files = exporter.export_to_csv(single_file=single_file)
        generated_files['CSV'] = csv_files if isinstance(csv_files, list) else [csv_files]
    
    if output_format == 'excel' or output_format == 'all':
        excel_files = exporter.export_to_excel(single_file=single_file)
        generated_files['Excel'] = excel_files if isinstance(excel_files, list) else [excel_files]
    
    # Print detailed summary
    print_extraction_summary(all_restaurants)
    
    # Print files generated
    if single_file:
        print(f"\n📁 FILES GENERATED (All restaurants in single files):")
        total_files = 0
        for format_name, file_list in generated_files.items():
            for filepath in file_list:
                filename = os.path.basename(filepath)
                print(f"- {format_name}: {filename}")
                total_files += 1
    else:
        print(f"\n📁 FILES GENERATED (One file per restaurant):")
        total_files = 0
        for format_name, file_list in generated_files.items():
            print(f"- {format_name}: {len(file_list)} files")
            total_files += len(file_list)
            # Show first few filenames as examples
            for i, filepath in enumerate(file_list[:3]):
                filename = os.path.basename(filepath)
                print(f"  └─ {filename}")
            if len(file_list) > 3:
                print(f"  └─ ... and {len(file_list) - 3} more files")
    
    print(f"- Menu Photos: {os.path.join(output_folder, 'menu_photos')}")
    print(f"\n🎯 Total files created: {total_files} restaurant files")


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



def create_sample_file(filename="sample_input.txt"):
    """Create a sample keywords file"""
    sample_keywords = [
        "Pizza Hut Times Square New York",
        "McDonald's 42nd Street Manhattan",
        "Olive Garden Brooklyn NY",
        "Chipotle Mexican Grill Union Square NYC"
    ]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_keywords))
    
    print(f"Sample keywords file created: {filename}")
    print(f"Please edit '{filename}' with your restaurant search queries (one per line)")
    print("Each line should contain restaurant name and location for best results")
    return filename


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="🏪 FOCUSED GOOGLE MAPS RESTAURANT SCRAPER\nStrategy: Text → Photos → External Links",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        default='input.txt',
        help='Input file containing restaurant search queries (default: input.txt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./output/',
        help='Output folder for results (default: ./output/)'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=2,
        choices=range(1, 4),
        metavar='{1,2,3}',
        help='Number of parallel threads (1-3, default: 2)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'csv', 'excel', 'all'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--single-file',
        action='store_true',
        help='Export all restaurants to single files instead of one file per restaurant (default: one file per restaurant)'
    )
    
    return parser.parse_args()


def main():
    """Main function with argparse"""
    args = parse_arguments()
    
    print("🏪 FOCUSED GOOGLE MAPS RESTAURANT SCRAPER")
    print("Strategy: Text → Photos → External Links")
    print("=" * 60)
    
    # Handle input file
    if not os.path.isfile(args.input):
        print(f"Input file '{args.input}' not found.")
        create_sample_file(args.input)
        print(f"\nPlease run the script again after editing sample file '{args.input}'")
        return
    
    # Ensure output folder ends with separator
    output_folder = args.output
    if not output_folder.endswith(os.sep):
        output_folder += os.sep
    
    print(f"\nConfiguration:")
    print(f"- Input file: {args.input}")
    print(f"- Output folder: {output_folder}")
    print(f"- Threads: {args.threads}")
    print(f"- Output format: {args.format}")
    print(f"- Export mode: {'Single file per restaurant' if not args.single_file else 'All restaurants in one file'}")
    print()
    
    # Start extraction
    main_focused_scraper(args.input, output_folder, args.threads, args.format, args.single_file)


if __name__ == "__main__":
    main()