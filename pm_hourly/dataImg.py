#!python3

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

with open('pmdata.txt', 'r' ) as f:
	txtstr = f.readlines()
	xlab = []
	xs = []
	y = []
	for i,line in enumerate(txtstr):
		if i==0:
			xlab.append(line[5:19])
		elif i != len(txtstr)-1:
				xlab.append(" ")
		else:
			xlab.append(line[5:19])
		xs.append(datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S'))
		index = line.find(',')
		y.append(int(line[19:index]))

# 配置横坐标
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
# 自动旋转日期标记
#plt.gcf().autofmt_xdate(rotation=90) 
plt.xticks(xs,xlab,rotation=15)

#plt.plot(xs, y, 'o-')
plt.plot(xs, y)
plt.show()
