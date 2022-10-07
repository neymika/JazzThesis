
import requests
from bs4 import BeautifulSoup

'''
Code editted from geeks for geeks: https://www.geeksforgeeks.org/downloading-files-web-using-python/
Need requests, bs4, html5lib. Use pip3 to install them.
'''

# specify the URL of the archive here
archive_url = "https://bushgrafts.com/midi/"

def get_midi_links():

    # create response object
    r = requests.get(archive_url)

    # create beautiful-soup object
    soup = BeautifulSoup(r.content,'html5lib')

    # find all links on web-page
    links = soup.findAll('a')
    midi_links = []

    for link in links:
        print(link)
        if link.get('href') is not None and link.get('href').endswith('mid'):
            midi_links.append(archive_url + link.get('href'))

    return midi_links


def download_midi_series(midi_links):

    for link in midi_links:

        '''iterate through all links in video_links
        and download them one by one'''

        # obtain filename by splitting url and getting
        # last string
        file_name = link.split('/')[-1]

        print( "Downloading file:%s"%file_name)

        # create response object
        r = requests.get(link, stream = True)

        # download started
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024*1024):
                if chunk:
                    f.write(chunk)

        print( "%s downloaded!\n"%file_name )

    print ("All midi files downloaded!")
    return


if __name__ == "__main__":

    # getting all midi links
    midi_links = get_midi_links()

    # download all midi files
    download_midi_series(midi_links)
