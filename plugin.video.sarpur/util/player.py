#!/usr/bin/env python
# encoding: UTF-8

import xbmc
import xbmcgui


def play(url, name):
    """
    .. py:function:: play(url)

    Play audio or video on a given url"

    :param url: Full url of the video
    :param name: Stream name
    """

    xbmc.Player().play(url, xbmcgui.ListItem(name))


def play_stream(playpath, sfwplayer, rtmp_url, url, name):
    """
    .. py:function:: play_stream(playpath, sfwplayer, rtmp_url, url, name)

    Play flash videos in XBMC

    :param playpath:
    :param sfwplayer: Path to the player on the page
    :param rtmp_url: URL to the actual video
    :param url: URL of the page where the flash player is
    :param name: Name of the video
    """
    item = xbmcgui.ListItem(name)
    item.setProperty("PlayPath", playpath)
    item.setProperty("SWFPlayer", sfwplayer)
    item.setProperty("PageURL", url)
    xbmc.Player().play(rtmp_url, item)

