#!/usr/bin/env python3
"""
Multiple search engines example for SerpApi Python client.

This example demonstrates how to use different search engines
and compare their results.
"""

import asyncio
import os
from serpapi import Client, SerpApiError


async def search_with_engine(client: Client, engine: str, query: str) -> dict:
    """Search using a specific engine."""
    try:
        results = await client.search({"engine": engine, "q": query})
        return {
            "engine": engine,
            "query": query,
            "status": results.get("search_metadata", {}).get("status", "Unknown"),
            "organic_count": len(results.get("organic_results", [])),
            "total_results": results.get("search_information", {}).get("total_results", "N/A"),
            "success": True,
            "results": results.get("organic_results", [])[:3]  # First 3 results
        }
    except SerpApiError as e:
        return {
            "engine": engine,
            "query": query,
            "error": str(e),
            "success": False
        }


async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        print("Please set SERPAPI_KEY environment variable")
        return
    
    # Create client
    client = Client(api_key=api_key, persistent=True)
    
    # Search query
    query = "artificial intelligence"
    
    # Different search engines to try
    engines = [
        "google",
        "bing", 
        "yahoo",
        "duckduckgo",
        "baidu"
    ]
    
    try:
        print(f"=== Multi-Engine Search: '{query}' ===")
        print(f"Searching with {len(engines)} different engines...")
        print()
        
        # Create tasks for concurrent execution
        tasks = [search_with_engine(client, engine, query) for engine in engines]
        
        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process and display results
        for result in results:
            if isinstance(result, Exception):
                print(f"Unexpected error: {result}")
                continue
                
            print(f"--- {result['engine'].upper()} ---")
            
            if result["success"]:
                print(f"Status: {result['status']}")
                print(f"Organic results: {result['organic_count']}")
                print(f"Total results: {result['total_results']}")
                
                if result["results"]:
                    print("Top results:")
                    for i, res in enumerate(result["results"], 1):
                        title = res.get("title", "No title")
                        link = res.get("link", "No link")
                        print(f"  {i}. {title}")
                        print(f"     {link}")
                else:
                    print("No organic results found")
            else:
                print(f"Error: {result['error']}")
            
            print()
        
        # Compare results across engines
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        if len(successful_results) > 1:
            print("=== Comparison Summary ===")
            for result in successful_results:
                print(f"{result['engine']}: {result['organic_count']} organic results")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Close the client
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
