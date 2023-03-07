import numpy as np
import pandas as pd

SITE = 'usatoday'
DOMAIN = 'usatoday.com'
DIR = '../data'
URLS_FILE = f'{DIR}/urls_{SITE}.csv'
FETCH_FILE = f'{DIR}/fetch_{SITE}.csv'
VISIT_FILE = f'{DIR}/visit_{SITE}.csv'

def is_in_domain(url):
    return f'://{DOMAIN}' in url or f'://www.{DOMAIN}' in url

def transform_status_codes(code):
    code_map = {
        200: '200 Ok',
        301: '301 Moved Permanently',
        302: '302 Found',
        303: '303 See Other',
        307: '307 Temporary Redirect',
        403: '403 Forbidden',
        404: '404 Not Found'
    }

    return code_map[code]

def get_size_group(size):
    size_map = {
        (0, 1_000): '< 1KB',
        (1_000, 10_000): '1KB ~ <10KB',
        (10_000, 100_000): '10KB ~ <100KB',
        (100_000, 1_000_000): '100KB ~ <1MB',
        (1_000_000, np.inf): '>= 1MB' 
    }

    for low, high in size_map:
        if low <= size < high:
            return size_map[(low, high)]

urls_df = pd.read_csv(URLS_FILE)
fetch_df = pd.read_csv(FETCH_FILE)
visit_df = pd.read_csv(VISIT_FILE)

fetch_df['status'] = fetch_df['status'].astype(np.int16)
num_fetches_succeeded = fetch_df[(fetch_df['status'] < 300) & (fetch_df['status'] >= 200)]['url'].count()
num_fetches_failed_or_aborted = fetch_df[(fetch_df['status'] > 300)]['url'].count()
num_fetches_attempted = num_fetches_succeeded + num_fetches_failed_or_aborted

# print(num_fetches_attempted, num_fetches_succeeded, num_fetches_failed_or_aborted)

unique_urls_fetched = urls_df['url'].unique()
unique_urls_inside_domain, unique_urls_outside_domain = [url for url in unique_urls_fetched if is_in_domain(url)], [url for url in unique_urls_fetched if not is_in_domain(url)]
num_urls, num_unique_urls, num_unique_urls_inside, num_unique_urls_outside = urls_df['url'].count(), len(unique_urls_fetched), len(unique_urls_inside_domain), len(unique_urls_outside_domain)

# print(num_urls, num_unique_urls, num_unique_urls_inside, num_unique_urls_outside)

http_status_groups = fetch_df.groupby('status')['url'].count().reset_index().rename(columns={'url': 'count'})
http_status_groups['status'] = http_status_groups['status'].apply(transform_status_codes)

# print(http_status_groups)

content_type_groups = visit_df.groupby('content_type')['url'].count().reset_index().rename(columns={'url': 'count'})

# print(content_type_groups)

visit_df['size_group'] = visit_df['size(bytes)'].apply(get_size_group)
content_size_groups = visit_df.groupby('size_group')['url'].count().reset_index().rename(columns={'url': 'count'})

# print(content_size_groups)

with open(f'{DIR}/CrawlReport_{SITE}.txt', 'w') as outfile:
    outfile.write(f'Name: Henil Shelat \n\
USC ID: 1438329575 \n\
News site crawled: {DOMAIN} \n\
Number of threads: NA \n\n')
    
    outfile.write(f'Fetch Statistics \n\
================ \n\
# fetches attempted: {num_fetches_attempted} \n\
# fetches succeeded: {num_fetches_succeeded} \n\
# fetches failed or aborted: {num_fetches_failed_or_aborted} \n\n')
    
    outfile.write(f'Outgoing URLs \n\
============= \n\
Total URLs extracted: {num_urls} \n\
# unique URLs extracted: {num_unique_urls} \n\
# unique URLs within News Site: {num_unique_urls_inside} \n\
# unique URLs outside News Site: {num_unique_urls_outside} \n\n')
    
    outfile.write('Status Codes \n\
============ \n')
    for status, count in http_status_groups.to_numpy():
        outfile.write(f'{status}: {count}\n')
    outfile.write('\n')

    outfile.write('File Sizes \n\
========== \n')
    for size, count in content_size_groups.to_numpy()[::-1]:
        outfile.write(f'{size}: {count}\n')
    outfile.write('\n')

    outfile.write('Content Types \n\
============= \n')
    for content_type, count in content_type_groups.to_numpy():
        outfile.write(f'{content_type}: {count}\n')
    outfile.write('\n')