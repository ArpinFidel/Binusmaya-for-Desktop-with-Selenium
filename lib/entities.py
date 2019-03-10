entities={}

class Entity:
	def __init__(self, name, id):
		self.name = name
		self.id = id

	def __eq__(self, other):
		return self.id==other.id
	
	def __ne__(self, other):
		return self.id!=other.id

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return (self.name+' ('+str(self.id)+')')

class Student(Entity):
	def __init__(self, name, id):
		super().__init__(name, int(id))

class Lecturer(Entity):
	def __init__(self, name, id):
		super().__init__(name, id)