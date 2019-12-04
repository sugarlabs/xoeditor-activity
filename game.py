# -*- coding: utf-8 -*-
# Copyright (c) 2012 Walter Bender
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
from gi.repository import Gtk, Gdk, GdkPixbuf
import cairo

from math import atan2, sin, cos, sqrt, pi

import logging
_logger = logging.getLogger('xo-editor-activity')

try:
    from sugar3.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0
from sugar3.graphics.xocolor import colors

from sprites import Sprites, Sprite


class Game():
    ''' OLPC XO man color changer designed in memory of Nat Jacobson '''

    def __init__(self, canvas, parent=None, mycolors=['#A0FFA0', '#FF8080']):
        self._activity = parent
        self.colors = [mycolors[0]]
        self.colors.append(mycolors[1])

        self._canvas = canvas
        if parent is not None:
            parent.show_all()
            self._parent = parent

        self._canvas.connect("draw", self.__draw_cb)
        self._canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._canvas.connect("button-press-event", self._button_press_cb)
        self._canvas.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._canvas.connect('button-release-event', self._button_release_cb)
        self._canvas.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self._canvas.connect("motion-notify-event", self._mouse_move_cb)

        self._width = Gdk.Screen.width()
        self._height = Gdk.Screen.height() - GRID_CELL_SIZE
        self._scale = self._width / 1200.

        self.press = None
        self.dragpos = [0, 0]
        self.startpos = [0, 0]

        self._dot_cache = {}
        self._xo_cache = {}

        self._radius = 22.5
        self._stroke_width = 9.5

        # Generate the sprites we'll need...
        self._sprites = Sprites(self._canvas)
        self._sprites.set_delay(True)
        self._dots = []
        self._xo_man = None
        self._generate_bg('#FFF')

        # First dot, starting angle
        self._cxy = [self._width / 2, self._height / 2]
        self._xy = [self._width / 2 + 120 * self._scale,
                    self._height / 2 - self._radius * self._scale]
        self._angle = 0
        self._dot_size_plus = self._radius * 3 * self._scale
        self._min = -self._dot_size_plus / 3
        self._max = self._height - (self._dot_size_plus / 2.2)

        self._zones = []
        self._calc_zones()
        self._generate_spiral()
        self._sprites.draw_all()

    def _calc_zones(self):
        for color in colors:
            rgb1 = _from_hex(color[0])
            rgb2 = _from_hex(color[1])
            dv = _contrast(rgb1, rgb2)
            dh = _delta_hue(rgb1, rgb2)
            self._zones.append(_zone(dv, dh))

    def _calc_next_dot_position(self):
        ''' calculate spiral coordinates '''
        dx = self._xy[0] - self._cxy[0]
        dy = self._xy[1] - self._cxy[1]
        r = sqrt(dx * dx + dy * dy)
        c = 2 * r * pi
        a = atan2(dy, dx)
        da = (self._dot_size_plus / c) * 2 * pi
        a += da
        r += self._dot_size_plus / (c / self._dot_size_plus)
        self._xy[0] = r * cos(a) + self._cxy[0]
        self._xy[1] = r * sin(a) + self._cxy[1]
        if self._xy[1] < self._min or self._xy[1] > self._max:
            self._calc_next_dot_position()

    def _generate_spiral(self):
        ''' Make a new set of dots for a sprial '''
        for z in range(4):
            for i in range(len(colors)):
                if self._zones[i] == z:
                    self._dots.append(
                        Sprite(self._sprites, self._xy[0], self._xy[1],
                               self._new_dot(colors[i])))
                    self._dots[-1].type = i
                    self._calc_next_dot_position()
        if self._xo_man is None:
            x = 510 * self._scale
            y = 280 * self._scale
            self._xo_man = Sprite(self._sprites, x, y,
                                  self._new_xo_man(self.colors))
            self._xo_man.type = None

    def move_dot(self, i, x, y):
        self._dots[i].move((x, y))

    def get_dot_xy(self, i):
        return self._dots[i].get_xy()

    def move_xo_man(self, x, y):
        self._xo_man.move((x, y))

    def get_xo_man_xy(self):
        return self._xo_man.get_xy()

    def rotate(self):
        x, y = self._dots[0].get_xy()
        for i in range(len(colors) - 1):
            self._dots[i].move(self._dots[i + 1].get_xy())
        self._dots[-1].move((x, y))

    def _generate_bg(self, color):
        ''' a background color '''
        self._bg = Sprite(self._sprites, 0, 0, self._new_background(color))
        self._bg.set_layer(0)
        self._bg.type = None

    def adj_background(self, color):
        ''' Change background '''
        self._bg.set_image(self._new_background(color))
        self._bg.set_layer(0)

    def _button_press_cb(self, win, event):
        win.grab_focus()
        x, y = list(map(int, event.get_coords()))
        self.dragpos = [x, y]

        spr = self._sprites.find_sprite((x, y))
        if spr is None or spr == self._bg:
            return
        self.startpos = spr.get_xy()
        self.press = spr

    def _mouse_move_cb(self, win, event):
        """ Drag a rule with the mouse. """
        if self.press is None:
            self.dragpos = [0, 0]
            return True
        win.grab_focus()
        x, y = list(map(int, event.get_coords()))
        dx = x - self.dragpos[0]
        dy = y - self.dragpos[1]
        self.press.move_relative((dx, dy))
        self.dragpos = [x, y]

    def _button_release_cb(self, win, event):
        if self.press is None:
            return True
        if _distance(self.press.get_xy(), self.startpos) < 20:
            if isinstance(self.press.type, int):
                self.i = self.press.type
                self._new_surface()
            self.press.move(self.startpos)
        self.press = None

    def _new_surface(self):
        self.colors[0] = colors[self.i][0]
        self.colors[1] = colors[self.i][1]
        self._xo_man.set_image(self._new_xo_man(colors[self.i]))
        self._xo_man.set_layer(100)

    def __draw_cb(self, canvas, cr):
        self._sprites.redraw_sprites(cr=cr)

    def do_expose_event(self, event):
        ''' Handle the expose-event by drawing '''
        # Restrict Cairo to the exposed area
        cr = self._canvas.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
                     event.area.width, event.area.height)
        cr.clip()
        # Refresh sprite list
        self._sprites.redraw_sprites(cr=cr)

    def _destroy_cb(self, win, event):
        Gtk.main_quit()

    def _new_dot(self, color):
        ''' generate a dot of a color color '''
        if True:  # not color in self._dot_cache:
            self._stroke = color[0]
            self._fill = color[1]
            self._svg_width = int(60 * self._scale)
            self._svg_height = int(60 * self._scale)
            pixbuf = svg_str_to_pixbuf(
                self._header() +
                '<circle cx="%f" cy="%f" r="%f" stroke="%s" fill="%s" \
stroke-width="%f" visibility="visible" />' % (
                    30 * self._scale, 30 * self._scale,
                    self._radius * self._scale, self._stroke,
                    self._fill, self._stroke_width * self._scale) +
                self._footer())

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                         self._svg_width, self._svg_height)
            context = cairo.Context(surface)
            Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
            context.rectangle(0, 0, self._svg_width, self._svg_height)
            context.fill()
            # self._dot_cache[color] = surface

        return surface  # self._dot_cache[color]

    def _new_background(self, color):
        ''' Background color '''
        self._svg_width = int(self._width)
        self._svg_height = int(self._height)
        string = \
            self._header() + \
            '<rect width="%f" height="%f" x="%f" \
y="%f" fill="%s" stroke="none" visibility="visible" />' % (
                self._width, self._height, 0, 0, color) + \
            self._footer()
        pixbuf = svg_str_to_pixbuf(string)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     self._svg_width, self._svg_height)
        context = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.rectangle(0, 0, self._svg_width, self._svg_height)
        context.fill()
        return surface

    def _new_xo_man(self, color):
        ''' generate a xo-man of a color color '''
        if True:  # not color in self._xo_cache:
            self._stroke = color[0]
            self._fill = color[1]
            self._svg_width = int(240. * self._scale)
            self._svg_height = int(260. * self._scale)
            string = \
                self._header() + \
                '<g>' + \
                '<g id="XO">' + \
                '<path id="Line1" d="M%f,%f C%f,%f %f,%f %f,%f" stroke="%s" \
stroke-width="%f" stroke-linecap="round" fill="none" visibility="visible" />' \
% (
                    165.5 * self._scale, 97 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    74.5 * self._scale, 188 * self._scale,
                    self._stroke, 37 * self._scale) + \
                '<path id="Line2" d="M%f,%f C%f,%f %f,%f %f,%f" stroke="%s" \
stroke-width="%f" stroke-linecap="round" fill="none" visibility="visible" />' \
% (
                    165.5 * self._scale, 188 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    74.5 * self._scale, 97 * self._scale,
                    self._stroke, 37 * self._scale) + \
                '<path id="Fill1" d="M%f,%f C%f,%f %f,%f %f,%f" stroke="%s" \
stroke-width="%f" stroke-linecap="round" fill="none" visibility="visible" />' \
% (
                    165.5 * self._scale, 97 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    74.5 * self._scale, 188 * self._scale,
                    self._fill, 17 * self._scale) + \
                '<path id="Fill2" d="M%f,%f C%f,%f %f,%f %f,%f" stroke="%s" \
stroke-width="%f" stroke-linecap="round" fill="none" visibility="visible" />' \
% (
                    165.5 * self._scale, 188 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    120 * self._scale, 140.5 * self._scale,
                    74.5 * self._scale, 97 * self._scale,
                    self._fill, 17 * self._scale) + \
                '<circle id="Circle" cx="%f" cy="%f" r="%f" \
fill="%s" stroke="%s" stroke-width="%f" visibility="visible" />' % (
                    120 * self._scale, 61.5 * self._scale,
                    27.5 * self._scale,
                    self._fill, self._stroke, 11 * self._scale) + \
                '</g></g>' + \
                self._footer()
            pixbuf = svg_str_to_pixbuf(string)

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                         self._svg_width, self._svg_height)
            context = cairo.Context(surface)
            Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
            context.rectangle(0, 0, self._svg_width, self._svg_height)
            context.fill()
            # self._xo_cache[color] = surface
        return surface  # self._xo_cache[color]

    def _header(self):
        return '<svg\n' + 'xmlns:svg="http:#www.w3.org/2000/svg"\n' + \
            'xmlns="http://www.w3.org/2000/svg"\n' + \
            'xmlns:xlink="http://www.w3.org/1999/xlink"\n' + \
            'version="1.1"\n' + 'width="' + str(self._svg_width) + '"\n' + \
            'height="' + str(self._svg_height) + '">\n'

    def _footer(self):
        return '</svg>\n'


def svg_str_to_pixbuf(svg_string):
    """ Load pixbuf from SVG string """
    pl = GdkPixbuf.PixbufLoader.new_with_type('svg')
    pl.write(svg_string.encode())
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf


def _from_hex(num):
    r = float.fromhex('0x' + num[1:3])
    g = float.fromhex('0x' + num[3:5])
    b = float.fromhex('0x' + num[5:])
    return [r, g, b]


def _to_hex(rgb):
    return('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))


def _contrast(rgb1, rgb2):
    v1 = float(rgb1[0]) * 0.3 + float(rgb1[1]) * 0.6 + float(rgb1[2]) * 0.1
    v2 = float(rgb2[0]) * 0.3 + float(rgb2[1]) * 0.6 + float(rgb2[2]) * 0.1
    return abs(v2 - v1)


def _hue(rgb):
    a = 0.5 * (2.0 * rgb[0] - rgb[1] - rgb[2])
    b = 0.87 * (rgb[1] - rgb[2])
    h = atan2(b, a)
    return h * 180 / pi


def _delta_hue(rgb1, rgb2):
    h1 = _hue(rgb1)
    h2 = _hue(rgb2)
    return abs(h2 - h1)


def _zone(dv, dh):
    if dh < 75:
        zone = 0
    elif dh > 150:
        zone = 1
    else:
        zone = 2
    if dv > 48:
        zone += 1
    return zone


def _distance(pos1, pos2):
    return sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) +
                (pos1[1] - pos2[1]) * (pos1[1] - pos2[1]))
