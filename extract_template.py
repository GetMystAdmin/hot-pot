from agents_stuff import build_html_from_posts, generate_social_posts
from gather_news import NewsAPI

def extract_template_section(html_file_path):
    """
    Extract HTML content between template section comments from a file.
    
    Args:
        html_file_path (str): Path to the HTML file
        
    Returns:
        str: The HTML content between template section markers, or None if not found
    """
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(html_file_path, 'r', encoding=encoding) as file:
                content = file.read()
                
            start_marker = "<!-- Template section start -->"
            end_marker = "<!-- Template section end -->"
            
            start_index = content.find(start_marker)
            if start_index == -1:
                continue
                
            # Add length of start marker to get to the actual content
            start_index += len(start_marker)
            
            end_index = content.find(end_marker, start_index)
            if end_index == -1:
                continue
                
            # Extract the content between markers
            template_content = content[start_index:end_index].strip()
            return template_content
            
        except FileNotFoundError:
            print(f"Error: File {html_file_path} not found")
            return None
        except UnicodeDecodeError:
            # Try the next encoding
            continue
        except Exception as e:
            print(f"Error: An unexpected error occurred: {str(e)}")
            return None
    
    print(f"Error: Could not read the file with any of the attempted encodings: {', '.join(encodings)}")
    return None

def replace_template_section(original_file_path, new_content, output_file_path=None):
    """
    Replace the template section in the original HTML file with new content and save to a new file.
    
    Args:
        original_file_path (str): Path to the original HTML file
        new_content (str): New HTML content to replace the template section with
        output_file_path (str, optional): Path for the output file. If None, generates a name with '_generated' suffix
        
    Returns:
        tuple: (bool, str) - (Success status, Output file path or error message)
    """
    try:
        with open(original_file_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        # Replace the template section in the original content
        start_marker = "<!-- Template section start -->"
        end_marker = "<!-- Template section end -->"
        start_index = original_content.find(start_marker)
        end_index = original_content.find(end_marker) + len(end_marker)
        
        if start_index == -1 or end_index == -1:
            return False, "Could not find template markers in the original file"
            
        new_html = original_content[:start_index] + start_marker + "\n" + new_content + "\n" + end_marker + original_content[end_index:]
        
        # Generate output file path if not provided
        if output_file_path is None:
            output_file_path = original_file_path.rsplit('.', 1)[0] + '_generated.html'
        
        # Save the new content
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(new_html)
        
        return True, output_file_path
        
    except Exception as e:
        return False, f"Error while replacing template: {str(e)}"

def generate_personalized_content(html_file_path, personality_traits):
    """
    Generate personalized content based on news articles and personality traits.
    
    Args:
        html_file_path (str): Path to the HTML template file
        personality_traits (str): String containing personality traits
        
    Returns:
        str: Path to the generated HTML file, or None if an error occurred
    """
    # Extract template from the HTML file
    template = extract_template_section(html_file_path)
    if not template:
        print("No template section found or an error occurred")
        return None
        
    # Get news articles
    news_api = NewsAPI()
    entertainment_articles = news_api.get_articles('entertainment')
    general_articles = news_api.get_articles('general')
    
    # Format news data
    news_data = ""
    for article in entertainment_articles + general_articles:
        news_data += f"\n{article['title']}\n"
        news_data += f"Source: {article['source']['name']}\n"
        news_data += f"Description: {article['description']}\n"

    # Generate posts and build HTML
    posts = generate_social_posts(news_data, personality_traits)
    html_content = build_html_from_posts(posts, template)

    # Replace template section and save to new file
    success, result = replace_template_section(html_file_path, html_content)
    
    if success:
        print(f"Generated HTML saved to: {result}")
        return result
    else:
        print(f"Error: {result}")
        return None

# Example usage:
if __name__ == "__main__":
    import sys
    
    # If a file path is provided as command line argument, use that
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default example file path if none provided
        file_path = "example-fixed.html"
    
    print(f"Processing HTML file: {file_path}")
    
    # Example personality traits
    personality_traits = """Happiness: 7/10
    Excitement: 4/10
    Sarcasm: 8/10
    Professionalism: 6/10
    Humor: 5/10"""
    
    generated_file = generate_personalized_content(file_path, personality_traits)
    
    if not generated_file:
        print("Note: Make sure your HTML file contains the following markers:")
        print("<!-- Template section start -->")
        print("<!-- Template section end -->") 