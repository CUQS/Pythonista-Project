#!python3

import re
import appex, ui
import requests
from datetime import datetime
import math

#find_pm = re.compile(u'''空气质量指数为([0-9]+)''')
find_tem = re.compile(u'''temp=([-0-9]+)''')
find_data = re.compile(u'''center.([0-9]+)''')
color_set = ["#007d00", "#c1c742", "#b35d00", "#c00000", "#400093", "#5c1919"]


# 获取pm数据
def get_date_pm():
	txt = ""
	flag = True
	try:
		hea = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
		html = requests.get('https://aqicn.org/city/beijing/shijingshangucheng/cn/',headers = hea, timeout=10)  
		html.encoding = 'utf-8'
		pagesource = html.text
		# 温度
		tem = ""
		for i in re.findall(find_tem, pagesource):
			tem += i
			break
		# 所有指标过去48小时，当前，最低，最高值
		dataAll = []
		for i in re.findall(find_data, pagesource):
			dataAll.append(i)
		# pm
		txt += dataAll[0]
		# 温度
		txt += "," + tem
		# 湿度
		txt += "," + dataAll[21]
		
	except requests.RequestException:
		txt += "An ambiguous exception that occurred while handling your request."
		flag = False
	except requests.ConnectionError:
		txt += "A Connection error occurred."
		flag = False
	return txt, flag

def colorSelect(num, pie_count):
	if num<=10:
		pie_count[0] += 1
		return "#007d00"
	if 10<num<=20:
		pie_count[1] += 1
		return "#c1c742"
	if 20<num<=30:
		pie_count[2] += 1
		return "#b35d00"
	if 30<num<=40:
		pie_count[3] += 1
		return "#c00000"
	if 40<num<=60:
		pie_count[4] += 1
		return "#400093"
	else:
		pie_count[5] += 1
		return "#5c1919"

def main():
	
	v = ui.View(frame=(0, 0, 320, 220), background_color="#DDF3FF")
	iv = ui.ImageView(frame=(8, 8, 320, 200), flex = 'w')
	label = ui.Label(frame=(8, 0, 320, 100),flex = 'w')
	label.name = 'text_label'
	label.font = ('<system-bold>', 20)
	label.number_of_lines = 0
	v.add_subview(label)
	v.add_subview(iv)
	appex.set_widget_view(v)
	# 当前时间
	date = datetime.now()
	date_str = date.__format__('%Y-%m-%d %H:%M:%S')
	# 事件日期时间
	d_nxt = datetime(2019, 7, 7, 13, 0, 0, 0)
	# 计算时间差
	d_diff = d_nxt-date
	d_days = d_diff.days
	d_hours = d_diff.seconds//3600
	if d_hours<0:
		d_days = d_days - 1
		d_hours = 24 + d_hours
	
	date_use = date_str + "\n距离能力考: " + str(d_days) + "天" + str(d_hours) + "小时\n"
	label.text = "waiting for data...\n" + date_use
	# 读取数据
	with open('pmdata.txt', 'r' ) as f:
		txtstr = f.readlines()
	# 追加数据及显示
	with open('pmdata.txt', 'a+' ) as f:
		weanow = ""
		data_save = datetime.strptime(txtstr[-1][:19], '%Y-%m-%d %H:%M:%S')
		# 前一数据不是同一天
		if data_save.day != date.day:
			txt, flag = get_date_pm()
			weanow += txt
			if flag:
				f.write(date_str+" "+weanow+"\n")
		else:
			# 前一数据相差1小时以上
			if (abs(date.hour-data_save.hour)>=1):
				# 与前一数据相差2小时以上
				# 或者分钟数在30以上
				if date.minute>25 or (abs(date.hour-data_save.hour)>=2):
					txt, flag = get_date_pm()
					weanow += txt
					if flag:
						f.write(date_str+" "+weanow+"\n")
				else:
					weanow += txtstr[-1][19:-1]
			else:
				weanow += txtstr[-1][19:-1]
		with ui.ImageContext(310, 200) as ctx:
			# 绘制参考线
			lineimg = ui.Path.rect(0, 101, 230, 1) # pm500+
			lineimg.fill()
			lineimg = ui.Path.rect(0, 200-10, 230, 1) # pm50
			ui.set_color('"#c1c742"')
			lineimg.fill()
			lineimg = ui.Path.rect(0, 200-20, 230, 1) # pm100
			ui.set_color('#b35d00')
			lineimg.fill()
			lineimg = ui.Path.rect(0, 200-30, 230, 1) # pm150
			ui.set_color('#c00000')
			lineimg.fill()
			lineimg = ui.Path.rect(0, 200-40, 230, 1) # pm200
			ui.set_color('#400093')
			lineimg.fill()
			lineimg = ui.Path.rect(0, 200-60, 230, 1) # pm300
			ui.set_color('#5c1919')
			lineimg.fill()
			
			# 绘制历史数据
			numdata = len(txtstr)
			pie_count = [0, 0, 0, 0, 0, 0]
			for i in range(numdata):
				index = txtstr[-66+i].find(',')
				height = int(txtstr[-66+i][19:index])//6
				if i<66:
					width = 3.5
					rct = ui.Path.rect(i*width, 200-height, width*0.618, height)
				ui.set_color(colorSelect(height, pie_count))
				if i<66:
					rct.fill()
			
			# 绘制比重图
			acc_h = 0
			for i in range(6):
				ui.set_color(color_set[i])
				single_h = pie_count[i]/numdata*200
				acc_h += single_h
				rct = ui.Path.rect(251, 200-acc_h, 36, single_h)
				rct.fill()
			
			iv.image = ctx.get_image()
		
		# 字符显示
		label.text = date_use + "PM2.5,温度,湿度: " + weanow + "\n500+分割线(╯﹏╰）"

if __name__ == '__main__':
	main()
	#print(get_date_pm()[0])
