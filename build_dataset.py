from string import Template
import pandas as pd
import requests
import sys

# Configuration parameters
approved_response_codes = [
    200
]
allowed_sites = [
    'MLA',
    'MLB',
    'MLM'
]
base_url = Template('https://api.mercadolibre.com/sites/$site/search?q=tv%204k$paging')


def api_connection(url: str) -> dict:
    """
    Args:
        url (str): URL to request

    Returns:
        dict: Dictionary with the response
    """
    response  = requests.get(url)
    if response.status_code in approved_response_codes:
        return response.json()
    else:
        return None


def find_brand_in_attributes(attributes: list) -> str:
    """Look into the item attributes to obtain the brand

    Args:
        attributes (list): List of attribute objects

    Returns:
        str: Name of the found brand
    """
    for attribute in attributes:
        if attribute['id'] == 'BRAND':
            return attribute['value_name']


def get_fields_by_item(item: dict, condition: str = 'new') -> dict:
    """Look into the filed object and extract the required fields

    Args:
        item (dict): Item object
        condition (str, optional): Based on the requirements it is possible to filter objects by the condition field. Defaults to 'new'.

    Returns:
        dict: Fields object.
    """
    fields = None
    if item['condition'] == condition:
        fields = {
            'item_id': item['id'],
            'title': item['title'],
            'price': item['price'],
            'domain_id': item['domain_id'],
            'brand': find_brand_in_attributes(item['attributes'])
        }
    return fields


def main(site: str) -> None:
    """Main execution of the scrapping and fields extraction

    Args:
        site (str): Received by python args.
    """
    response  = api_connection(base_url.substitute(site=site, paging='&offset=0&sort=id'))
    pages = 100
    items = []
    for i in range(pages):
        response = api_connection(base_url.substitute(site=site, paging=f'&offset={i}&sort=id'))
        if response is not None:
            results = response['results']
            for item in results:
                fields = get_fields_by_item(item=item)
                if fields is not None:
                    items.append(fields)
    df_items = pd.DataFrame(items)
    df_items.to_csv('dataset.csv', index=False)


if __name__ == '__main__':
    try:
        site = sys.argv[1]
        if site not in allowed_sites:
            site = allowed_sites[0]
            print('Default site used', site)
    except:
        site = allowed_sites[0]
        print('Default site used', site)
    main(site)
