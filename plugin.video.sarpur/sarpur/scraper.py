#!/usr/bin/env python
# encoding: UTF-8

import requests
from bs4 import BeautifulSoup


def get_document(url):
    """
    Downloads url and returns a BeautifulSoup object

    :param url: An url
    :return BeautifulSoup "document"
    """
    req = requests.get(url)
    doc = BeautifulSoup(req.content, "html.parser")
    return doc


def get_media_url(page_url):
    """
    Find the url to the MP4/MP3 on a page

    :param page_url: Page to find the url on
    :return: url
    """

    doc = get_document(page_url)
    sources = [tag['jw-src'] for tag in doc.find_all('source') if tag.has_attr('jw-src')]
    if len(sources) == 0:
        return -1

    return u"http://smooth.ruv.cache.is/{0}".format(sources[0][4:])


def get_podcast_shows(url):
    """
    Gets the names and rss urls of all the podcasts (shows)

    :param url: The url to the podcast index
    :return A list of 2-tuples with show name and rss url

    """
    doc = get_document(url)
    shows = []

    for show in doc.select("ul .hladvarp-info"):
        title = show.select('li h4')[0].text
        show_url = show.select("li a[href*=http]")[0].get('href')
        shows.append((title, show_url))

    return shows


def get_podcast_episodes(url):
    """
    Gets the items from the rss feed

    :param url: Get all the playable items in podcast rss
    :return a list of 2-tuples with airdate and media url

    """
    doc = get_document(url)
    episodes = []

    for item in doc.find_all("guid"):
        url = item.text
        date = item.select('~ pubdate')[0].text
        episodes.append((date, url))

    return episodes
