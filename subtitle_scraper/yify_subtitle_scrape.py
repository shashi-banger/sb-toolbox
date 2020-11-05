import requests
from lxml import etree
from bs4 import BeautifulSoup
import urllib.parse as url_parse

class MetaData:
    def __init__(self):
        self.MediaTitle = ""
        self.SeasonNumber = None
        self.Year = ""
        self.DurationMin = ""
        self.EpisodeIdentifier = ""
        self.Genre = "" 
        self.SubtitleSource = "" # e.g. https://yts-subs.com/
        self.SubtitleUrl = ""
        self.ImdbUrl = ""
        self.Actors = "" # comma separated names of actors
        self.PlotSummary = ""
        self.SubtitleScrapeLink = ""


def dump_meta_data_to_xml(meta_data, out_xml_file):
    root = etree.Element("MediaMeta")
    media_title = etree.SubElement(root, "MediaTitle")
    media_title.text = meta_data.MediaTitle

    year = etree.SubElement(root, "Year")
    year.text = meta_data.Year

    genre = etree.SubElement(root, "Genre")
    genre.text = meta_data.Genre

    subtitle_source = etree.SubElement(root, "SubtitleSource")
    subtitle_source.text = meta_data.SubtitleSource

    subtitle_url = etree.SubElement(root, "SubtitleUrl")
    subtitle_url.text = meta_data.SubtitleUrl

    imdb_url = etree.SubElement(root, "ImdbUrl")
    imdb_url.text = meta_data.ImdbUrl

    actors = etree.SubElement(root, "Actors")
    actors.text = meta_data.Actors

    plot = etree.SubElement(root, "PlotSummary")
    plot.text = meta_data.PlotSummary

    et = etree.ElementTree(root)
    et.write(out_xml_file, xml_declaration=True, pretty_print=True)


def _get_imdb_url(soup):
    imdb_url = ""
    all_a = soup.find_all('a')

    for a in all_a:
        if a.text == "IMDB link":
            imdb_url = a.get('href')
            break
    return imdb_url


def _get_duration_year(movie_info_list):
    duration = ""
    year = ""
    for mi in movie_info_list:
        if mi.small.text == 'year':
            year = mi.text 
        elif mi.small.text == "min":
            duration = mi.text 
    return (duration, year)


def subtitle_page_scrape(s_url, meta_data):
    page_url_parts = url_parse.urlparse(s_url)
    page = requests.get(s_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    movie_desc = soup.find("div", {"class":"movie-desc"})

    print(movie_desc.get_text())

    meta_data.PlotSummary = movie_desc.text
    meta_data.ImdbUrl = _get_imdb_url(soup)

    year = soup.find("div", attrs={"id": "circle-score-year", "class": "circle", "data-info":"year"})
    meta_data.Year = year.get("data-text")

    subtitles_table = soup.find('tbody')
    
    for subtitle_entry in subtitles_table.find_all('tr'):
        sub_lang = subtitle_entry.find('span', {"class":"sub-lang"})
        if sub_lang.get_text().lower() == "english":
            download_cell = subtitle_entry.find('td', {"class":"download-cell"})
            download_path = download_cell.a.get('href').split('/')[-1] + ".zip"
            new_url = url_parse.ParseResult(scheme='https', 
                                        netloc="yifysubtitles.org", 
                                        path="/subtitle/" + download_path, 
                                        params='', query='', fragment='')
            subtitle_url = url_parse.urlunparse(new_url)
            print(subtitle_url)
            meta_data.SubtitleUrl = subtitle_url
            break
    return


def page_scrape(page_url):
    page_url_parts = url_parse.urlparse(page_url)
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    all_meta_data = []
    for link in soup.find_all(name='div', attrs={"class":'media-body'}):
        meta_data = MetaData()
        href = link.a.get('href')
        if href is None:
            href = ''

        try:
            media_title = link.find('h3', attrs={"class": "media-heading", "itemprop": "name"})
            meta_data.MediaTitle = media_title.text            
        except Exception as e:
             pass

        try:
            actors = link.find('span', attrs={"class": "movie-actors", "itemprop": "actors"})
            meta_data.Actors = actors.text            
        except Exception as e:
             pass

        try:
            movie_genre = link.find('div', attrs={'class': 'movie-genre', 'itemprop':'genre'})
            meta_data.Genre = movie_genre.text 
        except Exception as e:
             pass

        try:
            movie_info = link.find_all('span', attrs={"class": "movinfo-section"})
            (duration, year) = _get_duration_year(movie_info)
            meta_data.Year = year
            meta_data.DurationMin = duration
        except Exception as e:
             pass

        meta_data.SubtitleSource = "https://yts-subs.com/"

        new_url = url_parse.ParseResult(scheme=page_url_parts.scheme, 
                                        netloc=page_url_parts.netloc, 
                                        path=href, 
                                        params='', query='', fragment='')

        meta_data.SubtitleScrapeLink = url_parse.urlunparse( new_url)
        try:
            all_meta_data.append(meta_data)
        except Exception as e:
            print(new_url)
            raise e


    #print(links)
    return all_meta_data
    #for tag in soup.find_all():
    #    print(tag.name)

    
if __name__ == "__main__":
    url = "https://yts-subs.com/browse?page=2"
    page_meta_data = page_scrape(url)

    #url = "https://yts-subs.com/movie-imdb/tt0034167"
    subtitle_page_scrape(page_meta_data[0].SubtitleScrapeLink, page_meta_data[0])

    print(page_meta_data[0])

    dump_meta_data_to_xml(page_meta_data[0], "/tmp/1.xml")
