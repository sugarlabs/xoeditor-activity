# -*- coding: utf-8 -*-
# Copyright (c) 2012 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk
from gi.repository import Gio

import dbus

from sugar3.activity import activity
from sugar3 import profile

from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.alert import ConfirmationAlert, NotifyAlert
from sugar3.graphics.xocolor import colors

from toolbar_utils import button_factory, separator_factory

from gettext import gettext as _

from game import Game

import logging
_logger = logging.getLogger('xo-editor-activity')


class XOEditorActivity(activity.Activity):
    """ Change the XO colors """

    def __init__(self, handle):
        """ Initialize the toolbars and the game board """
        try:
            super(XOEditorActivity, self).__init__(handle)
        except dbus.exceptions.DBusException as e:
            _logger.error(str(e))

        self.nick = profile.get_nick_name()
        if profile.get_color() is not None:
            self.colors = profile.get_color().to_string().split(',')
        else:
            self.colors = ['#A0FFA0', '#FF8080']

        self.level = 0

        self._setup_toolbars()

        # Create a canvas
        canvas = Gtk.DrawingArea()
        canvas.set_size_request(Gdk.Screen.width(),
                                Gdk.Screen.height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        self._game = Game(canvas, parent=self, mycolors=self.colors)

        # Read the dot positions from the Journal
        for i in range(len(colors)):
            if 'x%d' % (i) in self.metadata and 'y%d' % (i) in self.metadata:
                self._game.move_dot(i, int(self.metadata['x%d' % (i)]),
                                    int(self.metadata['y%d' % (i)]))
        if 'xox' in self.metadata and 'xoy' in self.metadata:
            self._game.move_xo_man(int(self.metadata['xox']),
                                   int(self.metadata['xoy']))

    def _save_colors_cb(self, button=None):
        ''' Save the new XO colors. '''
        ''' We warn the user if they are going to save their selection '''
        alert = ConfirmationAlert()
        alert.props.title = _('Saving colors')
        alert.props.msg = _('Do you want to save these colors?')

        def _change_colors_alert_response_cb(alert, response_id, self):
            if response_id is Gtk.ResponseType.OK:
                _logger.debug('saving colors')
                self.remove_alert(alert)
                self._confirm_save()
            elif response_id is Gtk.ResponseType.CANCEL:
                _logger.debug('cancel save')
                self.remove_alert(alert)
        alert.connect('response', _change_colors_alert_response_cb, self)
        self.add_alert(alert)
        alert.show()

    def _confirm_save(self):
        ''' Called from confirmation alert '''
        settings = Gio.Settings('org.sugarlabs.user')
        settings.set_string('color', '%s,%s' % (
            self._game.colors[0], self._game.colors[1]))
        alert = NotifyAlert()
        alert.props.title = _('Saving colors')
        alert.props.msg = _('A restart is required before your new colors '
                            'will appear.')

        def _notification_alert_response_cb(alert, response_id, self):
            self.remove_alert(alert)
        alert.connect('response', _notification_alert_response_cb, self)
        self.add_alert(alert)
        alert.show()

    def write_file(self, file_path):
        for i in range(len(colors)):
            x, y = self._game.get_dot_xy(i)
            self.metadata['x%d' % (i)] = str(x)
            self.metadata['y%d' % (i)] = str(y)

        x, y = self._game.get_xo_man_xy()
        self.metadata['xox'] = str(x)
        self.metadata['xoy'] = str(y)

    def _setup_toolbars(self):
        """ Setup the toolbars. """

        self.max_participants = 1  # No sharing

        toolbox = ToolbarBox()
        # Activity toolbar
        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, 0)
        activity_button.show()

        self.set_toolbar_box(toolbox)
        toolbox.show()
        self.toolbar = toolbox.toolbar

        self._save_colors_button = button_factory(
            'save-colors', self.toolbar, self._save_colors_cb,
            tooltip=_('Save colors'))

        separator_factory(toolbox.toolbar, True, False)
        stop_button = StopButton(self)
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()
