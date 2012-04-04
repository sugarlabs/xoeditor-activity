# -*- coding: utf-8 -*-
#Copyright (c) 2012 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


import gtk
import gconf

from sugar.activity import activity
from sugar import profile
try:
    from sugar.graphics.toolbarbox import ToolbarBox
    _have_toolbox = True
except ImportError:
    _have_toolbox = False

if _have_toolbox:
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
from sugar.graphics.objectchooser import ObjectChooser
from sugar.graphics.alert import ConfirmationAlert, NotifyAlert

from toolbar_utils import button_factory, radio_factory, separator_factory

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
        except dbus.exceptions.DBusException, e:
            _logger.error(str(e))

        self.nick = profile.get_nick_name()
        if profile.get_color() is not None:
            self.colors = profile.get_color().to_string().split(',')
        else:
            self.colors = ['#A0FFA0', '#FF8080']

        self.level = 0

        self._setup_toolbars(_have_toolbox)

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        self._game = Game(canvas, parent=self, mycolors=self.colors)

    def _setup_toolbars(self, have_toolbox):
        """ Setup the toolbars. """

        self.max_participants = 1  # No sharing

        if have_toolbox:
            toolbox = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)

            toolbox.toolbar.insert(activity_button, 0)
            activity_button.show()

            self.set_toolbar_box(toolbox)
            toolbox.show()
            self.toolbar = toolbox.toolbar

        else:
            # Use pre-0.86 toolbar design
            games_toolbar = gtk.Toolbar()
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)
            toolbox.add_toolbar(_('Game'), games_toolbar)
            toolbox.show()
            toolbox.set_current_toolbar(1)
            self.toolbar = games_toolbar

        '''
        _rotate_button = button_factory(
            'view-refresh', self.toolbar, self._rotate_cb,
            tooltip=_('Rotate colors'))
        '''

        if _have_toolbox:
            separator_factory(toolbox.toolbar, True, False)

        self._save_colors_button = button_factory(
            'save-colors', self.toolbar, self._save_colors_cb,
            tooltip=_('Save colors'))

        if _have_toolbox:
            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbox.toolbar.insert(stop_button, -1)
            stop_button.show()

    def _save_colors_cb(self, button=None):
        ''' Save the new XO colors. '''
        ''' We warn the user if they are going to save their selection '''
        alert = ConfirmationAlert()
        alert.props.title = _('Saving colors')
        alert.props.msg = _('Do you want to save these colors?')

        def _change_colors_alert_response_cb(alert, response_id, self):
            if response_id is gtk.RESPONSE_OK:
                _logger.debug('saving colors')
                self.remove_alert(alert)
                self._confirm_save()
            elif response_id is gtk.RESPONSE_CANCEL:
                _logger.debug('cancel save')
                self.remove_alert(alert)

        alert.connect('response', _change_colors_alert_response_cb, self)
        self.add_alert(alert)
        alert.show()

    def _confirm_save(self):
        ''' Called from confirmation alert '''
        client = gconf.client_get_default()
        client.set_string('/desktop/sugar/user/color', '%s,%s' % (
                self._game.colors[0], self._game.colors[1]))
        alert = NotifyAlert()
        alert.props.title = _('Saving colors')
        alert.props.msg = _('A restart is required before your new colors will appear.')

        def _notification_alert_response_cb(alert, response_id, self):
            self.remove_alert(alert)

        alert.connect('response', _notification_alert_response_cb, self)
        self.add_alert(alert)
        alert.show()

    def _rotate_cb(self, button=None):
        self._game.rotate()
