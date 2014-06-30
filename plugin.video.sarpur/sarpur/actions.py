#!/usr/bin/env python
# encoding: UTF-8


import sarpur
import scraper
from sarpur.cached import Categories
from util.gui import GUI


gui = GUI(sarpur.ADDON_HANDLE, sarpur.BASE_URL)
cats = Categories()

def index():
    """ The front page (i.e. the first one the user sees when opening the plugin) """

    for tab in cats.tabs:
        title = tab[0].encode('utf-8')
        url = tab[1].encode('utf-8')
        gui.addDir(title, 'view_tab', url)

    for i, channel in enumerate(cats.showtree):
        title = '{0} Þættir'.format(channel['name'].encode('utf-8'))
        gui.addDir(title, 'view_channel_index', i)

    gui.addDir('Hlaðvarp', 'hladvarp', '')
    gui.addDir('Bein úttsending RÚV', 'play_live', 'ruv')

def channel_index(channel):
    for i, category in enumerate(cats.showtree[channel].get('categories')):
        gui.addDir(category['name'].encode('utf-8'),
                   'view_channel_category',
                   "{0};{1}".format(channel,i))

def channel_category(channel, category):
    for show in cats.showtree[channel]['categories'][category]['shows']:
        name, url = show
        if url[0] == '/':
            url = 'http://dagskra.ruv.is%s' % url
        gui.addDir(name.encode('utf-8'), 'view_channel_category_show', url.encode('utf-8'))

def channel_category_show(url, show_name):
    episodes = scraper.get_episodes(url)
    if not episodes:
        gui.infobox("Engar upptökur", "Engin upptaka fannst")
    else:
        for episode in episodes:
            episode_name, url = episode
            name = "{0} - {1}".format(show_name, episode_name.encode('utf-8'))
            gui.addItem(name, 'play', url)

def play(url, name):
    (playpath, rtmp_url, swfplayer) = scraper.get_stream_info(url)
    gui.play(playpath, swfplayer, rtmp_url, url, name)

def tab_index(url):
    pageurl = 'http://www.ruv.is{0}'.format(url)
    print pageurl
    episodes = scraper.get_tab_items(pageurl)
    if not episodes:
        gui.infobox("Engar upptökur", "Engin upptaka fannst")
    else:
        for episode in episodes:
            episode_name, url = episode
            gui.addItem(episode_name.encode('utf-8'), 'play', url.encode('utf-8'))

