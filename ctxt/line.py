
"""
Each line consists of a string and some logic
for handling multiple changes simultaneously.
"""
class Line:
	def __init__(self, text=u""):
		self.text = text
	
	"""
	Enable the conversion from lines to strings.
	"""
	def __unicode__(self):
		return self.text
