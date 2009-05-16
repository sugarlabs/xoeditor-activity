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


from sugar import network
import urlparse
import urllib
import posixpath

class Server(network.GlibTCPServer):
	def __init__(self, server_address, acty):
		self.acty = acty
		network.GlibTCPServer.__init__(self, server_address, RegHandler)

#RegHandler extends SimpleHTTPServer.py (in python 2.4)
class RegHandler(network.ChunkedGlibHTTPRequestHandler):
	def do_POST( self ):
		self.translate_path()

	def do_GET( self ):
		self.translate_path()

	def translate_path(self):
		urlp = urlparse.urlparse(self.path)

		urls = urlp[2]
		urls = posixpath.normpath(urllib.unquote(urls))
		urlPath = urls.split('/')
		urlPath = filter(None, urlPath)

		params = urlp[4]
		parama = []
		allParams = params.split('&')
		for i in range (0, len(allParams)):
			parama.append(allParams[i].split('='))

		result = self.server.acty.slogic.doServerLogic(self.path,urlPath,parama)
		self.send_response(200)
		for i in range (0, len(result.headers)):
			self.send_header( result.headers[i][0], result.headers[i][1] )
		self.end_headers()
		self.wfile.write( result.txt )