# Google Maps Restaurant Scraper 🏪📊

A modern, focused Google Maps scraper built with Python and Playwright. **Specializes in extracting comprehensive restaurant data including menu items, photos, and business information**.

## Key Features

- **🎯 Focused Restaurant Extraction**: Prioritized approach for maximum menu data extraction
- **📋 Menu Text Extraction**: Direct extraction of menu items from Google Maps
- **📸 Menu Photo Download**: Downloads menu photos for future OCR processing  
- **🔗 External Links Collection**: Gathers delivery service links and website URLs
- **📊 Multi-Format Export**: Excel, CSV, and JSON output formats with flexible export options
- **🗂️ Smart File Organization**: One file per restaurant (default) or bulk files (legacy mode)
- **⚡ Fast & Reliable**: Built with modern Playwright for better performance
- **🌐 Multi-threaded**: Parallel processing for faster extraction

## Extraction Strategy

The scraper follows a three-tier priority system:

1. **Priority 1**: Extract menu text directly from Google Maps
2. **Priority 2**: Download menu photos for OCR processing if no text found
3. **Priority 3**: Collect external links (delivery services, websites) as backup

## Quick Start

### Using uv (Recommended)

1. **Install uv** if you haven't already:
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or with pip
   pip install uv
   ```

2. **Run the scraper**:
   ```bash
   # Install dependencies first
   uv sync

   # Basic usage (uses input.txt, creates JSON output)
   uv run python main.py

   # With custom options
   uv run python main.py -i my_restaurants.txt -f excel -t 3

   # See all options
   uv run python main.py -h
   ```

3. **Command Line Options**:
   - `-i/--input`: Input file with restaurant queries (default: `input.txt`)
   - `-o/--output`: Output folder for results (default: `./output/`)
   - `-t/--threads`: Number of parallel threads 1-3 (default: 2)
   - `-f/--format`: Output format - `json`, `csv`, `excel`, or `all` (default: `json`)
   - `--single-file`: Export all restaurants to single files instead of one file per restaurant

### Sample Input Format

Create an input file (default: `input.txt`) with restaurant queries (one per line):
```
Szechuan Royale, 470 Schooleys Mountain Rd #3, Hackettstown, NJ 07840
Pizza Hut Times Square New York
McDonald's 42nd Street Manhattan
Olive Garden Brooklyn NY
```

**Note**: If `input.txt` doesn't exist, the script will automatically create a sample file with example restaurants and provide instructions.

### Usage Examples

```bash
# Basic usage - uses input.txt, outputs JSON (one file per restaurant)
python main.py

# Custom input file with Excel output (one file per restaurant)
python main.py -i my_restaurants.txt -f excel

# All output formats with 3 threads (one file per restaurant)
python main.py -i restaurants.txt -f all -t 3

# Export all restaurants to single files (legacy behavior)
python main.py --single-file -f excel

# Custom output directory
python main.py -o ./my_results/ -f csv

# Get help and see all options
python main.py --help
```

### Output Files

**🆕 NEW: One File Per Restaurant (Default Behavior)**

By default, the scraper now creates **one file per restaurant** for better organization:
- **JSON files**: `RestaurantName_12345.json` - Individual restaurant data
- **Excel files**: `RestaurantName_12345.xls` - Individual restaurant with menu sheets
- **CSV files**: `RestaurantName_12345.csv` - Individual restaurant data
- **All formats**: Use `-f all` to generate all three formats for each restaurant
- **Menu photos**: Always downloaded to `menu_photos/` folder for OCR processing

**Legacy Mode: Single File for All Restaurants**

Use the `--single-file` flag to get the old behavior (all restaurants in one file):
- **JSON file**: `RestaurantName1_12345_to_RestaurantNameN_67890.json`
- **Excel file**: `RestaurantName1_12345_to_RestaurantNameN_67890.xls`
- **CSV file**: `RestaurantName1_12345_to_RestaurantNameN_67890.csv`

**File Naming Convention:**
- Format: `{RestaurantName}_{ZipCode}.{extension}`
- Special characters in restaurant names are automatically sanitized
- Zip codes are extracted from addresses for better organization

## Development Setup

### Modern Python Development with uv

This project uses [uv](https://docs.astral.sh/uv/) for fast dependency management and virtual environments.

```bash
# Clone the repository
git clone <your-repo-url>
cd google_maps_scraper

# Install dependencies
uv sync

# Install Playwright browsers (required for web scraping)
uv run playwright install chromium

# Run the scraper
uv run python main.py

# Or with custom options
uv run python main.py -i restaurants.txt -f excel -t 3
```

### Project Structure

```
google_maps_scraper/
├── focused_google_maps_scraper.py    # Main scraper logic (Playwright-based)
├── main.py                           # Command-line entry point
├── location_maps.py                  # Data models for restaurants
├── restaurant_exporter.py            # Multi-format data export
├── pyproject.toml                    # Modern Python project configuration
├── sample_restaurants.txt           # Example input file
├── output/                          # Generated reports and data
└── menu_photos/                     # Downloaded menu images
```

### Key Components

- **`FocusedGoogleMapsScraper`**: Main scraper class with prioritized extraction
- **`RestaurantMaps`**: Data model for restaurant information and menu items
- **`RestaurantDataExporter`**: Enhanced exporter with one-file-per-restaurant and bulk export modes