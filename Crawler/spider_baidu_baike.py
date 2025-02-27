# -*- coding=utf-8 -*-
import os
import time
import random
from DrissionPage import SessionPage, ChromiumOptions, ChromiumPage
import pandas as pd
import json
from collections.abc import Iterable

class spider_baike:
    def __init__(self, save_path:str=None, visible=False, edge_path:str=None):
        '''
        该爬虫类允许传入三个参数，save_path传入保存文件的路径，默认路径为代码文件同目录下生成output文件夹，文件为json格式。
        其次visible参数为是否显示爬取过程，默认为False。
        而edge_path参数为可选参数，传入edge浏览器的路径，默认为None，即使用默认路径（"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"）。
        '''
        # 判断保存路径是否是json后缀
        if save_path is None:
            base_dir = os.path.dirname(__file__)
            save_path = os.path.join(base_dir, 'output', '爬虫.json')
        
        if not save_path.endswith('.json'):
            raise Exception('传入的文件路径并非是json格式，请注意检查！')
        
        self.visible = visible
        self.path = save_path
        self.error = []
        self.error_code = []
        self.result = {
            '标题':[],
            '词条': [],
            '介绍': [],
            '结构化数据': [],
            '非结构化数据': [],
            '跳转页面标题': [],
            '图片': [],
            '网址': [],
        }
        
        self.result_list = []
        
        # 初始化edge浏览器路径
        if edge_path is None:
            self.edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        else:
            self.edge_path = edge_path
            
        
        if os.path.exists(save_path):
            print(f'文件{save_path}已存在！即将覆盖文件内容！')
        else:
            print(f'爬虫内容将保存在指定路径{save_path}')
    
    def run(self, search_name:Iterable=None, max_depth:int=0, url:str=None):
        '''
        爬虫将以传入的搜索词search_name或url为起始页面开始爬取，爬取跳转页面的深度默认为0，可通过max_depth参数修改，爬取内容包括：
            1. 爬取页面的标题
            2. 爬取页面的介绍部分
            3. 爬取页面的结构化数据
            4. 爬取页面的非结构化数据
            5. 该页面是从哪个标题页面跳转过来的
            6. 该页面存在的图片路径与其对应的图标题
            7. 该页面的网址
            8. 该网页标题的词条（分类)  
        将爬取到的信息保存到指定json文件中。
        '''
        if search_name is None and url is None:
            raise Exception('请输入搜索词或url！')
        
        print('爬虫开始......')
        self.max_depth = max_depth
        self.url = url
        if self.url == None:
            for name in search_name:
                url = f'https://baike.baidu.com/item/{name}'
                self.getData(url)
        else:
            self.getData(self.url)
        
        if self.result['标题'] == []:
            print('当前未爬取到任何数据！请检查网页结构是否发生改变！或是否需要验证！')
        
        if not self.visible:
            df = pd.DataFrame(self.result)
            df.to_json(orient='records', path_or_buf=self.path, ensure_ascii=False, indent=4)
        
        print('爬取结束!')
        self.page.quit()
        if self.error != []:
            self.print_error()
        
        
    def getData(self, url:str, last_title=None, depth:int = 0):
        # 限制爬取深度
        if depth > self.max_depth:
            return
        
        page = SessionPage()
        page.get(url)
        if page.response.status_code != 200:
            print(f'页面{url}爬取错误，请检查！')
            self.error.append(url)
            self.error_code.append(page.response.status_code)
            return
        
        #页面标题，检查该标题网页是否已经爬取过了
        try:         
            title = page.ele('@@class^lemmaTitle@@class:J-lemma-title@@tag()=h1').text
            if url in self.result['网址'] or title in self.result['标题']:
                return
        except:
            return
        
        #设置时延
        time.sleep(random.uniform(0.75, 1))
        
        print(f'当前正在爬取的页面标题:{title}')
        print(f'对应的url={page.url}')
        print(f'爬取的深度为{depth}', end='\n\n')
        #页面介绍
        try:
            introduce = page.ele('@@tag()=div@@class^lemmaSummary@@class:J-summary').text
        except:
            introduce = None
        # print(f'页面介绍:\n{introduce}')
        #页面结构化
        structured = self.getData_structured(page)
        # print(f'页面结构化数据:\n{structured}')
        #页面非结构化
        unstructured = self.getData_unstructured(page)
        #页面图片
        picture = self.getData_picture(url)
        #页面网址(url)
        #网页标题的词条
        try:
            word = page.ele('@@class^lemmaDescText@@tag()=div').text
        except:
            word = None
            
            
        #将爬取到的信息保存到字典中
        self.result['标题'].append(title)
        self.result['介绍'].append(introduce)
        self.result['结构化数据'].append(structured)
        self.result['非结构化数据'].append(unstructured)
        self.result['跳转页面标题'].append(last_title)
        self.result['图片'].append(picture)
        self.result['网址'].append(page.url)
        self.result['词条'].append(word)
        
        if self.visible:
            temp_data = {
                    '标题': title,
                    '词条': word,
                    '介绍': introduce,
                    '结构化数据': structured,
                    '非结构化数据': unstructured,
                    '跳转页面标题': last_title,
                    '图片': picture,
                    '网址': page.url,
                }
            self.result_list.append(temp_data)
            with open(self.path, 'w+' , encoding='utf-8') as file:
                json.dump(self.result_list, file, ensure_ascii=False, indent=4)
        
        #找出当前网页可以跳转到的页面
        div = page.ele('@class^mainContent')
        a_list = div.eles('@@tag()=a@@href^/item@!title@!text()=我的收藏')
        if a_list:
            for i in range(len(a_list)):
                self.getData(a_list[i].attr('href'), title, depth+1)
                
        
    def getData_structured(self, page:SessionPage):
        result = None
        cols = page.eles('@@tag()=dt@@class^basicInfoItem@@class:itemName').get.texts()
        values = page.eles('@@tag()=dd@@class^basicInfoItem@@class:itemValue').get.texts()
        
        # print(cols, values)
        if cols and values:
            result = ''
            for col, value in zip(cols, values):
                result += f'@@{col}:{value}'
        
        # print(result)
        
        return result
        
    def getData_unstructured(self, page:SessionPage):
        # 最终的文本字符串
        result = None
        # 某一段文本的文本字符串，用于匹配相对应出现的图片的标题
        temp_result = ''
        # 保存临时图片标题及对应的地址
        self.temp_picture_title = []; self.temp_picture_src = []
        #定位非结构化文本，同时提取其所有文本
        content = page.ele('@@tag()=div@@class=J-lemma-content')
        text = content.text
        # print(text)
        
        # 只要确定存在content部分的文本，即存在非结构化数据，将进行文本处理
        if content: 
            result = ''
            
            #获取所有content文本的子节点
            children = content.children('@@data-tag')
            if children != []:
                for child in children:
                    temp_result = ''
                    if child.attr('data-tag') == 'header':
                        if child.attr('data-index') != None and '-' in child.attr('data-index'):
                            result += f'##{child.text}\n'
                        else:
                            result += f'@@{child.text}'
                            
                    if child.attr('data-tag') == 'paragraph':
                        temp = child.eles('@@tag()=span@@class^text').get.texts()
                        for te in temp:
                            temp_result += f'{te}'
                            
                        temp_div = child.eles('@@tag()=div@@class^lemmaPicture')
                        
                        if temp_div != []:
                            for div in temp_div:
                                temp_a = div.eles('@@tag()=a@@class^imageLink@@href@@title')
                                temp_a_plural = child.eles('@@tag()=a@@class^albumWrapper')
                                
                                if temp_a != [] and temp_a_plural != []:
                                    temp_title, temp_src = (temp_a[0].attr('title'), temp_a[0].attr('href')) if temp_a is not None else(temp_a_plural[0].attr('title'), temp_a_plural[0].attr('href'))
                            
                                    if temp_title in temp_result:
                                        temp_result = temp_result.replace(temp_title, f'{temp_title}[{temp_src}] ', 1)
                                    else:
                                        self.temp_picture_title.append(temp_title)
                                        self.temp_picture_src.append(temp_src)
                                        
                        result += temp_result
                        
            else:
                result = text
                
            result = result.replace('播报\n编辑','')
            # print(result)

            if self.temp_picture_title != []:
                for index in range(len(self.temp_picture_title)):
                    if self.temp_picture_title[index] in result:
                        result = result.replace(self.temp_picture_title[index], f'{self.temp_picture_title[index]}[{self.temp_picture_src[index]}] ', 1)
                        self.temp_picture_title[index] = None; self.temp_picture_src[index] = None
                    
        return result
        
    def getData_picture(self, url:str):
        result = None
        co = ChromiumOptions()
        co = ChromiumOptions.set_browser_path(co, self.edge_path)
        co.headless()
        self.page = ChromiumPage(co)
        time.sleep(random.uniform(1, 1.2))
        self.page.get(url)
        try:
            result = f'@@{self.page.ele('@@class^lemmaTitle@@class:J-lemma-title@@tag()=h1').text}:' + self.page.ele('@@tag()=div@@class^abstractAlbum').ele('@@tag()=img@@src^https://bkimg.cdn.bcebos.com/pic/').attr('src')
        except:
            result = None
        
        for index in range(len(self.temp_picture_title)):
            if self.temp_picture_title[index] != None and result != None:
                result += f'@@{self.temp_picture_title[index]}:{self.temp_picture_src[index]}'
        
        # 将所有图片处理完毕后，清空临时列表
        del(self.temp_picture_title, self.temp_picture_src)
        
        # print(result)
        return result
    
    def print_error(self):
        if self.error != []:
            print('本次爬取过程中出现错误的网址如下：')
            for url, code in zip(self.error, self.error_code):
                print(url,f'        状态码为{code}')
            



if __name__ == '__main__':
    spider = spider_baike(save_path='../output/test.json', visible=True)
    spider.run(['绿茶'])