from datetime import datetime
from xml.etree import ElementTree
from typing import List, Dict

from app.database import SalesReport


async def parse_sales_data(xml_content: str, report: SalesReport) -> List[Dict]:
    tree = __get_xml_tree(xml_content=xml_content)

    __validate_sales_data_root(tree=tree)
    report.sales_date = __extract_date_format(date_str=tree.attrib['date'])
    products_element = __extract_products_section(tree=tree)
    products = __parse_products(products_element=products_element, report=report)

    if not products:
        raise ValueError('Invalid XML: No valid products found in `products` element.')

    return products


def __get_xml_tree(xml_content: str) -> ElementTree.Element:
    if not xml_content.strip():
        raise ValueError("Invalid XML: The provided content is empty.")

    try:
        tree = ElementTree.fromstring(xml_content)
        return tree
    except ElementTree.ParseError as e:
        raise ValueError(f"Invalid XML: Failed to parse content. Error: {e}")


def __validate_sales_data_root(tree: ElementTree.Element):
    if tree.tag != 'sales_data' or 'date' not in tree.attrib:
        raise ValueError('Invalid XML: Root element must be `sales_data` with a `date` attribute.')


def __extract_date_format(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid date format in XML. Expected format: YYYY-MM-DD.')


def __extract_products_section(tree: ElementTree.Element) -> ElementTree.Element:
    products_element = tree.find('products')
    if products_element is None:
        raise ValueError('Invalid XML: `products` element is missing.')
    return products_element


def __parse_products(products_element: ElementTree.Element, report: SalesReport) -> List[Dict]:
    products = []
    for product in products_element.findall('product'):
        try:
            product_data = __extract_product_data(product=product)
            if not all(product_data.values()):
                raise ValueError(f'Missing or empty fields in: {product}')
        except (AttributeError, ValueError, TypeError) as e:
            raise ValueError(f'Invalid product data: {e}')

        products.append({
            **product_data,
            'sales_report': report
        })

    return products


def __extract_product_data(product: ElementTree.Element) -> Dict:
    return {
        'product_id': int(product.find('id').text),
        'product_name': product.find('name').text,
        'quantity': int(product.find('quantity').text),
        'price': float(product.find('price').text),
        'category': product.find('category').text,
    }
