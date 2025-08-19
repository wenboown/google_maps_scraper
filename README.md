# Google Maps Restaurant Scraper 🏪📊

A modern, focused Google Maps scraper built with Python and Playwright. **Specializes in extracting comprehensive restaurant data including menu items, photos, and business information**.

## Key Features

- **🎯 Focused Restaurant Extraction**: Prioritized approach for maximum menu data extraction
- **📋 Menu Text Extraction**: Direct extraction of menu items from Google Maps
- **📸 Menu Photo Download**: Downloads menu photos for future OCR processing  
- **🔗 External Links Collection**: Gathers delivery service links and website URLs
- **📊 Multi-Format Export**: Excel, CSV, and JSON output formats
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

   # Then run
   uv run python main.py
   ```

3. **Follow the prompts**:
   - **[1] Restaurant keywords file**: Provide a .txt file with restaurant queries (one per line)
   - **[2] Output folder**: Specify where to save results (default: `./output/`)
   - **[3] Number of threads**: Choose 1-3 parallel threads (default: 2)

### Sample Input Format

Create a text file (e.g., `restaurants.txt`) with restaurant queries:
```
Szechuan Royale, 470 Schooleys Mountain Rd #3, Hackettstown, NJ 07840
Pizza Hut Times Square New York
McDonald's 42nd Street Manhattan
Olive Garden Brooklyn NY
```

### Output Files

The scraper generates:
- **Excel file**: `focused_extraction_results.xls` - Full restaurant data with menu items
- **CSV file**: `focused_extraction_results.csv` - Structured data export  
- **JSON file**: `focused_extraction_results.json` - Complete data in JSON format
- **Menu photos**: Downloaded to `menu_photos/` folder for OCR processing

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
```

### Project Structure

```
google_maps_scraper/
├── focused_google_maps_scraper.py    # Main scraper logic (Playwright-based)
├── main.py                           # Interactive entry point
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
- **`RestaurantDataExporter`**: Handles Excel, CSV, and JSON export formats

### Alternative Setup (Traditional)

If you prefer traditional Python virtual environments:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate
# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install playwright requests xlwt

# Install browsers
playwright install chromium

# Run scraper
python main.py
```

## Tutorial article and video

For any doubts about how to use the program, you can read the article of our web or see the demo video.

- Explanatory article: https://juaristech.com/google-maps-scraper
- Demo video: https://youtu.be/XX-u-eNkRFs

## Contact

- Website: [JuarisTech](https://juaristech.com/)
- Email: admin@juaristech.com

