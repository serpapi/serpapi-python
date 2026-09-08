---
title: "Examples"
description: "Python search examples grouped by API category."
---

# Examples

Each example makes a search and prints selected fields from the response. Before running one, [install the package and set your API key](../user_guide/getting-started.md#installation).

The examples use `results.get("organic_results", [])` or a similar expression to read a list of results. The empty list `[]` is the default if that section is missing. Within a result, `item.get("title")` returns `None` if the title is missing. A slice such as `[:5]` limits the printed list to its first five items.

Follow the API documentation linked from each example for all supported parameters. The API categories below are also listed in [SerpApi's `llms.txt`](https://serpapi.com/llms.txt).

## Starter Examples

### Search Engines

- [Google Across Countries](google-across-countries.md)
- [Bing Search](bing-search.md)
- [DuckDuckGo Search](duckduckgo-search.md)
- [Baidu Search](baidu-search.md)

### AI Answers

- [Google AI Overview](google-ai-overview.md)

### Local and Maps

- [Google Maps Local Businesses](google-maps-local-business.md)
- [Google Local Services](google-local-services.md)

### Shopping and Marketplaces

- [Google Shopping Products](google-shopping-products.md)
- [Google Shopping Price Monitoring](google-shopping-price-monitoring.md)
- [Amazon Product Search](amazon-product-search.md)
- [Walmart Product Search](walmart-product-search.md)
- [eBay Product Listings](ebay-product-listings.md)
- [Home Depot Product Search](home-depot-product-search.md)

### Travel and Hospitality

- [Google Flights Travel](google-flights-travel.md)
- [Tripadvisor Travel Search](tripadvisor-travel-search.md)

### Finance, Trends, and Jobs

- [Google Finance Market Data](google-finance-market-data.md)
- [Google Trends Demand](google-trends-demand.md)
- [Google News Monitoring](google-news-monitoring.md)
- [Google Jobs Listings](google-jobs-listings.md)

### Media, Apps, and Research

- [YouTube Video Search](youtube-video-search.md)
- [Google Images Search](google-images-search.md)
- [Google Lens Image Upload](google-lens-image-upload.md)
- [Google Scholar Research](google-scholar-research.md)
- [Google Play Store Apps](google-play-store-apps.md)

## Supported API Map

**Search Engines**

- [Google Search API](https://serpapi.com/search-api)
- [Google Light Search API](https://serpapi.com/google-light-api)
- [Bing Search API](https://serpapi.com/bing-search-api)
- [DuckDuckGo Search API](https://serpapi.com/duckduckgo-search-api)
- [DuckDuckGo Light API](https://serpapi.com/duckduckgo-light-api)
- [Baidu Search API](https://serpapi.com/baidu-search-api)
- [Yahoo! Search API](https://serpapi.com/yahoo-search-api)
- [Yandex Search API](https://serpapi.com/yandex-search-api)
- [Naver Search API](https://serpapi.com/naver-search-api)

**AI Answers**

- [Google AI Mode API](https://serpapi.com/google-ai-mode-api)
- [Google AI Overview API](https://serpapi.com/google-ai-overview-api)
- [Bing Copilot API](https://serpapi.com/bing-copilot-api)
- [Brave AI Mode API](https://serpapi.com/brave-ai-mode-api)
- [Naver AI Overview API](https://serpapi.com/naver-ai-overview-api)

**Local and Maps**

- [Google Local API](https://serpapi.com/google-local-api)
- [Google Local Services API](https://serpapi.com/google-local-services-api)
- [Google Maps API](https://serpapi.com/google-maps-api)
- [Google Maps Photos API](https://serpapi.com/google-maps-photos-api)
- [Google Maps Autocomplete API](https://serpapi.com/google-maps-autocomplete-api)
- [Google Maps Directions API](https://serpapi.com/google-maps-directions-api)
- [Google Maps Posts API](https://serpapi.com/google-maps-posts-api)
- [Google Maps Reviews API](https://serpapi.com/google-maps-reviews-api)
- [Google Maps Contributor Reviews API](https://serpapi.com/google-maps-contributor-reviews-api)
- [Apple Maps API](https://serpapi.com/apple-maps-api)
- [Apple Maps Places API](https://serpapi.com/apple-maps-places-api)
- [Bing Maps API](https://serpapi.com/bing-maps-api)
- [DuckDuckGo Maps API](https://serpapi.com/duckduckgo-maps-api)
- [Yelp Search API](https://serpapi.com/yelp-search-api)
- [Yelp Place API](https://serpapi.com/yelp-place)
- [Yelp Reviews API](https://serpapi.com/yelp-reviews-api)

**Shopping and Marketplaces**

- [Google Shopping API](https://serpapi.com/google-shopping-api)
- [Google Shopping Light API](https://serpapi.com/google-shopping-light-api)
- [Google Immersive Product API](https://serpapi.com/google-immersive-product-api)
- [Amazon Search API](https://serpapi.com/amazon-search-api)
- [Amazon Product API](https://serpapi.com/amazon-product-api)
- [Walmart Search API](https://serpapi.com/walmart-search-api)
- [Walmart Product API](https://serpapi.com/walmart-product-api)
- [Walmart Reviews API](https://serpapi.com/walmart-product-reviews-api)
- [eBay Search API](https://serpapi.com/ebay-search-api)
- [eBay Product API](https://serpapi.com/ebay-product-api)
- [The Home Depot Search API](https://serpapi.com/home-depot-search-api)
- [The Home Depot Product API](https://serpapi.com/home-depot-product)
- [The Home Depot Reviews API](https://serpapi.com/home-depot-product-reviews)
- [Bing Shopping API](https://serpapi.com/bing-shopping-api)
- [Bing Product API](https://serpapi.com/bing-product-api)
- [Yahoo! Shopping API](https://serpapi.com/yahoo-shopping-search-api)

**Travel and Hospitality**

- [Google Flights API](https://serpapi.com/google-flights-api)
- [Google Flights Autocomplete API](https://serpapi.com/google-flights-autocomplete-api)
- [Google Flights Deals API](https://serpapi.com/google-flights-deals-api)
- [Google Hotels API](https://serpapi.com/google-hotels-api)
- [Google Hotels Autocomplete API](https://serpapi.com/google-hotels-autocomplete-api)
- [Google Hotels Photos API](https://serpapi.com/google-hotels-photos-api)
- [Google Hotels Reviews API](https://serpapi.com/google-hotels-reviews-api)
- [Google Travel Explore API](https://serpapi.com/google-travel-explore-api)
- [Tripadvisor Search API](https://serpapi.com/tripadvisor-search-api)
- [Tripadvisor Place API](https://serpapi.com/tripadvisor-place-api)
- [Tripadvisor Reviews API](https://serpapi.com/tripadvisor-reviews-api)
- [OpenTable Reviews API](https://serpapi.com/open-table-reviews-api)

**News, Trends, and Demand**

- [Google News API](https://serpapi.com/google-news-api)
- [Google News Light API](https://serpapi.com/google-news-light-api)
- [Bing News API](https://serpapi.com/bing-news-api)
- [DuckDuckGo News API](https://serpapi.com/duckduckgo-news-api)
- [Baidu News API](https://serpapi.com/baidu-news-api)
- [Google Trends API](https://serpapi.com/google-trends-api)
- [Google Trends Autocomplete API](https://serpapi.com/google-trends-autocomplete)
- [Google Trends Trending Now API](https://serpapi.com/google-trends-trending-now)
- [Google Sports API](https://serpapi.com/google-sports-api)
- [Google Forums API](https://serpapi.com/google-forums-api)

**Media, Apps, and Social**

- [Google Images API](https://serpapi.com/google-images-api)
- [Google Images Light API](https://serpapi.com/google-images-light-api)
- [Google Lens API](https://serpapi.com/google-lens-api)
- [Google Reverse Image API](https://serpapi.com/google-reverse-image)
- [Google Videos API](https://serpapi.com/google-videos-api)
- [Google Videos Light API](https://serpapi.com/google-videos-light-api)
- [Google Short Videos API](https://serpapi.com/google-short-videos-api)
- [Bing Images API](https://serpapi.com/bing-images-api)
- [Bing Reverse Image API](https://serpapi.com/bing-reverse-image-api)
- [Bing Videos API](https://serpapi.com/bing-videos-api)
- [Yahoo! Images API](https://serpapi.com/yahoo-images-api)
- [Yahoo! Videos API](https://serpapi.com/yahoo-videos-api)
- [Yandex Images API](https://serpapi.com/yandex-images-api)
- [Yandex Videos API](https://serpapi.com/yandex-videos-api)
- [YouTube Search API](https://serpapi.com/youtube-search-api)
- [YouTube Video API](https://serpapi.com/youtube-video-api)
- [YouTube Video Transcript API](https://serpapi.com/youtube-video-transcript)
- [Apple App Store API](https://serpapi.com/apple-app-store)
- [Apple App Store Reviews API](https://serpapi.com/apple-reviews)
- [Apple App Store Product API](https://serpapi.com/apple-product)
- [Google Play Store API](https://serpapi.com/google-play-api)
- [Google Play Games API](https://serpapi.com/google-play-games)
- [Google Play Movies API](https://serpapi.com/google-play-movies)
- [Google Play Books API](https://serpapi.com/google-play-books)
- [Google Play Product API](https://serpapi.com/google-play-product-api)
- [Facebook Profile API](https://serpapi.com/facebook-profile-api)
- [Instagram Profile API](https://serpapi.com/instagram-profile-api)

**Research, Knowledge, Ads, Finance, and Jobs**

- [Google Scholar API](https://serpapi.com/google-scholar-api)
- [Google Scholar Author API](https://serpapi.com/google-scholar-author-api)
- [Google Scholar Case Law API](https://serpapi.com/google-scholar-case-law-api)
- [Google Patents API](https://serpapi.com/google-patents-api)
- [Google Patents Details API](https://serpapi.com/google-patents-details-api)
- [Google Related Questions API](https://serpapi.com/google-related-questions-api)
- [Google Autocomplete API](https://serpapi.com/google-autocomplete-api)
- [Google Ads API](https://serpapi.com/google-ads-api)
- [Google Ads Transparency API](https://serpapi.com/google-ads-transparency-center-api)
- [Google Finance API](https://serpapi.com/google-finance-api)
- [Google Finance Markets API](https://serpapi.com/google-finance-markets)
- [Google Jobs API](https://serpapi.com/google-jobs-api)

```{toctree}
:hidden:
:maxdepth: 2

categories/search-engines
categories/ai-answers
categories/local-and-maps
categories/shopping-and-marketplaces
categories/travel-and-hospitality
categories/finance-trends-and-jobs
categories/media-apps-and-research
```
