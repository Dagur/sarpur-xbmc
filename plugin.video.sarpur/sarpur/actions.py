#!/usr/bin/env python
# encoding: UTF-8
import json

import sarpur
import time
from sarpur import scraper
import util.player as player
from util.gui import GUI
from datetime import datetime, timedelta
import requests
import xbmcgui

INTERFACE = GUI(sarpur.ADDON_HANDLE, sarpur.BASE_URL)


def index():
    """
    The front page (i.e. the first one the user sees when opening the plugin)
    """

    INTERFACE.add_dir(u'RÚV', 'view_category', '1')
    INTERFACE.add_dir(u'RÚV Íþróttir', 'view_category', '10')
    INTERFACE.add_dir(u'RÁS 1', 'view_category', '2')
    INTERFACE.add_dir(u'RÁS 2', 'view_category', '3')
    INTERFACE.add_dir(u'Rondó', 'view_category', 'rondo')
    INTERFACE.add_dir(u'Krakkasarpurinn', 'view_category', 'born')
    #INTERFACE.add_item('Bein útsending RÚV', 'play_live', 'ruv')
    #INTERFACE.add_item('Bein útsending RÁS 1', 'play_live', 'ras1')
    #INTERFACE.add_item('Bein útsending RÁS 2', 'play_live', 'ras2')
    #INTERFACE.add_item('Bein útsending Rondó', 'play_live', 'rondo')
    #INTERFACE.add_dir(u'Hlaðvarp', 'view_podcast_index', '')


def play_url(url, name):
    """
    Plays videos (and audio) other than live streams and podcasts.

    :param url: The page url
    :param name: The name of the item to play
    """
    video_url = scraper.get_media_url(url)
    if video_url == -1:
        GUI.infobox(u"Vesen", u"Fann ekki upptöku")
    else:
        player.play(video_url, name)


def play_video(file, name):
    """

    :param url:
    :param name:
    :return:
    """
    url =  u"http://smooth.ruv.cache.is/opid/{0}".format(file)
    r = requests.head(url)

    if r.status_code != 200:
        url =  u"http://smooth.ruv.cache.is/lokad/{0}".format(file)

    player.play(url, name)


def play_podcast(url):
    """
    Plays podcast

    :param url: The file url (this can be any file that xbmc can play)
    """

    player.play(url)


def play_live_stream(category_id, name):
    """
    Play one of the live streams.

    :param category_id: The name of the stream (defined in LIVE_URLS in __init__.py)
    """
    url = sarpur.LIVE_URLS.get(category_id)
    player.play(url, name)


def view_category(category_id, date_string):

    if date_string.startswith('<<'):
        format = "<< %d.%m.%Y"
    elif date_string.endswith('>>'):
        format = "%d.%m.%Y >>"
    else:
        format = None
        date = datetime.today()

    if format:
        try:
            date = datetime.strptime(date_string, format)
        except TypeError:
            # Bugfix for bug that doesn't make sense
            # http://forum.kodi.tv/showthread.php?tid=112916
            date = datetime(*(time.strptime(date_string, format)[0:6]))

    url = "http://www.ruv.is/sarpur/app/json/{0}/{1}".format(category_id, date.strftime("%Y%m%d"))
    shows = json.loads(requests.get(url).content)

    day_before = date + timedelta(days=-1)
    next_day = date + timedelta(days=1)
    INTERFACE.add_dir(u"<< {0}".format(day_before.strftime("%d.%m.%Y")),
                      'view_category',
                      category_id)
    INTERFACE.add_dir("{0} >>".format((next_day.strftime("%d.%m.%Y"))),
                      'view_category',
                      category_id)

    for show in shows['events']:
        ev = show['event']
        showtime = datetime.fromtimestamp(float(ev['start_time']))
        end_time = datetime.fromtimestamp(float(ev['end_time']))
        in_progress = showtime < datetime.now() < end_time
        duration = unicode(end_time - showtime)[2:4]

        title = u"{1} - {0}".format(
            ev['title'],
            in_progress and u"[COLOR blue]Í GANGI[/COLOR]" or showtime.strftime("%H:%M"))
        original_title = ev.get('orginal_title')
        description = ev.get('description', '').strip()
        if original_title and description:
            plot = u"{0} - {1}".format(original_title, description)
        elif description:
            plot = description
        elif original_title:
            plot = original_title
        else:
            plot = u""

        meta = {
            'TVShowTitle': title,
            'Episode': ev['episode_number'],
            'Premiered': showtime.strftime("%d.%m.%Y"),
            'TotalEpisodes': ev['number_of_episodes'],
            'Plot': plot,
            'Duration': duration,
            'fanart_image': ev.get('picture')
        }

        if in_progress:
            INTERFACE.add_item(title,
                               'play_live',
                               category_id,
                               iconimage=ev.get('picture'),
                               extra_info=meta)

        elif ev.get('media'):
            INTERFACE.add_item(title,
                               'play_file',
                               ev.get('media'),
                               iconimage=ev.get('picture'),
                               extra_info=meta)
        else:
            INTERFACE.add_item(title,
                               'play_url',
                               ev.get('url'),
                               iconimage=ev.get('picture'),
                               extra_info=meta)

def view_group(rel_url):
    """
    List items on one of the groups (flokkur tab) on sarpurinn.

    :param rel_url: Relative url to the flokkur

    """
    full_url = 'http://www.ruv.is/sarpurinn{0}'.format(rel_url)
    for video in scraper.get_videos(full_url):
        name, url = video
        INTERFACE.add_item(name.encode('utf-8'), 'play', url.encode('utf-8'))


def podcast_index():
    """
    List all the podcasts.
    """
    for show in scraper.get_podcast_shows(sarpur.PODCAST_URL):
        name, url = show
        INTERFACE.add_dir(name.encode('utf-8'), 'view_podcast_show', url)


def podcast_show(url, name):
    """
    List all the recordings for a podcast show.

    :param url: The podcast url (xml file)
    :param name: The name of the show
    """
    for recording in scraper.get_podcast_episodes(url):
        date, url = recording
        title = "{0} - {1}".format(name, date.encode('utf-8'))
        INTERFACE.add_item(title, 'play_podcast', url.encode('utf-8'))
