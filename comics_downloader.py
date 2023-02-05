from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os
import threading
from tqdm import tqdm


comics_name = 'garfield'  # should be the same as in the url https://www.gocomics.com/garfield/
# IMPORTANT. The script is tested on a period of up to 2 months.
# In the case of specifying a period of more than 60 months may be blocked by the server
comics_date_start = "2023/01/29"  # beginning of the period in the format YEAR/MONTH/DAY ('%Y/%m/%d')
comics_date_end = "2023/01/31"  # end of period format YEAR/MONTH/DAY ('%Y/%m/%d')
download_folder = "garfield_comics"  # folder to store downloaded files
format_img = 'jpg'  # like png, gif, jpg, etc.
num_of_threads = 5  # maximum number of simultaneous downloads


def date_range(start, end):
    '''
    Returns a dictionary of dates in the format YEAR/MONTH/DAY as keys and corresponding URL of the comics for the respective date as values.
    The function uses the datetime and timedelta modules to generate a range of dates
    from the start date to the end date and constructs the URL for each date.
    It then uses the requests module to make a GET request to the URL and retrieves the HTML content.
    The BeautifulSoup library is used to parse the HTML and extract the URL of the image for the comic strip.
    '''
    start_date = datetime.strptime(start, '%Y/%m/%d')
    end_date = datetime.strptime(end, '%Y/%m/%d')
    current_date = start_date
    dictionary_data = {}
    while current_date <= end_date:
        date_str = current_date.strftime('%Y/%m/%d')
        key = date_str
        value = f"https://www.gocomics.com/{comics_name}/{date_str}"
        res = requests.get(value)
        soup = BeautifulSoup(res.text, "html.parser")
        container = soup.find("div", class_="comic__container")
        img = container.find("img", class_="lazyload img-fluid")
        src = img["src"]
        dictionary_data[key] = src
        current_date += timedelta(days=1)
    return dictionary_data



def download_comic(key, url, bar):
    """
    Downloads a comic strip for a given date.
    The function takes in a date string, URL of the comic strip, and a progress bar object.
    It generates the filename for the comic strip using the date string and the format YEAR_MONTH_DAY.format_img(gif/png)
    The function checks if the file already exists, and if it does, skips the download.
    If the file does not exist, the function uses the requests module to make a GET request to the URL and retrieves the image content.
    The image content is then written to a file using the filename.
    """
    filename = key.replace('/', '_').replace(':', '_').replace('\\', '_') + f'.{format_img}'
    full_path = os.path.join(download_folder, filename)
    if os.path.exists(full_path):
        print(f"{filename} already exists, skipping download")
        return

    response = requests.get(url)
    if response.status_code == 200:
        with open(full_path, "wb") as f:
            f.write(response.content)
        print(f"{filename} has been downloaded successfully")
        bar.update(1)
    else:
        print(f"Error downloading {filename}, status code: {response.status_code}")


def download_threads(threads):
    """
    Starts and joins a batch of threads.
    The function takes in a list of thread objects and starts num_of_threads number of threads at a time.
    It waits for all the threads to finish before starting the next batch.
    """
    for i in range(0, len(threads), num_of_threads):
        for j in range(i, min(i + num_of_threads, len(threads))):
            threads[j].start()
        for j in range(i, min(i + num_of_threads, len(threads))):
            threads[j].join()



def main():
    """
    The main function that ties everything together.
    The function creates a dictionary of comic strips using the date_range function.
    If the download folder does not exist, it creates the folder.
    It initializes a progress bar using the tqdm library and creates a list of threads using the download_comic function.
    The function then uses the download_threads function to start and join the threads.
    The function prints a message indicating that all files have been downloaded successfully.
    """
    dictionary = date_range(comics_date_start, comics_date_end)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    threads = []
    bar = tqdm(total=len(dictionary))
    for key, value in dictionary.items():
        threads.append(threading.Thread(target=download_comic, args=(key, value, bar)))
    download_threads(threads)
    print("All files have been downloaded successfully")


if __name__ == "__main__":
    main()

"""
The construction if __name__ == "__main__": 
is a way to ensure that a Python script is only executed as the main program and not imported as a module into another script.

When a Python script is run, the __name__ special attribute is automatically set to "__main__". 
Therefore, if the script is being executed as the main program, __name__ will be equal to "__main__". 
If the script is being imported as a module into another script, __name__ will be set to the name of the module.

So, in this code, the main() function is only run if the script is executed as the main program, and not imported as a module.
"""
