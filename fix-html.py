#!/usr/bin/env python3
from bs4 import BeautifulSoup
import sys
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import json
import html

load_dotenv()

def extract_body(file_path):
    """
    Extract only the body content from HTML file.
    """
    try:
        # Read file and handle encoding
        with open(file_path, 'rb') as file:
            raw_content = file.read()
            
        # Try different encodings
        for encoding in ['utf-8', 'cp1252', 'ascii']:
            try:
                content = raw_content.decode(encoding, errors='ignore')
                break
            except:
                continue
                
        # Parse HTML and get body
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')
        
        if body:
            # Return the body content with its tags
            return str(body)
        else:
            print("No <body> tag found in the HTML file", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        return None

def process_with_assistant(body_content):
    """
    Process the HTML body content using OpenAI Assistant.
    """
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add the message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=body_content
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.getenv('OPENAI_ASSISTANT_ID')
        )
        
        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                raise Exception(f"Assistant run failed with status: {run_status.status}")
            time.sleep(1)
        
        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        
        # Extract JSON part from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)
        else:
            raise Exception("No JSON found in assistant response")
        
    except Exception as e:
        print(f"Error processing with OpenAI Assistant: {str(e)}", file=sys.stderr)
        return None

def make_it_variable(body, tag_class_json):
    """
    Takes HTML body content and a tag+class selector in JSON format, identifies repeatable sections,
    and modifies them to be extendable.
    
    Args:
        body (str): HTML body content
        tag_class_json (str): JSON string containing tag and class info
        
    Returns:
        str: Modified HTML with repeatable sections made variable
    """
    from bs4 import BeautifulSoup
    
    # Parse JSON
    try:
        tag_class_dict = json.loads(tag_class_json)
        tag = tag_class_dict["tag"].strip("<>")  # Remove angle brackets if present
        class_name = tag_class_dict["class"]
        selector = f"{tag}.{class_name}"
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}", file=sys.stderr)
        return body
    except KeyError as e:
        print(f"Missing required key in JSON: {str(e)}", file=sys.stderr)
        return body
    
    # Parse HTML
    soup = BeautifulSoup(body, 'html.parser')
    
    # Find all elements matching the tag+class
    elements = soup.select(selector)
    
    if not elements:
        print(f"No elements found matching {selector}", file=sys.stderr)
        return body
        
    # Get the first element as template
    template = elements[0]
    
    # Remove all but first instance
    for element in elements[1:]:
        element.decompose()
        
    # Add comment indicating this is a template section
    template.insert_before(BeautifulSoup('<!-- Template section start -->', 'html.parser'))
    template.insert_after(BeautifulSoup('<!-- Template section end -->', 'html.parser'))
    
    # Return the prettified HTML with proper formatting
    return soup.prettify()

def replace_body_content(file_path, new_body, new_file_path="example-fixed.html"):
    """
    Create a new HTML document combining original head with new body content.
    """
    try:
        # Read the original file and handle encoding
        with open(file_path, 'rb') as file:
            raw_content = file.read()
            
        # Try different encodings
        content = None
        for encoding in ['utf-8', 'cp1252', 'ascii']:
            try:
                content = raw_content.decode(encoding, errors='ignore')
                break
            except:
                continue
                
        if not content:
            raise Exception("Could not decode file with any supported encoding")
            
        # Parse the original HTML and new body
        original_soup = BeautifulSoup(content, 'html.parser')
        new_body_soup = BeautifulSoup(new_body, 'html.parser')
        
        # Create new HTML document
        new_soup = BeautifulSoup('<!DOCTYPE html>\n<html></html>', 'html.parser')
        html_tag = new_soup.find('html')
        
        # Get original head or create new one if not exists
        head = original_soup.find('head')
        if not head:
            head = new_soup.new_tag('head')
        
        # Add head and new body to the new document
        html_tag.append(head)
        html_tag.append(new_body_soup)
        
        # Write the complete HTML to the original file
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(new_soup.prettify())
        return True
        
    except Exception as e:
        print(f"Error creating new HTML document: {str(e)}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix-html.py <input_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    body_content = extract_body(input_file)
    
    if body_content:
        result = process_with_assistant(body_content)
        if result:
            print(result)
            fixed_html = make_it_variable(body_content, result)
            
            # Save a backup of the fixed body content
            with open("example-fixed.html", "w", encoding='utf-8') as file:
                file.write(fixed_html)
            
            # Replace the body in the original file
            if replace_body_content(input_file, fixed_html, "example-fixed.html"):
                print(f"Successfully updated {input_file}")
            else:
                print(f"Failed to update {input_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
