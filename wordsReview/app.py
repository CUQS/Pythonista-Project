#!python3
import ui
import random
import dialogs
from PIL import Image
import io

NEW_WORD = 0
REVIEW_WORD = 80
WORD_ALL = 1049
REMEMBER_COUNT = [0]

class Env:
	def __init__(self):
		# words_data
		f = open('words.txt', 'r', encoding='gb18030')
		self.txt = f.readlines()
		f.close()
		# studying_record
		f = open('data.txt', 'r')
		data = f.readlines()
		f.close()

		self.get = [int(i) for i in data[3].split(',')]
		REMEMBER_COUNT[0] = len(self.get)
		if ',' in data[1]:
			studying_t = data[1].split(',')
			studying_t = [int(i) for i in studying_t]
			try:
				newWordsNum = int(dialogs.input_alert('新词数', '正在学习: '+str(len(studying_t))))
				if newWordsNum>WORD_ALL-len(studying_t)-REMEMBER_COUNT[0]:
					newWordsNum = WORD_ALL-len(studying_t)-REMEMBER_COUNT[0]
			except:
				newWordsNum = NEW_WORD
			studying_t.extend([i + max([max(studying_t),max(self.get)]) + 1 for i in range(newWordsNum)])
		else:
			studying_t = []
			newWordsNum = NEW_WORD
			studying_t.extend([i+max(self.get)+1 for i in range(newWordsNum)])
		self.new = newWordsNum
		self.writeStudying = studying_t.copy()

		if len(self.writeStudying) >= REVIEW_WORD + newWordsNum:
			self.studying = self.writeStudying[-REVIEW_WORD - newWordsNum:]
		else:
			self.studying = self.writeStudying[:]
		self.words_num = len(self.studying)
	
		# section
		self.s_forget = []
		self.s_review = []
		self.sectFinish = True
		self.word_now = [self.studying[-1]]
	
		# flag
		self.easy_flag = False
		self.forget_flag = False
		self.front_act = "ok"
		self.turn = 1
	
		# action_space
		self.action_space = ['forget', 'remember', 'easy', 'ok', 'misAct']

	def step(self, action):
		state = {'word': "", 'word_info': ""}
		if action == 'ok' or action == 'misAct':
			if action == 'ok':
				word = self.word_now.pop()
				if self.easy_flag:
					self.easy_word_pop(word)
				if self.forget_flag:
					if self.front_act == 'forget':
						if self.s_forget.count(word) < 2:
							self.s_forget.append(word)
					if self.front_act == 'remember':
						if self.s_review.count(word) < 1:
							self.s_review.append(word)
			if action == 'misAct':
				self.studying.append(self.word_now.pop())
			self.forget_flag = False
			self.easy_flag = False
			l1 = len(self.studying)
			l2 = len(self.s_forget)
			l3 = len(self.s_review)
			if l1 == 0 and l2 == 0 and l3 == 0:
				if len(self.word_now) == 0:
					self.save()
					return state, True
			else:
				self.word_now.append(self._choose_policy(l1, l2, l3))
			state['word'] = self.get_word(self.word_now[0])
			self.turn = 1
			return state, False

		# if forget must choose remember or forget again
		if action == 'forget' or action == 'remember' or action == 'easy':
			state['word'] = self.get_word(self.word_now[0])
			state['word_info'] = self.get_info(self.word_now[0])
			self.turn = 2
			if action == 'easy':
				self.easy_flag = True
			if self.forget_flag:
				self.front_act = action
			if action == 'forget':
				if not self.forget_flag:
					state['word_info'] = self.get_sentence(self.word_now[0])
					self.turn = 1
				else:
					self.turn = 2
				self.forget_flag = True
		return state, False

	def _choose_policy(self, l1, l2, l3):
		c = []
		if l1 > 0 and l2 > 0 and l3 > 0:
			c.extend([1, 1, 1, 1, 2, 2, 2, 2, 3, 3])
		elif l1 > 0 and l2 > 0 and l3 == 0:
			c.extend([1, 1, 1, 2])
		elif l1 > 0 and l2 == 0 and l3 == 0:
			c.extend([1])
		elif l1 > 0 and l2 == 0 and l3 > 0:
			c.extend([1, 1, 1, 1, 3])
		elif l1 == 0 and l2 > 0 and l3 > 0:
			c.extend([2, 2, 3])
		elif l1 == 0 and l2 == 0 and l3 > 0:
			c.extend([3])
		elif l1 == 0 and l2 > 0 and l3 == 0:
			c.extend([2])
		c = random.choice(c)
		if c == 1:
			if l1 > 1:
				return self.studying.pop(random.randint(0, l1-2))
			else:
				return self.studying.pop()
		elif c == 2:
			if l2 > 1:
				return self.s_forget.pop(random.randint(0, l2-2))
			else:
				return self.s_forget.pop()
		elif c == 3:
			if l3 > 1:
				return self.s_review.pop(random.randint(0, l3-2))
			else:
				return self.s_review.pop()

	def get_word(self, index):
		word_t = self.txt[index * 5][:-1]
		i = word_t.find('（')
		if i != -1:
			return word_t[:i]
		else:
			return word_t

	def get_sentence(self, index):
		return self.txt[index * 5 + 2]

	def get_info(self, index):
		return "".join(self.txt[index * 5:index * 5 + 4])

	def easy_word_pop(self, index):
		list_index = self.writeStudying.index(index)
		self.get.append(self.writeStudying.pop(list_index))
	
	def save(self):
		f = open('data.txt', 'w')
		f.write("studying\n")
		writeStudying_t = [str(i) for i in set(self.writeStudying)]
		f.write(",".join(writeStudying_t))
		f.write("\nget\n")
		get_t = [str(i) for i in set(self.get)]
		f.write(",".join(get_t))
		f.close()
		

class AppUi(ui.View):
	
	def __init__(self):
		self.v = ui.load_view('app')
		self.v['BtnForget'].action = self.ActForget
		self.v['BtnRemember'].action = self.ActRemember
		self.v['BtnEasy'].action = self.ActEasy
		self.v['BtnSave'].action = self.ActSave
		
		ip = Image.open('IMG_4025.JPG')
		with io.BytesIO() as bIO:
			ip.save(bIO, ip.format)
			self.v['Img'].image = ui.Image.from_data(bIO.getvalue())
		
		self.v.present('sheet')
		self.env = Env()
		s, done = self.env.step('ok')
		self.v['word'].text = s['word']
		self.v['text'].text = s['word_info']
		self.draw_record()
		self.draw_topline()
		dialogs.hud_alert('新词数: '+str(self.env.new))
		
	def draw_record(self):
		self.v['record1'].text = str(len(self.env.writeStudying))
		self.v['record2'].text = str(len(self.env.get))
		self.v['record3'].text = str(WORD_ALL)
		
	def draw_topline(self):
		n = self.env.words_num
		l1 = len(set(self.env.studying))
		if not l1 <= 1:
			l1 += 1
		l2 = len(set(self.env.s_forget))
		l3 = len(set(self.env.s_review))
		remember = n-l1-l2-l3
		x1 = 760*remember/n
		x2 = 760*l3/n
		x3 = 760*l1/n
		x4 = 760*l2/n
		with ui.ImageContext(740, 34) as ctx:
			ui.set_color('#00b600')
			line_remember = ui.Path.rect(0, 0, x1, 34)
			line_remember.fill()
			ui.set_color('#a3f5aa')
			line_review = ui.Path.rect(x1, 0, x2, 34)
			line_review.fill()
			ui.set_color('#f5f5f5')
			line_study = ui.Path.rect(x1+x2, 0, x3, 34)
			line_study.fill()
			ui.set_color('#f55252')
			line_study = ui.Path.rect(x1+x2+x3, 0, x4, 34)
			line_study.fill()
			self.v['iv'].image = ctx.get_image()
		
	def ActEasy(self, sender):
		self.draw_topline()
		self.v['BtnForget'].title = "MISACT"
		self.v['BtnRemember'].title = "NEXT"
		self.v['BtnEasy'].enabled = False
		s, done = self.env.step('easy')
		if not done:
			self.v['text'].text = s['word_info']
		else:
			self.v['BtnForget'].enabled = False
			self.v['BtnRemember'].enabled = False
			self.v['BtnEasy'].enabled = False
			self.v['text'].text = "End\nRemember Num: " + str(len(self.env.get)-REMEMBER_COUNT[0])
	
	def ActForget(self, sender):
		self.draw_topline()
		if self.env.turn == 1:
			self.v['BtnEasy'].enabled = False
			s, done = self.env.step('forget')
			if self.env.turn == 2:
				self.v['BtnForget'].title = "MISACT"
				self.v['BtnRemember'].title = "NEXT"
		elif self.env.turn == 2:
			s, done = self.env.step('misAct')
			self.v['BtnForget'].title = "FORGET"
			self.v['BtnRemember'].title = "REMEMBER"
			self.v['BtnEasy'].enabled = True
		self.v['word'].text = s['word']
		if not done:
			self.v['text'].text = s['word_info']
		else:
			self.v['text'].text = "End\nRemember Num: " + str(len(self.env.get)-REMEMBER_COUNT[0])
	
	def ActRemember(self, sender):
		self.draw_topline()
		if self.env.turn == 1:
			self.v['BtnEasy'].enabled = False
			s, done = self.env.step('remember')
			self.v['BtnForget'].title = "MISACT"
			self.v['BtnRemember'].title = "NEXT"
		elif self.env.turn == 2:
			s, done = self.env.step('ok')
			self.v['BtnForget'].title = "FORGET"
			self.v['BtnRemember'].title = "REMEMBER"
			self.draw_record()
			self.v['BtnEasy'].enabled = True
		self.v['word'].text = s['word']
		if not done:
			self.v['text'].text = s['word_info']
		else:
			self.v['BtnForget'].enabled = False
			self.v['BtnRemember'].enabled = False
			self.v['BtnEasy'].enabled = False
			self.v['text'].text = "End\nRemember Num: " + str(len(self.env.get)-REMEMBER_COUNT[0])
			self.draw_record()
		
	def ActSave(self, sender):
		self.env.save()
		self.v['text'].text = self.v['text'].text + "\n Saved\n Remember Num: " + str(len(self.env.get)-REMEMBER_COUNT[0])
		
		
def ActEasy(sender):
	pass
		
		
def ActForget(sender):
	pass
	
	
def ActRemember(sender):
	pass
	
	
def ActSave(self, sender):
	pass
	
if __name__ == '__main__':
	app = AppUi()
