# A class that's not really used

class Line:
	"""
Each line consists of a string and some logic
for handling multiple changes simultaneously.
"""
	def __init__(self, text=u""):
		self.text = text
	
	def __unicode__(self):
		"""
	Enable the conversion from lines to strings.
	"""
		return self.text
