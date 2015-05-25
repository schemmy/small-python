# -*- coding: utf-8 -*-

# 下载ZOL的壁纸（网址为：desk.zol.com.cn）
# 使用到的第三方库：requests，BeautifulSoup4
# 使用方法：
# 1:若下手机壁纸，则把 zol_url 改为 http://sj.zol.com.cn
# 2:选择下载的壁纸类别后，修改 category_url（默认下载“风景”类别下壁纸）
# 3:终端中输入 “python download_zol_pic.py [起始页，可选参数] [终止页，可选参数]”
#   如输入 “python download_zol_pic.py” 则下载第一页
#     输入 “python download_zol_pic.py 3” 下载第一到三页
#     输入 “python download_zol_pic.py 3 5” 下载第三到五页
# Author：egrcc
# Email：zhaolujun1994@gmail.com
# Version：0.1

import os
import sys
import requests
from bs4 import BeautifulSoup

# 设置编码，不设置时，我本地无法在运行时显示文件名，会报当前文件的第93行编码错误
reload(sys)
sys.setdefaultencoding("utf-8")

# ZOL壁纸首页，若下载手机壁纸则应设为 zol_url = "http://sj.zol.com.cn"
zol_url = "http://desk.zol.com.cn"
# 壁纸的类别，可根据你所选的类别的url修改
category_url = "/fengjing/"
url = zol_url + category_url
# http请求头
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0'}

# 得到该url下每个图集的url，并放入pic_list_url中
def get_pic_list_url(url):
    # 该url下所有图集的url
    pic_list_url = []
    # 加入http请求头，模拟浏览器，不加则有时下载会出错（大部分仍然没问题），下同
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.content)

    for li_tag in soup.find_all("li", class_ = "photo-list-padding"):
        pic_href = li_tag.a['href']
        pic_list_url.append(zol_url + pic_href)

    return pic_list_url

# 下载图片
def download_pic(url):
    pic_list_url = get_pic_list_url(url)
    for item in pic_list_url:
        # 每个图集的url同时是该图集下第一张壁纸的url
        pic_url = item
        while True:
            r = requests.get(pic_url, headers = headers)
            soup = BeautifulSoup(r.content)
            # 用BeautifulSoup解析，获取文件名
            wrapper_tag = soup.find_all('div', class_ = "wrapper photo-tit clearfix")
            title_tag = wrapper_tag[0].find_all('a')[0]
            file_name = title_tag.string + title_tag.next_sibling.string + ".jpg"
            # 把文件名中的“/”用“_”取代，不然Linux系统下会出错
            file_name = file_name.replace("/", "_")

            # 若 soup.find_all("dd", id = "tagfbl")[0].a 没有“id”属性
            # 则说明壁纸没有提供下载（从html源码中可看出），就跳过
            if soup.find_all("dd", id = "tagfbl")[0].a.get('id') == None:
                # 该图集下下一张图片的url，下同
                next_pic_url = zol_url +  soup.find("a", id = "pageNext")['href']
                # 当下一张图片的url与第一张图片的url相同时，则说明该图集已下载完，下同
                if(next_pic_url == item):
                    break
                pic_url = next_pic_url
                continue
            
            # most_res_pic_url 为最高分辨率图片url，默认总是下载最高分辨率
            most_res_pic_url = zol_url + soup.find_all("dd", id = "tagfbl")[0].a['href']
            most_res_pic_r = requests.get(most_res_pic_url, headers = headers)
            most_res_pic_soup = BeautifulSoup(most_res_pic_r.content)

            # real_pic_url 为图片真正的url
            real_pic_url = most_res_pic_soup.find('img')['src']
            real_pic_r = requests.get(real_pic_url, headers = headers)
            # 在当前目录下创建“pictures”文件夹
            path = os.getcwd()
            path = os.path.join(path,'pictures')
            if not os.path.exists(path):
                os.mkdir(path) 

            file_path = os.path.join(path, file_name)
            # 如果文件名为 file_name 的文件不存在（则说明该文件没有下载过），下载该文件
            # 加入 if 的目的是为了避免重复下载
            if not os.path.exists(file_path):
                #  如果不加b参数，下载图片会有编码错误，全是彩电~.~，运行系统：win7
                f = open(file_path, 'wb')
                print "downloading " + file_name + "......"
                f.write(real_pic_r.content)
                f.close()
            else:
                break

            next_pic_url = zol_url +  soup.find("a", id = "pageNext")['href']
            if(next_pic_url == item):
                break
            pic_url = next_pic_url


# 程序入口
try:
    start_page_number = int(sys.argv[1])
    end_page_number = int(sys.argv[2])
except Exception:
    try:
        if isinstance(start_page_number, int):
            current_page = 1
            end_page_number = start_page_number
    except Exception:
        current_page = 1
        end_page_number = 1        
else:
    current_page = start_page_number

while current_page <= end_page_number :
    download_pic(url + str(current_page) + ".html")
    print "已下载完第" + str(current_page) + "页图片。"
    current_page = current_page + 1
    if current_page > end_page_number:
        print "下载完成。"
    
