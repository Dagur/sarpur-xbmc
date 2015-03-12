#!/usr/bin/env python
# encoding: UTF-8

from urllib import quote_plus as quote

import xbmcgui
import xbmcplugin


class GUI(object):
    """
    A very simple class that wraps the interface functions in XBMC
    """

    def __init__(self, addon_handle, base_url):
        """
        :param addon_handle: An identifier that XBMC uses to identify the addon
                             (created in default.py)
        :param base_url: The root internal url used in all calls in the addon
        """
        self.addon_handle = addon_handle
        self.base_url = base_url

    def _add_dir(self, name, action_key, action_value, iconimage, is_folder,
                 extra_info=None):
        """
        Creates a link in xbmc.

        :param name: Name of the link
        :param action_key: Name of the action to take when link selected
        :param action_value: Parameter to use with the action
        :param iconimage: Icon to use for the link
        :param is_folder: Does the link lead to a folder or playable item

        """
        format_params = {
            "base_url": self.base_url,
            "key": quote(action_key),
            "value": quote(action_value),
            "name": quote(name.encode('utf-8'))
        }

        url = "{base_url}?action_key={key}&action_value={value}&name={name}".format(**format_params)

        list_item = xbmcgui.ListItem(name,
                                    iconImage=iconimage,
                                    thumbnailImage='')
        info_labels = {"Title": name}
        if extra_info:
            info_labels.update(extra_info)

        list_item.setInfo(type="Video", infoLabels=info_labels)

        xbmcplugin.addDirectoryItem(
            handle=self.addon_handle,
            url=url,
            listitem=list_item,
            isFolder=is_folder)

    def add_dir(self, name, action_key, action_value,
               iconimage='DefaultFolder.png'):
        """
        Create folder (wrapper function for _addDir).

        :param name: The name of the folder
        :param action_key: Action to take
        :param action_value: Parameter to action
        :iconimage: Image to use with the folder
        """
        self._add_dir(name,
                     action_key,
                     action_value,
                     iconimage,
                     is_folder=True)

    def add_item(self, name, action_key, action_value,
                iconimage='DefaultMovies.png', extra_info=None):
        """
        Create link to playable item (wrapper function for _addDir).

        :param name: The name of the folder
        :param action_key: Action to take
        :param action_value: Parameter to action
        :iconimage: Image to use for the item
        """
        self._add_dir(name,
                     action_key,
                     action_value,
                     iconimage,
                     is_folder=False,
                     extra_info=extra_info)

    @staticmethod
    def infobox(title, message):
        """
        Display a pop up message.

        :param title: The title of the pop up window
        :param message: Message you want to display to the user
        """
        xbmcgui.Dialog().ok(title, message)
