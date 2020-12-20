import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['KaiTi', 'SimHei', 'FangSong']  # 汉字字体,优先使用楷体，如果找不到楷体，则使用黑体
mpl.rcParams['font.size'] = 12  # 字体大小
mpl.rcParams['axes.unicode_minus'] = False  # 正常显示负号


data = [(122, 115), (132, 150), (143, 130), (94, 70), (92, 99), (95, 80)]

N = 6

Ming = []
Yu = []

for i in range(N):
    Ming.append(data[i][0])
    Yu.append(data[i][1])

ind = np.arange(N)  # the x locations for the groups
width = 0.25

fig, ax = plt.subplots()  # 创建一个子图
rects1 = ax.bar(ind, Ming, width, color='blue')
rects2 = ax.bar(ind + width, Yu, width, color='orange')

# 设置语文、数学、英语成绩的图例，位置为图表的左上角
ax.legend((rects1[0], rects2[0]), ('小明成绩', '小禹成绩'),
          loc='upper right')


# 定义标注柱形图高度的函数
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()  # 获得柱形的高度
        ax.text(rect.get_x() + rect.get_width() / 2., height, '%d' % int(height), ha='center', va='bottom')  # 添加文本


# 调用autolabel函数，在柱状图上标注高度
autolabel(rects1)
autolabel(rects2)
ax.set_xlabel('学科')
ax.set_ylabel('成绩')

plt.title(u'周测成绩情况-2016xxxx-xxx')
ax.set_xticks(ind + width * 2 / 2)
ax.set_xticklabels((u'语文', u'数学', u'英语', u'物理', u'化学', u'生物'))
plt.show()