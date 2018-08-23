#!/usr/bin/env python
# encoding: UTF-8

from datetime import datetime, timedelta
import json

import requests

import sarpur
from sarpur import scraper, logger  # noqa
import util.player as player
from util.gui import GUI

INTERFACE = GUI(sarpur.ADDON_HANDLE, sarpur.BASE_URL)
EVENT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


def index():
    """
    The front page (i.e. the first one the user sees when opening the plugin)
    """

    INTERFACE.add_dir(u'Beinar útsendingar', 'view_live_index', '')
    INTERFACE.add_dir(u'RÚV', 'view_category', 'ruv')
    INTERFACE.add_dir(u'RÚV 2', 'view_category', 'ruv2')
    INTERFACE.add_dir(u'RÁS 1', 'view_category', 'ras1')
    INTERFACE.add_dir(u'RÁS 2', 'view_category', 'ras2')
    INTERFACE.add_dir(u'RÁS 3', 'view_category', 'ras3')
    INTERFACE.add_dir(u'Rondó', 'view_category', 'rondo')
    INTERFACE.add_dir(u'Hlaðvarp', 'view_podcast_index', '')
    # INTERFACE.add_dir(u'Leita', 'search', '')


def live_index():
    """
    List of available live streams
    """
    INTERFACE.add_item(u'RÚV', 'play_live', 'ruv')
    INTERFACE.add_item(u'RÚV 2', 'play_live', 'ruv2')
    INTERFACE.add_item(u'RÁS 1', 'play_live', 'ras1')
    INTERFACE.add_item(u'RÁS 2', 'play_live', 'ras2')
    INTERFACE.add_item(u'Rondó', 'play_live', 'rondo')


def play_url(url, name):
    """
    Play media on page (scrapes it to find it)

    :param url: The page url
    :param name: Text to display in media player
    """
    video_url = scraper.get_media_url(url)
    if video_url == -1:
        GUI.info_box(u"Vesen", u"Fann ekki upptöku")
    else:
        player.play(video_url, name)


def play_video(file, name):
    """
    Play video given only the filename

    :param file: playable file
    :param name: Text to display in media player
    :return:
    """
    player.play(file, name)


def play_live_stream(channel, name):
    """
    Play one of the live streams.

    :param channel: The channel/radio station
    :param name: Text to display in media player
    """
    url = scraper.get_live_url(channel)
    if url == -1:
        GUI.info_box(u"Vesen", u"Fann ekki straum")
    else:
        player.play(url, name)


def view_category(channel, date_string):
    """
    Display the available media in category

    :param channel: The channel/radio station
    :param date_string: Display media at this date. Format is %Y%m%d
    """

    if date_string.startswith('<<'):
        format = "<< %d.%m.%Y"
    elif date_string.endswith('>>'):
        format = "%d.%m.%Y >>"
    else:
        format = None
        date = datetime.today()

    if format:
        date = scraper.strptime(date_string, format)

    url = 'https://api.ruv.is/api/schedule/{0}/{1}/'.format(
        channel,
        date.strftime('%Y-%m-%d'),
    )
    shows = requests.get(url).json()

    if 'error' in shows:
        if 'message' in shows:
            GUI.info_box(u"Vesen", shows['error']['message'])
        else:
            GUI.info_box(u"Vesen", json.dumps(shows['error']))
        return

    day_before = date + timedelta(days=-1)
    next_day = date + timedelta(days=1)
    INTERFACE.add_dir(u"<< {0}".format(day_before.strftime("%d.%m.%Y")),
                      'view_category',
                      channel)
    INTERFACE.add_dir("{0} >>".format((next_day.strftime("%d.%m.%Y"))),
                      'view_category',
                      channel)

    for ev in shows['events']:
        showtime = scraper.strptime(ev['start_time'], EVENT_DATE_FORMAT)
        end_time = scraper.strptime(ev['end_time'], EVENT_DATE_FORMAT)
        in_progress = showtime <= datetime.now() < end_time
        duration = (end_time - showtime).seconds
        display_show_time = (
            in_progress and u"[COLOR blue]Í GANGI[/COLOR]" or
            showtime.strftime("%H:%M")
        )

        title = u"{1} - {0}".format(
            ev['title'],
            display_show_time,
        )
        original_title = ev.get('orginal_title')
        description = '\n'.join(ev.get('description', []))
        if original_title and description:
            plot = u"{0} - {1}".format(original_title, description)
        elif description:
            plot = description
        elif original_title:
            plot = original_title
        else:
            plot = u""

        image = ev.get('image', ev.get('default_image'))
        meta = {
            'TVShowTitle': title,
            'Premiered': showtime.strftime("%d.%m.%Y"),
            'Plot': plot,
            'Duration': duration,
            'fanart_image': image,
        }
        if 'episode_number' in ev:
            meta['Episode'] = ev['episode_number']
        if 'number_of_episodes' in ev:
            meta['TotalEpisodes'] = ev['number_of_episodes']

        has_passed = ev['program'] and ev['program']['episodes']
        is_available = ev['web_accessible'] and ev['program'] is not None
        is_playable = has_passed and is_available

        if in_progress:
            INTERFACE.add_item(title,
                               'play_live',
                               channel,
                               image=image,
                               extra_info=meta)

        elif is_playable:
            INTERFACE.add_item(title,
                               'play_file',
                               ev['program']['episodes'][0]['file'],
                               image=image,
                               extra_info=meta)
        else:
            INTERFACE.add_unselectable_item(
                title,
                image=image,
                extra_info=meta
            )


def podcast_index():
    """
    List all the podcasts.
    """
    for show in scraper.get_podcast_shows(sarpur.PODCAST_URL):
        INTERFACE.add_dir(show['name'],
                          'view_podcast_show',
                          show['url'],
                          image=show['img'])


def podcast_show(url, name):
    """
    List all the recordings in a podcast.

    :param url: The podcast url (xml/rss file)
    :param name: The name of the show
    """
    for recording in scraper.get_podcast_episodes(url):
        INTERFACE.add_item(recording['title'],
                           'play_video',
                           recording['url'],
                           extra_info=recording)


def search():
    query = INTERFACE.keyboard(u"Leita að efni")
    if not query:
        index()
    else:
        for show in scraper.search(query):
            INTERFACE.add_item(show['name'],
                               'play_url',
                               show['url'],
                               image=show['img'],
                               extra_info=show)
