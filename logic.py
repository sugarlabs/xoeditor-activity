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


from result import ServerResult
import os
import urllib

class ServerLogic:
	def __init__(self, acty):
		self.acty = acty

	def doServerLogic(self, url, path, params):
		r = ServerResult()

		fileName = path[len(path)-1]
		if (fileName == "saveXo"):
			upXo = params[0][1]
			upXo = urllib.unquote(upXo)
			xoFile = open(os.path.join(self.acty.journalPath, "xo-dude.xml"), 'w')
			xoFile.write(upXo)
			xoFile.close()
		else:
			localfile = open(os.path.join(self.acty.htmlPath, fileName), 'r')
			localdata = localfile.read()
			localfile.close()
			r.txt = localdata
			#todo: dynamic mime type for js and xml, etc.
			r.headers.append( ("Content-type", "text/xml") )

		return r