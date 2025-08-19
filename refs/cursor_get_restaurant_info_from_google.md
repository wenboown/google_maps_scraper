# Get restaurant info from Google Business
_Exported on 8/2/2025 at 08:43:27 EDT from Cursor (1.3.8)_

---

**User**

how to get the public information about a resturant from their google business page? like food menu items and opening hours? without using google API? we can search and id the specific resturant using name + address or phone number.

---

**Cursor**

I'll help you understand how to get public restaurant information from Google Business pages without using the official Google API. Let me search for information about web scraping techniques and tools that can extract restaurant data.

Based on my research, I can provide you with comprehensive information about extracting public restaurant information from Google Business pages without using the official Google API. Here are the main approaches and considerations:

## Methods to Extract Restaurant Information

### 1. **Web Scraping with Browser Automation**

The most effective approach uses browser automation tools to handle dynamic content:

**Tools to use:**
- **Playwright** (recommended) - Fast, reliable, handles JavaScript well
- **Selenium** - More established but slower
- **Puppeteer** - Good for headless Chrome automation

**Key data you can extract:**
- Restaurant name and address
- Phone number
- Opening hours (usually in structured format)
- Reviews and ratings
- Photos
- Menu information (when available)
- Website links
- Price range indicators

### 2. **Traditional HTTP Scraping**

Using libraries like:
- **BeautifulSoup + Requests** (Python)
- **Scrapy** (Python framework)

However, this is limited because Google Maps relies heavily on JavaScript for dynamic content loading.

### 3. **Finding Restaurants by Search**

You can search for restaurants using:
- **Name + Address**: `"Restaurant Name" + "123 Main St"`
- **Name + Phone**: `"Restaurant Name" + "(555) 123-4567"`
- **Google Maps search URLs**: `https://www.google.com/maps/search/restaurant+name+address`

## Key Technical Considerations

### **Important Limitations:**
1. **Anti-bot protection**: Google has sophisticated detection systems
2. **Dynamic content**: Most data loads via JavaScript
3. **Rate limiting**: Too many requests will get blocked
4. **Changing selectors**: Google frequently updates their HTML structure

### **Best Practices:**
1. **Use delays** between requests (3-5 seconds minimum)
2. **Rotate proxies** for larger operations
3. **Rotate user agents** to appear more human-like
4. **Handle cookies and captchas** appropriately
5. **Cache results** to avoid repeated requests

## Structured Data on Google Business Pages

Google Business pages often include structured data in these formats:

### **Schema.org JSON-LD**
Look for `<script type="application/ld+json">` tags containing:
- `@type: "Restaurant"` or `@type: "LocalBusiness"`
- `openingHours` (in standardized format like "Mo-Fr 09:00-17:00")
- `hasMenu` (menu information when available)
- `aggregateRating` (overall ratings)
- `address` (structured postal address)
- `telephone` (phone number)

### **Opening Hours Format**
Google typically uses this format:
```
"openingHours": [
  "Mo-Fr 09:00-17:00",
  "Sa 10:00-15:00",
  "Su closed"
]
```

## Example Implementation Strategy

1. **Search Phase**: Use Google Maps search to find the restaurant
2. **Extract Business URL**: Get the specific Google Business page URL
3. **Parse Structured Data**: Extract JSON-LD schema data first
4. **Fallback to HTML Parsing**: If structured data isn't available
5. **Data Validation**: Verify extracted information is complete

## Legal and Ethical Considerations

**Important warnings:**
- **Respect robots.txt**: Google's robots.txt may restrict scraping
- **Terms of Service**: This may violate Google's ToS
- **Rate limiting**: Don't overwhelm their servers
- **Use responsibly**: Only for legitimate business purposes
- **Consider alternatives**: Official APIs exist for a reason

## Alternative Approaches

1. **Use existing APIs**: Places API, though it costs money
2. **Third-party services**: Some companies offer restaurant data APIs
3. **Public datasets**: Some cities/regions publish restaurant inspection data
4. **Social media APIs**: Facebook Places, Yelp API, etc.

## Sample Data Structure You Can Extract

```json
{
  "name": "Restaurant Name",
  "address": "123 Main St, City, State ZIP",
  "phone": "(555) 123-4567",
  "hours": {
    "monday": "9:00 AM - 10:00 PM",
    "tuesday": "9:00 AM - 10:00 PM",
    // ... other days
  },
  "rating": 4.5,
  "review_count": 234,
  "price_range": "$$",
  "cuisine_type": "Italian",
  "website": "https://restaurant-website.com",
  "menu_items": [
    // Available when menu data is public
  ]
}
```

The success of extracting this information depends heavily on how the specific restaurant has configured their Google Business profile and what information they've made publicly available.

```plaintext
"openingHours": [
  "Mo-Fr 09:00-17:00",
  "Sa 10:00-15:00",
  "Su closed"
]
```

```json
{
  "name": "Restaurant Name",
  "address": "123 Main St, City, State ZIP",
  "phone": "(555) 123-4567",
  "hours": {
    "monday": "9:00 AM - 10:00 PM",
    "tuesday": "9:00 AM - 10:00 PM",
    // ... other days
  },
  "rating": 4.5,
  "review_count": 234,
  "price_range": "$$",
  "cuisine_type": "Italian",
  "website": "https://restaurant-website.com",
  "menu_items": [
    // Available when menu data is public
  ]
}
```

