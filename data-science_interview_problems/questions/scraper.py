import requests
from bs4 import BeautifulSoup

from questions import Question, Answer



def get_content(url):
	""" Get the question and answer (as a list of HTML content) from a single page """
	page = requests.get(url)
	assert page.status_code == 200

	def _get_content(page, section_style='box-sizing: border-box;'):
		soup = BeautifulSoup(page.text, 'lxml')
		sections = soup.find_all('section', attrs={'style': section_style})[1:]

		# find the starting section for answers
		start_idx = [i for i, s in enumerate(sections) if '答案揭晓' in s.get_text()]
		if not start_idx:
			raise ValueError('No answers in this page')
		else:
			start_idx = start_idx[0]

		question_sections = [s for s in sections[start_idx+1:] if 'DS Interview Questions' in s.get_text()]
		# pick the sections at odd index
		question_sections = [s for i, s in enumerate(question_sections) if i % 2 == 0]

		# for each question find the corresponding answer
		# which is usually in the next section
		question = question_sections[0]
		question_html = list(question.children)
		while len(question_html) == 1 and question_html[0].name == 'section':
			question_html = list(question_html[0].children)
		question_html = [h for h in question_html if h.get_text().strip() != 'DS Interview Questions']

		answer_section = question.next_sibling
		# go through the nested sections until the we find the actual HTML for the answer part
		answer_html = answer_section.find_all('section', attrs={'style': section_style})[1:2]
		while len(answer_html) == 1 and answer_html[0].name == 'section':
			answer_html = list(answer_html[0].children)

		# need to convert to string, since pickling doesn't work well with beautifulsoup
		return [str(q) for q in question_html], [str(a) for a in answer_html]

	for style in ['box-sizing: border-box;', 
				'   box-sizing: border-box; ',
				'   box-sizing: border-box; ']:
		try:
			return _get_content(page, style)
		except:
			continue
	else:
		raise ValueError("Failed to parse url: {}".format(url))


if __name__ == '__main__':

	import pickle

	content = []

	cid = 0
	while True:
		url = 'https://mp.weixin.qq.com/mp/homepage?__biz=MzIzMDA1MTM3Mg==&hid=7&sn=eb1bafd2f52396868dd0d37801758f5b&scene=1&devicetype=iOS12.4&version=17000529&lang=zh_CN&nettype=3G+&ascene=7&session_us=gh_fb56fa7dda76&fontScale=100&wx_header=1&cid={}&begin=0&count=100&action=appmsg_list&f=json&r=0.5466809010203566&appmsg_token='.format(cid)
		
		page = requests.post(url)
		assert page.status_code == 200
		pages = page.json()['appmsg_list']		

		if len(pages) == 0:
			break

		for p in pages:
			try:
				q_id = int(''.join([ch for ch in p['title'] if ch.isdigit()]))
				q, a = get_content(p['link'])

				content.append(Question(id=q_id, content=q))
				content.append(Answer(id=q_id, content=a))

				print('面试题 {}: Success.'.format(q_id))
			except Exception as e:
				print('面试题 {}: Failed.'.format(p['title']))
				print(p['link'])
		
		cid += 1

	with open('./data/数据应用学院每日一题.pkl', 'wb') as f:
		pickle.dump(content, f)
