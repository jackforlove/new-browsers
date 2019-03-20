from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
import chardet,base64
from urllib import parse,request
from html.parser import HTMLParser
from pink import img as a
from add_page import img as b
from back import img as c
from baidu import img as d
from cross import img as e
from lock import img as f
from next import img as g
from renew import img as h
from xsj import img as i
import sys
url=[]

class MainWindow(QMainWindow):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# 设置窗口标题
		self.setWindowTitle('佩奇浏览器XL v1.0')
		self.resize(1000,600)
		# 设置窗口图标
		self.setWindowIcon(QIcon('pink.png'))
		self.show()
		self.lock_sign=0

		# 添加 URL 地址栏
		self.urlbar = QLineEdit()
		# 让地址栏能响应回车按键信号
		self.urlbar.setFixedWidth(400)
		self.urlbar.returnPressed.connect(self.navigate_to_url)

		# 添加标签栏
		self.tabs = QTabWidget()
		self.tabs.setDocumentMode(True)
		self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
		self.tabs.currentChanged.connect(self.current_tab_changed)
		self.tabs.setTabsClosable(True)
		self.tabs.tabCloseRequested.connect(self.close_current_tab)

		self.add_new_tab(QUrl('http://tool.uixsj.cn/3dzqb/'), 'Homepage')

		self.setCentralWidget(self.tabs)

		new_tab_action = QAction(QIcon('add_page.png'), 'New Page', self)
		new_tab_action.triggered.connect(self.add_new_tab)


		# 添加导航栏
		navigation_bar = QToolBar('Navigation')
		navigation_bar.setMovable(False)
		navigation_bar_1=QToolBar('navi')
		navigation_bar_1.setMovable(False)
		# 设定图标的大小
		navigation_bar.setIconSize(QSize(16, 16))
		navigation_bar_1.setIconSize(QSize(16,16))
		self.addToolBar(navigation_bar)
		self.addToolBar(navigation_bar_1)

		# 添加前进、后退、停止加载和刷新的按钮
		back_button = QAction(QIcon('back.png'), '返回', self)
		next_button = QAction(QIcon('next.png'), '前进', self)
		stop_button = QAction(QIcon('cross.png'), '停止', self)
		reload_button = QAction(QIcon('renew.png'), '刷新', self)
		lock_button=QAction(QIcon('lock.png'),'网页锁定',self)
		defend_button=QAction(QIcon('pink.png'),'当前链接提取',self)

		label=QLabel('书签栏  ')
		label_1=QAction(QIcon('baidu.ico'),'百度',self)
		label_2=QAction(QIcon('xsj.ico'),'现实君',self)



		back_button.triggered.connect(self.tabs.currentWidget().back)
		next_button.triggered.connect(self.tabs.currentWidget().forward)
		stop_button.triggered.connect(self.tabs.currentWidget().stop)
		reload_button.triggered.connect(self.tabs.currentWidget().reload)
		lock_button.triggered.connect(self.lock)
		defend_button.triggered.connect(self.defend)
		label_1.triggered.connect(self.label_1)
		label_2.triggered.connect(self.label_2)

		# 将按钮添加到导航栏上
		navigation_bar.addAction(back_button)
		navigation_bar.addAction(next_button)
		navigation_bar.addAction(stop_button)
		navigation_bar.addAction(reload_button)




		navigation_bar.addSeparator()
		navigation_bar_1.addSeparator()
		navigation_bar.addWidget(self.urlbar)
		navigation_bar.addAction(lock_button)
		navigation_bar.addAction(defend_button)
		navigation_bar_1.addWidget(label)
		navigation_bar_1.addAction(label_1)
		navigation_bar_1.addAction(label_2)

	
	# 响应回车按钮，将浏览器当前访问的 URL 设置为用户输入的 URL
	def navigate_to_url(self):
		q = QUrl(self.urlbar.text())
		if q.scheme() == '':
			q.setScheme('http')
		self.tabs.currentWidget().setUrl(q)

	def renew_urlbar(self, q, browser=None):
		# 如果不是当前窗口所展示的网页则不更新 URL
		if browser != self.tabs.currentWidget():
			return
		# 将当前网页的链接更新到地址栏
		self.urlbar.setText(q.toString())
		self.urlbar.setCursorPosition(0)

	# 添加新的标签页
	def add_new_tab(self, qurl=QUrl(''), label='Blank'):
		# 为标签创建新网页
		browser = QWebEngineView()
		browser.setUrl(qurl)
		i = self.tabs.addTab(browser, label)

		self.tabs.setCurrentIndex(i)

		browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))

		browser.loadFinished.connect(lambda _, i=i, browser=browser: 
			self.tabs.setTabText(i, browser.page().title()))

	# 双击标签栏打开新页面
	def tab_open_doubleclick(self, i):
		if i == -1 and not self.lock_sign:
			self.add_new_tab()

	# 
	def current_tab_changed(self, i):
		qurl = self.tabs.currentWidget().url()
		self.renew_urlbar(qurl, self.tabs.currentWidget())

	def close_current_tab(self, i):
		# 如果当前标签页只剩下一个则不关闭
		if self.tabs.count() < 2 or self.lock_sign==1:
			return
		self.tabs.removeTab(i)
	def lock(self):
		if self.lock_sign==0:
			self.lock_sign=1
			return
		if self.lock_sign==1:
			self.lock_sign=0
			return
	def defend(self):
		name=self.urlbar.text()
		if len(name)>10:
			self.xmlDefend(name)
			if not url:
				QMessageBox.information(self,'提取失败','没有找到链接')
			else:
				QMessageBox.information(self,'提取完成','提取完成\n以保存到当前目录下')
				with open(name[10:20]+'的链接提取.txt','w') as f:
					for i in url[1::2]:
						f.write(i+'\n')



	def xmlDefend(self,name):
		req=request.Request(name)
		html=request.urlopen(req,timeout=5).read()
		# print(html.decode("gbk"))
		cha=chardet.detect(html)
		parser=MyHTMLParser()
		parser.feed(html.decode(cha['encoding']))

	def label_1(self):
		i=self.tabs.currentIndex()
		if i >=-1 and not self.lock_sign:
		   self.add_new_tab(QUrl('https://www.baidu.com'))
	def label_2(self):
		i=self.tabs.currentIndex()
		if i >=-1 and not self.lock_sign:
		   self.add_new_tab(QUrl('http://tool.uixsj.cn'))

def pack_img(img_url,py_url):
	open_icon = open(img_url,"rb")
	b64str = base64.b64encode(open_icon.read())
	open_icon.close()
	write_data = "img = %s" % b64str
	f = open(py_url,"w+")
	f.write(write_data)
	f.close()
def zip_img(img,img_name):
	with open(img_name,"wb+") as tmp:
		tmp.write(base64.b64decode(img))
		tmp.close()

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag=='a':
             if len(attrs) > 0:
                 #print(attrs)
                 if 'href' in attrs[0]:
                     #print(attrs[0][1])
                     for i in attrs[0]:
                        url.append(i)
		
# 创建应用
# pack_img('icons/pink.png','pink.py')
# pack_img('icons/add_page.png','add_page.py')
# pack_img('icons/back.png','back.py')
# pack_img('icons/next.png','next.py')
# pack_img('icons/cross.png','cross.py')
# pack_img('icons/renew.png','renew.py')
# pack_img('icons/lock.png','lock.py')
# pack_img('icons/baidu.ico','baidu.py')
# pack_img('icons/xsj.ico','xsj.py')
try:
	zip_img(a,'pink.png')
	zip_img(b,'add_page.png')
	zip_img(c,'back.png')
	zip_img(d,'baidu.ico')
	zip_img(e,'cross.png')
	zip_img(f,'lock.png')
	zip_img(g,'next.png')
	zip_img(h,'renew.png')
	zip_img(i,'xsj.ico')
finally:

	app = QApplication(sys.argv)
	# 创建主窗口
	window = MainWindow()
	# 显示窗口
	window.show()
	# 运行应用，并监听事件
	app.exec_()
