import os
import requests
import json
import argparse
from datetime import datetime
from uuid import uuid4
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()

class AstraDBClient:
    def __init__(self):
        # Get environment variables
        self.db_id = '839635db-b3b0-4b64-b71e-90531f6aae36'
        self.db_region = 'us-east1'
        self.keyspace = 'url_cache'
        self.token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        
        self.base_url = f"https://{self.db_id}-{self.db_region}.apps.astra.datastax.com"
        self.headers = {
            'content-type': 'application/json',
            'x-cassandra-token': self.token
        }

    def create_table(self, table_name, column_definitions, primary_key):
        """
        Create a table in the keyspace
        """
        url = f"{self.base_url}/api/rest/v2/schemas/keyspaces/{self.keyspace}/tables"
        
        payload = {
            "name": table_name,
            "ifNotExists": True,
            "columnDefinitions": column_definitions,
            "primaryKey": primary_key,
            "tableOptions": {
                "defaultTimeToLive": 0
            }
        }

        response = requests.post(url, headers=self.headers, json=payload)
        print(self.headers)
        return response.json() if response.content else response.status_code

    def add_row(self, table_name, data):
        """
        Add a row to the specified table
        """
        url = f"{self.base_url}/api/rest/v2/keyspaces/{self.keyspace}/{table_name}"
        print(self.headers)
        print(url)
        response = requests.post(url, headers=self.headers, json=data)
        return response.json() if response.content else response.status_code

    def get_row(self, table_name, url):
        """
        Retrieve a row from the specified table by searching for its URL
        
        Args:
            table_name (str): Name of the table
            url (str): URL to search for
            
        Returns:
            dict: Row data if found, None if not found
        """
        request_url = f"{self.base_url}/api/rest/v2/keyspaces/{self.keyspace}/{table_name}"
        # Add query parameters to search by URL
        params = {
            "where": {
                "url": {
                    "$eq": url
                }
            }
        }
        response = requests.get(request_url, headers=self.headers, params={"where": json.dumps(params["where"])})
        if response.status_code == 404 or not response.content:
            return None
        
        data = response.json()
        # The response will be a list of matching rows, we want the first one
        return data["data"][0] if data.get("data") else None

def add_url_template_to_db(url: str, template_content: str) -> dict:
    """
    Add a URL and its template content to the database
    
    Args:
        url (str): The URL to cache
        template_content (str): The template content to store
        
    Returns:
        dict: Response from the database operation
    """
    client = AstraDBClient()
    
    cache_data = {
        "url": url,
        "template": template_content,
        "id": str(uuid4()),
        "created": str(datetime.now().isoformat())
    }
    
    return client.add_row("url_cache_base3", cache_data)

def get_template_by_url(url: str) -> dict:
    """
    Retrieve a template entry by its URL
    
    Args:
        url (str): URL to retrieve the template for
        
    Returns:
        dict: Template data if found, None if not found
    """
    client = AstraDBClient()
    return client.get_row("url_cache_base3", url)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Add URL and template to AstraDB cache')
    parser.add_argument('url', help='URL to cache')
    parser.add_argument('template_file', help='Path to template file')
    
    args = parser.parse_args()
    
    # Read template content from file
    try:
        with open(args.template_file, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file '{args.template_file}' not found")
        return
    except Exception as e:
        print(f"Error reading template file: {e}")
        return

    # Add the data using the new function
    result = add_url_template_to_db(args.url, template_content)
    print("Row insertion result:", result)

if __name__ == "__main__":
    main()
