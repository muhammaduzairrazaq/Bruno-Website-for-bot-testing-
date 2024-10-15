# Script to remove the href attribute from the anchor tags in a saved HTML file.


from bs4 import BeautifulSoup

def remove_href_from_file(html_file):
    # Step 1: Open the saved HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Step 2: Find all <a> tags and remove their href attributes
    for a_tag in soup.find_all('a', href=True):
        del a_tag['href']

    # Step 3: Save the modified HTML back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"Modified HTML saved: {html_file}")

# Example usage:
html_file = 'Furna-Tech™ _ Interactive Furniture Solutions.html'  # Replace with your saved HTML file path
remove_href_from_file(html_file)
