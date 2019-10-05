import bisect
import dill
from bs4 import BeautifulSoup


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


class HTMLMixin:
	""" For objects who has a `content` attribute, which is a list of HTML """

	def raw_html_to_text(self, html):
		""" Parse a HTML string into Tag and get the text content """
		tag = BeautifulSoup(html, 'lxml')
		return tag.get_text().strip()

	def get_text(self):
		return '\n'.join(self.raw_html_to_text(p) for p in self.content)

	def get_html(self):
		return '\n'.join(self.content)

	def to_dict(self):
		return {k: getattr(self, k) for k in self.__slots__}

	def save(self, path):
		with open(path, 'wb') as f:
			# save a dictionary
			dill.dump(self.to_dict(), f)

	def load(self, path):
		with open(path, 'rb') as f:
			content = pkl.load(f)

		for k, v in content.items():
			setattr(self, k, v)

	@classmethod
	def from_file(cls, path):
		with open(path, 'rb') as f:
			content = dill.load(f)
		return cls(**content)


class Question(UniqueInstance, HTMLMixin):
	""" Content => List[HTML], type => List[str] """

	__slots__ = ['id', 'content', 'type']

	def __init__(self, id, content, type=None):
		super().__init__(self.__class__.__name__, id)
		self.id = id
		self.content = content
		self.type = type or []

	def __repr__(self):
		return f'Question<{self.id}>'


class Answer(UniqueInstance, HTMLMixin):
	""" Content => List[HTML] """
	__slots__ = ['id', 'content']

	def __init__(self, id, content):
		super().__init__(self.__class__.__name__, id)
		self.id = id
		self.content = content
		
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
	tag = BeautifulSoup('<p>123</p>', 'lxml')
	tag = tag.find('p')
	q = Question(1, [str(tag)] * 2)
	print(q.to_dict())
	print(q.get_text())
	print(q.get_html())




