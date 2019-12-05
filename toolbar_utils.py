# -*- coding: utf-8 -*-
# Copyright (c) 2011, Walter Bender
# Port To GTK3:
# Ignacio Rodriguez <ignaciorodriguez@sugarlabs.org>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


from gi.repository import Gtk

from sugar3.graphics.toolbutton import ToolButton


def button_factory(icon_name, toolbar, callback, cb_arg=None, tooltip=None,
                   accelerator=None):
    '''Factory for making tooplbar buttons'''
    button = ToolButton(icon_name)
    if tooltip is not None:
        button.set_tooltip(tooltip)
    button.props.sensitive = True
    if accelerator is not None:
        button.props.accelerator = accelerator
    if cb_arg is not None:
        button.connect('clicked', callback, cb_arg)
    else:
        button.connect('clicked', callback)
    if hasattr(toolbar, 'insert'):  # the main toolbar
        toolbar.insert(button, -1)
    else:  # or a secondary toolbar
        toolbar.props.page.insert(button, -1)
    button.show()
    return button


def separator_factory(toolbar, expand=False, visible=True):
    ''' add a separator to a toolbar '''
    separator = Gtk.SeparatorToolItem()
    separator.props.draw = visible
    separator.set_expand(expand)
    if hasattr(toolbar, 'insert'):  # the main toolbar
        toolbar.insert(separator, -1)
    else:  # or a secondary toolbar
        toolbar.props.page.insert(separator, -1)
    separator.show()
