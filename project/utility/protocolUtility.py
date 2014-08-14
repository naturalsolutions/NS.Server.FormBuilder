import glob
import os
import xml.dom.minidom

class ProtocolUtility (object):

	XMLRepository = os.path.dirname(os.path.abspath(__file__)) + "\\..\\XMLRepository\\"

	@staticmethod
	def writeProtocol (name, content, current):
		# if directory not exists we create it
		if not os.path.isdir (XMLRepository + name):
			os.mkdir (XMLRepository + name)
		path    = str(XMLRepository +  name + '/' + current + '.xml')
		f       = open (path, 'w')
		prettyXml = xml.dom.minidom.parseString (content).toprettyxml()
		f.write (prettyXml)
		f.close()