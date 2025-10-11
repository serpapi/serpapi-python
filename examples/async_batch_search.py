#!/usr/bin/env python3
"""
Async batch search example for SerpApi Python client.

This example demonstrates how to perform multiple searches concurrently
using async/await for better performance.
"""

import asyncio
import os

from serpapi import Client, SerpApiError


async def search_company(client: Client, company: str) -> dict:
    """Search for a specific company."""
    try:
        results = await client.search({"q": company})
        return {
            "company": company,
            "status": results.get("search_metadata", {}).get("status", "Unknown"),
            "search_id": results.get("search_metadata", {}).get("id", "N/A"),
            "organic_count": len(results.get("organic_results", [])),
            "success": True,
        }
    except SerpApiError as e:
        return {"company": company, "error": str(e), "success": False}


async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("Please set SERPAPI_KEY environment variable")
        return

    # Create client with persistent connections for better performance
    client = Client(api_key=api_key, engine="google", persistent=True)

    # List of companies to search
    companies = ["meta", "amazon", "apple", "netflix", "google", "microsoft", "tesla"]

    try:
        print("=== Async Batch Search ===")
        print(f"Searching for {len(companies)} companies concurrently...")
        print()

        # Create tasks for concurrent execution
        tasks = [search_company(client, company) for company in companies]

        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_searches = []
        failed_searches = []

        for result in results:
            if isinstance(result, Exception):
                print(f"Unexpected error: {result}")
                continue

            if result["success"]:
                successful_searches.append(result)
                print(
                    f"✓ {result['company']}: {result['organic_count']} results "
                    f"(Status: {result['status']}, ID: {result['search_id'][:8]}...)"
                )
            else:
                failed_searches.append(result)
                print(f"✗ {result['company']}: {result['error']}")

        print()
        print(
            f"Summary: {len(successful_searches)} successful, {len(failed_searches)} failed"
        )

        # Demonstrate search archive functionality
        if successful_searches:
            print("\n=== Search Archive Example ===")
            first_result = successful_searches[0]
            search_id = first_result["search_id"]

            try:
                archived_result = await client.search_archive(search_id)
                print(f"Retrieved archived result for {first_result['company']}")
                print(
                    f"Archive status: {archived_result.get('search_metadata', {}).get('status', 'Unknown')}"
                )
            except SerpApiError as e:
                print(f"Failed to retrieve archive: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Close the client
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
