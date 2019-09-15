import bisect


class DuplicateIdException(Exception):
	pass


class UniqueInstance:
	""" A unique instance makes sure that all its subclasses dont have duplicate ids """

	id_pool = dict()

	def __init__(self, cls_name, id):
		if cls_name in self.id_pool and id in self.id_pool[cls_name]:
			raise DuplicateIdException(f'Duplicated id {id} for class {cls_name}')
		else:
			self.id_pool[cls_name] = self.id_pool.get(cls_name, set()) | set([id])


class Question(UniqueInstance):

	__slots__ = ['id', 'content', 'type']

	def __init__(self, id, content, type=None):
		super().__init__(self.__class__.__name__, id)
		self.content = content
		self.type = type

	def __repr__(self):
		return f'Question<{self.id}>'


class Answer(UniqueInstance):

	__slots__ = ['id', 'content', 'type']

	def __init__(self, id, content, type=None):
		super().__init__(self.__class__.__name__, id)
		self.content = content
		self.type = type

	def __repr__(self):
		return f'Answer<{self.id}>'


def find_instance_by_id(id, instances):
	""" find the question with given id, assuming the instances are already sorted in id """
	ids = [q.id for q in instances]
	idx = bisect.bisect(ids, id)
	
	if instances[idx].id == id:
		return instances[idx]
	else:
		raise ValueError(f'instances with the given id {id} is not found.')


if __name__ == '__main__':
	print(help(bisect.bisect_right))








