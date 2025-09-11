#!/usr/bin/env python3
"""
Utility script to decode/process Google News URLs from CSV files
"""
import csv
import sys
import os
from urllib.parse import urlparse
import argparse
from src.scrapers.url_resolver import resolve_google_news_url

def process_csv_file(input_file: str, output_file: str, url_column: str = 'link'):
    """
    Process a CSV file and resolve Google News URLs
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        url_column (str): Name of the column containing URLs to resolve
    """
    print(f"Processing CSV file: {input_file}")
    print(f"URL column: {url_column}")
    print(f"Output file: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        return
    
    # Read the input CSV
    rows = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"Found {len(rows)} rows in CSV file")
    
    # Add resolved_url column if it doesn't exist
    if 'resolved_url' not in fieldnames:
        fieldnames = list(fieldnames) + ['resolved_url']
    
    # Process each row
    processed_count = 0
    for i, row in enumerate(rows):
        if url_column in row and row[url_column]:
            print(f"Processing row {i+1}/{len(rows)}: {row[url_column][:80]}...")
            try:
                resolved_url = resolve_google_news_url(row[url_column])
                row['resolved_url'] = resolved_url
                processed_count += 1
                
                # Add a small delay to avoid rate limiting
                if i % 5 == 0 and i > 0:
                    import time
                    time.sleep(1)
            except Exception as e:
                print(f"Error processing row {i+1}: {e}")
                row['resolved_url'] = row[url_column]  # Fallback to original URL
        else:
            row['resolved_url'] = ''  # Empty if no URL in this row
    
    # Write the output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Processed {processed_count} URLs")
    print(f"Output saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Decode/process Google News URLs from CSV files')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('-o', '--output', help='Output CSV file (default: adds "_resolved" to input filename)')
    parser.add_argument('-c', '--column', default='link', help='Column name containing URLs (default: link)')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0]
        ext = os.path.splitext(args.input_file)[1]
        args.output = f"{base_name}_resolved{ext}"
    
    process_csv_file(args.input_file, args.output, args.column)

if __name__ == "__main__":
    main()
