from datetime import datetime, timedelta
import requests
import os
import threading
import tqdm
from bs4 import BeautifulSoup
import concurrent.futures


comics_name = 'garfield'  # should be the same as in the url https://www.gocomics.com/garfield/
comix_date_start = "2023/01/03"
comix_date_end = "2023/01/31"
download_folder = "garfield_comics"

# Create a function in Python that generates a list of dates by specifying a start date and an end date:
def date_range(start, end):
    start_date = datetime.strptime(start, '%Y/%m/%d')
    end_date = datetime.strptime(end, '%Y/%m/%d')
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y/%m/%d'))
        current_date += timedelta(days=1)
    return date_list


dates = date_range(comix_date_start, comix_date_end)

'''
# for debugging
print(dates)
dates = ["2023/01/29", "2023/01/30", "2023/01/31"]
'''
# Part 1 gets the list of links to the images

comics_url = []

# Create a download_folder directory, if it doesn't exist. This is where we will save the files

if not os.path.isdir(download_folder):
     os.mkdir(download_folder)


def fetch_url(date):
    url = f"https://www.gocomics.com/{comics_name}/{date}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    container = soup.find("div", class_="comic__container")
    img = container.find("img", class_="lazyload img-fluid")
    src = img["src"]
    comics_url.append(src)

# limit the number of simultaneous openings to 5
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = [executor.submit(fetch_url, date) for date in dates]

'''
print(comics_url)


# for debugging
comics_url = ['https://assets.amuniversal.com/bbae9e406978013bd934005056a9545d',
              'https://assets.amuniversal.com/bea2a9c06978013bd934005056a9545d',
              'https://assets.amuniversal.com/307b96d06316013bd77a005056a9545d']
              
# Part 2, saving files, having a reference list (comics_url)


The HTML response does not contain a title tag, so the script cannot retrieve the title of the comic. 
hence the list index is out of range and causes an error.
To fix this, I had to modify the code to handle cases where the title tag is not found in the HTML response.

also
The subdirectory "download_folder" uses double backslashes (\\) to separate the path components, 
which is the correct format for Windows paths.

'''
def download_comic(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            title = response.text.split("<title>")
            if len(title) > 1:
                title = title[1].split("</title>")[0]
                # Fix the filename for Windows compatibility
                filename = f"{download_folder}\\{title}.gif".replace(':', '_').replace('/', '_').replace('\\', '_')
            else:
                filename = f"{download_folder}\\{url.split('/')[-1]}.gif"
            if not os.path.exists(filename):
                try:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                        print(f"Comic {title} successfully downloaded")
                        print()
                except Exception as e:
                    print(f"Error writing {filename}: {e}")
                    print()
            else:
                print(f"Comic {title} already exists")
                print()
        else:
            print(f"Error downloading {url}: status code {response.status_code}")
            print()
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Limit the number of simultaneous downloads to 2
semaphore = threading.Semaphore(2)

# Progress bar for download progress
pbar = tqdm.tqdm(total=len(comics_url))

threads = []
for url in comics_url:
    # Wait for the semaphore to be available before downloading a new comic
    semaphore.acquire()
    t = threading.Thread(target=download_comic, args=(url,), name=url)
    t.start()
    threads.append(t)
    # Release the semaphore after starting a new download
    semaphore.release()
    pbar.update(1)

# Wait for all threads to finish
for t in threads:
    t.join()

pbar.close()
