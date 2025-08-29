import requests
from bs4 import BeautifulSoup
import json
import re

def get_cs_glossary():
    url = "https://en.wikipedia.org/wiki/Glossary_of_computer_science"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content div
        content = soup.find('div', {'id': 'mw-content-text'})
        
        glossary = {}
        current_section = None
        
        # The structure for the computer science glossary is slightly different.
        # It uses h2 for main sections and dl for terms within those sections.
        # We also need to handle terms directly under a letter heading (like 'A', 'B', etc.)
        
        for element in content.find_all(['h2', 'h3', 'dl', 'dt', 'dd']): # Added dt and dd to handle cases where they are not inside dl
            if element.name == 'h2':
                # Extract section title (e.g., "A", "B", etc.)
                # We are primarily interested in the letter headings for the main sections.
                span = element.find('span', class_='mw-headline')
                if span:
                    section_title = span.get_text().strip()
                    current_section = section_title
                    if current_section not in glossary:
                        glossary[current_section] = {}
            elif element.name == 'dl':
                # Process definition terms and descriptions
                terms = element.find_all('dt', recursive=False) # Only direct children
                descriptions = element.find_all('dd', recursive=False) # Only direct children
                
                for i, term_element in enumerate(terms):
                    term = term_element.get_text().strip()
                    
                    # Get corresponding description
                    if i < len(descriptions):
                        description = descriptions[i].get_text().strip()
                        
                        # Clean up the description
                        description = re.sub(r'\s+', ' ', description)
                        
                        if current_section:
                            glossary[current_section][term] = description
                        else:
                            # Fallback if no section is found for some reason
                            if 'General' not in glossary:
                                glossary['General'] = {}
                            glossary['General'][term] = description
            
            # Handle cases where dt and dd are direct siblings under a section, not wrapped in dl
            elif element.name == 'dt':
                term = element.get_text().strip()
                next_sibling = element.find_next_sibling()
                if next_sibling and next_sibling.name == 'dd':
                    description = next_sibling.get_text().strip()
                    description = re.sub(r'\s+', ' ', description)
                    if current_section:
                        glossary[current_section][term] = description
                    else:
                        if 'General' not in glossary:
                            glossary['General'] = {}
                        glossary['General'][term] = description


        # A common issue in Wikipedia glossaries is a "See also" or "References" section at the end.
        # We'll clean those up.
        keys_to_remove = []
        for key in glossary.keys():
            if key.lower() in ["see also", "references", "external links", "notes", "bibliography"]:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del glossary[key]

        return glossary
    
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"Error parsing the content: {e}")
        return None

def save_glossary_to_file(glossary, filename='cs_glossary.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(glossary, f, indent=2, ensure_ascii=False)
        print(f"Glossary saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def print_glossary(glossary, max_terms_per_section=5):
    for section, terms in glossary.items():
        print(f"\n{'='*50}")
        print(f"SECTION: {section}")
        print(f"{'='*50}")
        
        count = 0
        for term, description in terms.items():
            if count >= max_terms_per_section:
                print(f"... and {len(terms) - max_terms_per_section} more terms")
                break
            
            print(f"\n{term}:")
            print(f"  {description[:200]}{'...' if len(description) > 200 else ''}")
            count += 1

def search_term(glossary, search_term_query):
    search_term_query_lower = search_term_query.lower()
    results = []
    for section, terms in glossary.items():
        for term, description in terms.items():
            if search_term_query_lower in term.lower() or search_term_query_lower in description.lower():
                results.append({
                    'term': term,
                    'section': section,
                    'description': description
                })
    return results

if __name__ == "__main__":
    print("Fetching Computer Science Glossary from Wikipedia...")
    
    # Get the glossary
    cs_glossary = get_cs_glossary()
    
    if cs_glossary:
        print(f"Successfully extracted glossary with {len(cs_glossary)} sections")
        
        # Print a preview
        print_glossary(cs_glossary, max_terms_per_section=5)
        
        # Save to file
        save_glossary_to_file(cs_glossary)
        
        # Example search
        print(f"\n{'='*50}")
        print("SEARCH EXAMPLE")
        print(f"{'='*50}")
        search_results = search_term(cs_glossary, "algorithm")
        if search_results:
            print(f"Found {len(search_results)} terms containing 'algorithm':")
            for result in search_results[:3]:  # Show first 3 results
                print(f"\n{result['term']} (in {result['section']}):")
                print(f"  {result['description'][:150]}...")
        else:
            print("No terms found containing 'algorithm'.")
    else:
        print("Failed to extract glossary")