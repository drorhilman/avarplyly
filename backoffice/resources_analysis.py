import pandas as pd, re, itertools, json
from glob import glob
from datetime import datetime


documents_suffixes = [ 'csv', 'docx', 'doc']
images_suffixes = ['jpg', 'jpeg', 'svg', 'png', 'webp', 'pdn', 'tif', 'tiff']
pages_suffixes = ['htm', 'html']
base_path = '../_site'


def analyze_page_for_resources(page_file):
    """get all sources from the files on page"""

    pattern = re.compile("<img\s+[^>]*?src=[\"|']([^\"']+)")
    with open(page_file, 'r', encoding="utf8") as f:
        page = f.read()
    resources = pattern.findall(page)
    resources = [{'path' : path.lstrip('/'), 
                'type': image_or_doc(path),
                'source' : page_file
                } 
                for path in resources]
    return resources

def image_or_doc(path):
    """
    Determine if a file is an image or document.
    """
    suffix = path.split('.')[-1]
    if suffix in images_suffixes: return 'image'
    if suffix in documents_suffixes: return 'document'
    if '/data:image/' in path: return 'image'
    return 'unknown'


def relative_path(path, base_path = base_path):
    """
    Return the relative path from the site root.
    """
    return path.split(f'{base_path}')[1].lstrip('/').lstrip('\\')

def save_legal_status(data):
    now = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    data['update_date'] = now
    fname = f'legal_records/{now}-resource_record.json'
    with open(fname, 'w', encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def load_legal_status():
    records = (pd.DataFrame(
                [
                    json.load(open(file)) 
                    for file in glob('legal_records/*.json')
                ]
                )
                .sort_values('update_date', ascending=False)
                .drop_duplicates('resource')
            )
    return records



def site_resources(base_path = base_path):
    """
    List all resources on the site.
    """
    all_site_resources = glob(f'{base_path}/**/*', recursive=True)
    sources = [{'path': relative_path(path), 
                'type': image_or_doc(path),
                'source' : 'assets'
                } 
                for path in all_site_resources 
                if path.split('.')[-1] in [*images_suffixes, *documents_suffixes]
                and not '/temp/' in path
                ]   

    pages = [x for x in all_site_resources if x.split('.')[-1] in pages_suffixes]
    page_resources =   [analyze_page_for_resources(page_file) for page_file in pages]
    page_resources = list(itertools.chain.from_iterable(page_resources))

    resources = pd.DataFrame(page_resources + sources).drop_duplicates(subset=['path'])
    legal_resources = load_legal_status()
    resources = resources.merge(legal_resources, how='left', left_on='path', right_on='resource').fillna('')
    return resources


if __name__ == '__main__':
    resources = site_resources()
    print(resources)