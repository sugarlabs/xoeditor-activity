#!/usr/bin/env python
#Copyright (c) 2007, Media Modifications Ltd.

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import gtk
import gobject
import os

from sugar.activity import activity
from webviewer import WebViewer
from server import Server
from logic import ServerLogic
from result import ServerResult

httpPort = 8889
title = "xo Editor"
initHtml = "xo-color.xml"

class xoEditorActivity(activity.Activity):
	def __init__(self, handle):
		activity.Activity.__init__(self, handle)
		self.set_title( title )

		#wait a moment so that our debug console capture mistakes
		gobject.idle_add(self._initme, None)

	def _initme( self, userdata=None ):
		self.basePath = activity.get_bundle_path()
		self.htmlPath = os.path.join(self.basePath, "html")
		self.journalPath = os.path.join(os.path.expanduser("~"), "Journal", title)
		if (not os.path.exists(self.journalPath)):
			os.makedirs(self.journalPath)

		#add sharing callback here
		#self.connect( "shared", self._shared_cb )

		#this includes the default sharing tab
		toolbox = activity.ActivityToolbox(self)
		self.set_toolbox(toolbox)
		toolbox.show()

		#add components
		self.browser = WebViewer( )
		self.set_canvas(self.browser)
 		self.browser.show()

		#fire up the web engine, spiderman!
		self.slogic = ServerLogic(self);
		self.server = Server( ("",httpPort), self )
		self.browser.load_uri( "http://localhost:" + str(httpPort) + "/" + initHtml )

		#when the party's over, turn out the lights, turn out the lights
		self.connect("destroy", self.destroy)
		return False

	def destroy(self, *args):
		gtk.main_quit()
