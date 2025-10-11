#!/usr/bin/env python3
"""
Basic usage example for SerpApi Python client.

This example demonstrates how to use the SerpApi client for basic search operations.
"""

import asyncio
import os
from serpapi import Client, SerpApiError

async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        print("Please set SERPAPI_KEY environment variable")
        return
    
    # Create client
    client = Client(api_key=api_key, engine="google")
    
    try:
        # Basic search
        print("=== Basic Google Search ===")
        results = await client.search({"q": "coffee"})
        
        if "organic_results" in results:
            print(f"Found {len(results['organic_results'])} organic results:")
            for i, result in enumerate(results["organic_results"][:3], 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   {result.get('link', 'No link')}")
                print()
        else:
            print("No organic results found")
        
        # HTML search
        print("=== HTML Search ===")
        html_content = await client.html({"q": "python programming"})
        print(f"HTML content length: {len(html_content)} characters")
        print(f"First 200 characters: {html_content[:200]}...")
        print()
        
        # Location search
        print("=== Location Search ===")
        locations = await client.location({"q": "Austin", "limit": 3})
        print(f"Found {len(locations)} locations:")
        for location in locations:
            print(f"- {location.get('name', 'No name')} ({location.get('country_code', 'No country')})")
        print()
        
        # Account information
        print("=== Account Information ===")
        account = await client.account()
        print(f"Account ID: {account.get('account_id', 'N/A')}")
        print(f"Plan: {account.get('plan_name', 'N/A')}")
        print(f"Searches left: {account.get('total_searches_left', 'N/A')}")
        
    except SerpApiError as e:
        print(f"SerpApi Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Close the client
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
