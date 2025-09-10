"""
Google News URL decoder module

This module decodes Google News URLs to get the actual article URLs.
Based on the TypeScript implementation by Ruslan Gainutdinov.

Licensed under: MIT License

Copyright (c) 2024 Ruslan Gainutdinov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import base64
import requests
import json
from urllib.parse import quote, urlparse
import logging

logger = logging.getLogger(__name__)

def fetch_decoded_batch_execute(article_id: str) -> str:
    """
    Fetch decoded URL using Google's batch execute protocol
    
    Args:
        article_id (str): The Google News article ID
        
    Returns:
        str: The decoded actual URL
    """
    try:
        # Prepare the request data
        request_data = [
            [
                "Fbv4je",
                f'["garturlreq",[["en-US","US",["FINANCE_TOP_INDICES","WEB_TEST_1_0_0"],null,null,1,1,"US:en",null,180,null,null,null,null,null,0,null,null,[1608992183,723341000]],"en-US","US",1,[2,3,4,8],1,0,"655000234",0,0,null,0],"{article_id}"]',
                None,
                "generic"
            ]
        ]
        
        # Convert to JSON and encode
        json_data = json.dumps([request_data])
        payload = "f.req=" + quote(json_data)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "https://news.google.com/"
        }
        
        response = requests.post(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute?rpcids=Fbv4je",
            headers=headers,
            data=payload,
            timeout=30
        )
        response.raise_for_status()
        
        text = response.text
        
        # Parse the response
        # The response has a specific format with multiple lines
        lines = text.strip().split('\n')
        if len(lines) < 3:
            raise Exception("Invalid response format")
        
        # Find the line with our data (usually the third line)
        data_line = None
        for line in lines:
            if line.startswith('[["wrb.fr","Fbv4je"'):
                data_line = line
                break
        
        if not data_line:
            # Try the third line as fallback
            if len(lines) >= 3:
                data_line = lines[2]
            else:
                raise Exception("Could not find data line in response")
        
        # Parse the JSON
        response_data = json.loads(data_line)
        if not response_data or len(response_data) < 2:
            raise Exception("Invalid response data format")
        
        # Extract the URL from the response
        # The structure is usually [[..., "...", "..."], ...]
        second_element = response_data[0][1] if isinstance(response_data[0], list) and len(response_data[0]) > 1 else None
        if not second_element:
            raise Exception("Could not extract second element from response")
        
        # Parse the inner JSON
        inner_data = json.loads(second_element)
        if not inner_data or len(inner_data) < 2:
            raise Exception("Invalid inner data format")
        
        return inner_data[1]
    except Exception as e:
        logger.error(f"Error fetching decoded URL: {e}")
        # Return the original URL as fallback
        raise

def decode_google_news_url(source_url: str) -> str:
    """
    Decode Google News URL to get the actual article URL
    
    Args:
        source_url (str): The Google News URL to decode
        
    Returns:
        str: The decoded actual URL or the original URL if it can't be decoded
    """
    try:
        url = urlparse(source_url)
        path = url.path.split("/")
        
        # Check if it's a Google News articles URL
        if (url.hostname in ["news.google.com", "news.google.com.au", "news.google.co.uk", "news.google.ca", "news.google.de"] and 
            len(path) > 1 and 
            (path[-2] == "articles" or path[-2] == "rss")):
            
            # Extract the base64 encoded part
            base64_part = path[-1].split("?")[0]  # Remove query parameters
            
            # Decode the base64
            # Add padding if needed
            missing_padding = len(base64_part) % 4
            if missing_padding:
                base64_part += '=' * (4 - missing_padding)
            
            try:
                decoded_bytes = base64.urlsafe_b64decode(base64_part)
                decoded_str = decoded_bytes.decode('latin1')
            except Exception:
                # Try regular base64 if urlsafe fails
                try:
                    decoded_bytes = base64.b64decode(base64_part)
                    decoded_str = decoded_bytes.decode('latin1')
                except Exception:
                    # If both fail, return original URL
                    return source_url
            
            # Check for new style encoding (starts with AU_)
            if decoded_str.startswith('\x08\x13"') or "AU_yqL" in decoded_str:
                # This is the new style encoding that requires batch execute
                try:
                    return fetch_decoded_batch_execute(base64_part.rstrip('='))
                except Exception:
                    # If batch execute fails, return original URL
                    return source_url
            
            # For older style encoding, try to extract the URL
            # This is a simplified version - in practice, the full decoding
            # is more complex and depends on the exact byte structure
            return source_url
        else:
            return source_url
    except Exception as e:
        logger.error(f"Error decoding Google News URL {source_url}: {e}")
        return source_url

# Test function
if __name__ == "__main__":
    # Test with a sample URL
    test_url = "https://news.google.com/rss/articles/CBMilwJBVV95cUxQVUdVT3F3MjhvcEJ6ckN4RWlLWGE5MV96WHROVU8xbjJTT1IzVlZMTUY5eUNPdll3MlZ1NG5Fa1E3dlh5eURLVmVWem8xNEpwYlpSVjJZaFhtYXNpMkdWQTFYaWlIUE5OYlNlS081cWo1cFltLXRTX3dwRF9aekFtZEtyUW5WOTNJNTZUaWJ3aVA4TzExakJjTlJIMnJjWjQ1c293MlBwZ1ZnMVhlWTZGQ3A5cW5aM2JmUUZiVElveS1BMTliaUkyaXBpcVJneDZjdE1IQ3VyMUtORFpyTkxzOTMxR0FzN1kyenA5QlhhNXlSY0lURGw0R1RiOHI0Y1p4RUswaUNoUjlINUJQWWs0M0JMY1M5d0k?oc=5"
    print("Testing URL decoding...")
    print(f"Input URL: {test_url}")
    try:
        decoded_url = decode_google_news_url(test_url)
        print(f"Decoded URL: {decoded_url}")
    except Exception as e:
        print(f"Error: {e}")