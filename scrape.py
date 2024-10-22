import requests
from bs4 import BeautifulSoup
import time
import json

"""
Scrap the content of a single page.
"""
NOTION_HELP_PAGE = 'https://www.notion.so/help/category/new-to-notion'

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def scrape_help_page(url):
    soup = get_soup(url)
    
    title = soup.title.string.strip()

    structured_content = []
    current_header = None
    current_paragraphs = []
    
    for element in soup.find_all(['h2', 'h3', 'p']):
        if element.name in ['h2', 'h3']:
            if current_header:
                structured_content.append({
                    'header': current_header,
                    'paragraphs': current_paragraphs,
                    'char_length': sum(len(p) for p in current_paragraphs) + len(current_header)
                })
            current_header = element.text.strip().replace('\xa0', ' ')
            current_paragraphs = []
        elif element.name == 'p':
            # strip and ignore empty paragraphs
            if element.text.strip():
                current_paragraphs.append(element.text.strip().replace('\xa0', ' '))
    
    # Add the last section
    if current_header:
        structured_content.append({
            'header': current_header,
            'paragraphs': current_paragraphs,
            'char_length': sum(len(p) for p in current_paragraphs) + len(current_header)

        })
    
    return {'title': title, 'content': structured_content, 'url': url,}


def get_all_help_links():
    base_url = NOTION_HELP_PAGE
    soup = get_soup(base_url)
    
    # Find all help article links
    article_links = soup.find_all('a', class_='toggleList_link__safdF')
    
    article_urls = []
    
    for link in article_links:
        # ignore if notion-academy in link, ignore guides 
        if 'notion-academy' not in link['href'] and 'help/guides' not in link['href']:
            article_urls.append('https://www.notion.so' + link['href'])
    
    return article_urls

def scrape_notion_help(existing_data, forceRetry=False):
    article_links = get_all_help_links()
    print(f'🍏 Found {len(article_links)} links to scrape. Existing data has {len(existing_data.keys())} entries.')
    
    scraped_data = {}

    # Scrape data in batches of 5 
    for i in range(0, len(article_links), 5):
        batch = article_links[i:i+5]
        for j, link in enumerate(batch):
            if not forceRetry and link in existing_data:
                print(f"{i + j + 1}/{len(article_links)} Skipping: {link}")
                scraped_data[link] = existing_data[link]
                continue
            article_data = scrape_help_page(link)
            scraped_data[article_data['url']] = article_data
            print(f"{i + j + 1}/{len(article_links)} Scraped: {article_data['title']}")
        time.sleep(1)  # Be respectful with request rate
    
    return scraped_data

def clean_scraped_data(scraped_data):
    """
    Remove non-core content from scraped data.
    
    This function removes:
    - Sections with headers like "Was this resource helpful?"
    - Empty sections
    - Paragraphs with specific unwanted content
    """
    unwanted_headers = ['was this resource helpful']
    unwanted_paragraphs = ['Company', 'Download', 'Resources', 'Notion for']
    
    def should_remove_section(section):
        return any(header in section['header'].lower() for header in unwanted_headers)
    
    def should_remove_paragraph(text):
        return any(unwanted == text for unwanted in unwanted_paragraphs)
    
    for article in scraped_data.values():
        article['content'] = [
            {
                'header': section['header'],
                'paragraphs': [
                    para for para in section['paragraphs']
                    if not should_remove_paragraph(para)
                ],
                'char_length': section['char_length']
            }
            for section in article['content']
            if not should_remove_section(section)
        ]

        article['content'] = [section for section in article['content'] if len(section['paragraphs']) > 0]


    return scraped_data


def get_chunks(scraped_data, max_chunk_size=750):
    """
    Split scraped data into chunks, keeping headers and paragraphs together as much as possible.
    
    Args:
    scraped_data (dict): The scraped data to be chunked.
    max_chunk_size (int): Maximum size of each chunk in characters. Default is 750.

    Returns:
    list: A list of formatted chunks.
    """
    def format_chunk(chunk):
        """ Format a chunk into a single string."""
        return f"HEADER: {chunk['header']}\n\nCONTENT: " + '\n'.join(chunk['paragraphs'])

    chunks = []
    for article in scraped_data.values():
        for section in article['content']:
            header = section['header']
            paragraphs = section['paragraphs']
            formatted_length = len(format_chunk(section))
            
            if formatted_length <= max_chunk_size:
                chunks.append(format_chunk(section))
            else:
                # If the section is too long, split it into smaller chunks
                current_chunk = {'header': header, 'paragraphs': []}
                current_length = len(f"HEADER: {header}\n\nCONTENT: ")
                
                for paragraph in paragraphs:
                    paragraph_length = len(paragraph) + (1 if current_chunk['paragraphs'] else 0)  # Add 1 for '\n' if not first paragraph
                    if current_length + paragraph_length <= max_chunk_size:
                        current_chunk['paragraphs'].append(paragraph)
                        current_length += paragraph_length
                    else:
                        chunks.append(format_chunk(current_chunk))
                        current_chunk = {'header': header, 'paragraphs': [paragraph]}
                        current_length = len(f"HEADER: {header}\n\nCONTENT: ") + len(paragraph)
                
                # Add the last chunk if it's not empty
                if current_chunk['paragraphs']:
                    chunks.append(format_chunk(current_chunk))

    return chunks

if __name__ == '__main__':
    # Read existing scraped data
    with open('notion_help_articles.json', 'r') as f:
        help_articles = json.loads(f.read())

    # Run the scraper
    help_articles = scrape_notion_help(help_articles)

    # Write to a file
    with open('notion_help_articles.json', 'w') as f:
        f.write(json.dumps(help_articles, ensure_ascii=False))

    # Print results
    for article in list(help_articles.values())[0:10]:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Content preview: {article['content'][:100]}...")
        print('-' * 50)

    # Clean the data
    cleaned_data = clean_scraped_data(help_articles)
    print(f'🍏 Cleaned {len(help_articles)} entries to {len(cleaned_data)} entries')
   
    # Get chunks
    chunks = get_chunks(cleaned_data, 750)
    print(f'🍏 Found {len(chunks)} chunks')

    # Print the first chunk
    print(f'🍏 Chunk sample: \n{chunks[0]}')

    # Write chunks to a file
    with open('notion_help_chunks.json', 'w') as f:
        f.write(json.dumps(chunks, ensure_ascii=False))