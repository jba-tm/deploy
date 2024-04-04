import numpy as np
import csv
from lxml import etree
from tqdm import tqdm

data_path = "app/contrib/graph_knowledge/data"

xml_file = f"{data_path}/Semi-structured data/full database.xml"

# Load and parse the XML file
tree = etree.parse(xml_file)  # Replace with the path to your XML file

namespaces = {'db': 'http://www.drugbank.ca'}  # 'db' is a prefix we assign to the namespace

print("Load and parse the XML file")


def extract_primary_drug_id(drug_element):
    """
    Extracts the primary drug-id.
    """
    primary_drug_id = drug_element.find("db:drugbank-id[@primary='true']", namespaces)
    return primary_drug_id.text.strip() if primary_drug_id is not None and primary_drug_id.text else np.na


def extract_values(elements):
    """
    Extracts text from multiple occurrences of an element and concatenates them using '|'.
    Replaces missing elements with 'null' or an empty string.
    """
    values = []
    for elem in elements:
        # Check if the element has text, and if not, use 'null' or an empty string
        text = elem.text if elem.text is not None else 'null'
        values.append(text)
    return ' | '.join(values)


def extract_classification(drug_element):
    """
    Extracts text from all sub-elements within 'classification' and concatenates them using '|'.
    Handles multiple occurrences of the same sub-tag.
    """
    classification = drug_element.find('db:classification', namespaces)
    classification_data_local = {}
    if classification is not None:
        for subtag in classification:
            tag_name = subtag.tag.split('}')[-1]
            if tag_name in classification_data:
                classification_data_local[tag_name] += f'|{subtag.text}'
            else:
                classification_data_local[tag_name] = subtag.text if subtag.text is not None else 'null'

    # Rename 'description' to 'info about compound'
    if 'description' in classification_data_local:
        classification_data_local['info about compound'] = classification_data_local.pop('description')

    return classification_data_local


def extract_synonyms(drug_element):
    """
    Extracts text from all 'synonym' elements nested within 'synonyms'.
    """
    synonyms = drug_element.find('db:synonyms', namespaces)
    if synonyms is not None:
        return ' | '.join([syn.text for syn in synonyms if syn.text is not None])
    return 'null'


def extract_general_references(drug_element):
    """
    Extracts specific data from 'general-references' within a drug element.
    Handles empty 'articles' and 'links' sections correctly.
    """
    general_references = drug_element.find('db:general-references', namespaces)
    if general_references is not None:
        pubmed_ids, citations, article_names, article_links = ([] for _ in range(4))

        # Process articles
        articles = general_references.find('db:articles', namespaces)
        if articles is not None and articles.findall('db:article', namespaces):
            for article in articles.findall('db:article', namespaces):
                pubmed_id = article.findtext('db:pubmed-id', default='null', namespaces=namespaces)
                citation = article.findtext('db:citation', default='null', namespaces=namespaces)
                pubmed_ids.append(pubmed_id)
                citations.append(citation)
        else:
            pubmed_ids.append('null')
            citations.append('null')

        # Process links
        links = general_references.find('db:links', namespaces)
        if links is not None and links.findall('db:link', namespaces):
            for link in links.findall('db:link', namespaces):
                title = link.findtext('db:title', default='null', namespaces=namespaces)
                url = link.findtext('db:url', default='null', namespaces=namespaces)
                article_names.append(title)
                article_links.append(url)
        else:
            article_names.append('null')
            article_links.append('null')

        return {
            'pubmed-id': ' | '.join(pubmed_ids),
            'citation': ' | '.join(citations),
            'article name': ' | '.join(article_names),
            'article link': ' | '.join(article_links)
        }

    return {'pubmed-id': 'null', 'citation': 'null', 'article name': 'null', 'article link': 'null'}


def extract_tag_content(drug_element, tag_name):
    """
    Extracts text content from a specific tag within the drug element.
    Returns 'null' if the tag is missing or empty.
    """
    tag_element = drug_element.find(f'db:{tag_name}', namespaces)
    return tag_element.text.strip() if tag_element is not None and tag_element.text else 'null'


def extract_product_info(product_element):
    """
    Extracts information from each product tag within products.
    Handles empty 'products' sections correctly.
    """
    product_data = {
        'medicine name': [],
        'manufacturer': [],
        'dosage form': [],
        'dosage strength': [],
        'route': [],
        'Country of manufacture': [],
        'medicine source': []
    }

    # Check if product_element is not None and has product children
    if product_element is not None and product_element.findall('db:product', namespaces):
        for product in product_element.findall('db:product', namespaces):
            product_data['medicine name'].append(product.findtext('db:name', default='null', namespaces=namespaces))
            product_data['manufacturer'].append(product.findtext('db:labeller', default='null', namespaces=namespaces))
            product_data['dosage form'].append(
                product.findtext('db:dosage-form', default='null', namespaces=namespaces))
            product_data['dosage strength'].append(
                product.findtext('db:strength', default='null', namespaces=namespaces))
            product_data['route'].append(product.findtext('db:route', default='null', namespaces=namespaces))
            product_data['Country of manufacture'].append(
                product.findtext('db:country', default='null', namespaces=namespaces))
            product_data['medicine source'].append(product.findtext('db:source', default='null', namespaces=namespaces))
    else:
        # Append 'null' for each key if no product children are found
        for key in product_data:
            product_data[key].append('null')

    # Concatenating values with '|'
    for key in product_data:
        values = product_data[key]
        product_data[key] = '||'.join('null' if val == '' else val for val in values)

    return product_data


if __name__ == "__main__":
    # Find all 'drug' elements
    all_drug_elements = tree.findall('.//db:drug', namespaces)

    drugs_data = []
    classification_columns = set()
    all_classification_tags = [
        'info about compound', 'direct-parent', 'kingdom', 'superclass', 'class',
        'subclass', 'alternative-parent', 'substituent'
    ]

    # Iterate over each drug element and extract information
    for drug in tqdm(all_drug_elements):
        if drug.getparent().tag.split('}')[-1] == 'drugbank':
            drug_data = {
                'ID': extract_primary_drug_id(drug),
                'name': extract_values(drug.findall('db:name', namespaces)),
                'description': extract_values(drug.findall('db:description', namespaces)),
                'state': extract_tag_content(drug, 'state'),
                'synonym': extract_synonyms(drug),
                'synthesis-reference': extract_tag_content(drug, 'synthesis-reference'),
                'indication': extract_tag_content(drug, 'indication'),
                'pharmacodynamics': extract_tag_content(drug, 'pharmacodynamics'),
                'mechanism-of-action': extract_tag_content(drug, 'mechanism-of-action'),
                'toxicity': extract_tag_content(drug, 'toxicity'),
                'metabolism': extract_tag_content(drug, 'metabolism'),
                'absorption': extract_tag_content(drug, 'absorption'),
                'half-life': extract_tag_content(drug, 'half-life'),
                'protein-binding': extract_tag_content(drug, 'protein-binding'),
                'route-of-elimination': extract_tag_content(drug, 'route-of-elimination'),
                'volume-of-distribution': extract_tag_content(drug, 'volume-of-distribution'),
                'clearance': extract_tag_content(drug, 'clearance'),
                'average-mass': extract_tag_content(drug, 'average-mass'),
                'monoisotopic-mass': extract_tag_content(drug, 'monoisotopic-mass'),
            }
            products_element = drug.find('db:products', namespaces)
            products_info = extract_product_info(products_element) if products_element is not None else {
                'medicine name': 'null', 'manufacturer': 'null', 'dosage form': 'null',
                'dosage strength': 'null', 'route': 'null', 'Country of manufacture': 'null', 'medicine source': 'null'
            }

            # Add classification data with all possible tags
            classification_data = {tag: 'null' for tag in all_classification_tags}  # Initialize with 'null'
            classification_data.update(extract_classification(drug))
            general_references_data = extract_general_references(drug)
            drug_data.update(products_info)

            drugs_data.append(drug_data)
            drug_data.update(classification_data)
            drug_data.update(general_references_data)
            classification_columns.update(classification_data.keys())

    print("Find all 'drug' elements")

    print("Iterate over each drug element and extract information")
    # Define CSV columns
    columns = [
                  'ID', 'name', 'description', 'state',
                  'synonym', 'pubmed-id', 'citation', 'article name',
                  'article link'
              ] + sorted(list(classification_columns)) + [
                  'synthesis-reference', 'indication',
                  'pharmacodynamics', 'mechanism-of-action',
                  'toxicity', 'metabolism',
                  'absorption', 'half-life',
                  'protein-binding',
                  'route-of-elimination',
                  'volume-of-distribution', 'clearance',
                  'average-mass', 'monoisotopic-mass',
                  'medicine name', 'manufacturer', 'dosage form',
                  'dosage strength', 'route',
                  'Country of manufacture', 'medicine source'
              ]

    # Write to CSV
    with open(
            f"{data_path}/Structured data/drugs.csv", 'w',
            newline='', encoding='utf-8'
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(drugs_data)
