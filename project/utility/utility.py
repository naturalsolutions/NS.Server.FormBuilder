from xml.etree  import ElementTree

class XMLUtiliy(object):

	@staticmethod
	def checkXML (XMLContent):
		try:
			x = ElementTree.fromstring(content)
		except:
			raise Exception("XML Content is not valid")
