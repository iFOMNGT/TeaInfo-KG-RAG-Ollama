# -*- coding=utf-8 -*-
import os
import pandas as pd

def json2txt(txt_path:str, json_path:str=None, json_file:pd.DataFrame=None, start_idx:int=None, end_idx:int=None) -> None:
    """将固定格式的json文件转化为固定格式的txt文本

    Args:
        txt_path (str): 传入txt文件的保存路径。
        json_path (str, optional): 传入json文件的路径。
        json_file(DataFrame, optional): 传入json文件的DataFrame形式。 默认为空。
        start_idx (int, optional): 起始索引。 默认为空。
        end_idx (int, optional): 结束索引。 默认为空。

    Raises:
        ValueError: 当传入的文件路径不存在，或文件格式错误时，抛出该异常。
    """
    if json_path is None and json_file is None:
        raise ValueError('请传入json文件路径或DataFrame')
    
    if json_path is not None:
        if not (json_path.endswith('.json') and txt_path.endswith('.txt')):
            if not (os.path.exists(json_path) and os.path.exists(txt_path)):
                raise ValueError('文件格式错误！，请检查传入路径是否正确')
    
    if json_file is not None:
        df = json_file
    else:
        df = pd.read_json(json_path)
        
    if start_idx:
        df = df.iloc[start_idx:]
    if end_idx:
        df = df.iloc[:end_idx]
    
    with open(txt_path, 'w+', encoding='utf-8') as file:
        for index, row in df.iterrows():
            file.write(f'== {row['标题']} ==\n')
            # 将标题与词条结合 -> 绿茶是茶叶品种
            file.write(f'{row['标题']}是{row['词条']}\n')
            # 介绍则直接写入文本中
            file.write(f'-- {row['标题']}的介绍 --\n')
            file.write(row['介绍']+'\n')
            
            # 将标题与结构化数据结合 -> 绿茶的中文名：绿茶
            if row['结构化数据']:
                structed_data = row['结构化数据'][2:].split('@@')
                for data in structed_data:
                    file.write(f'- {row['标题']}的{data}\n')
                
            # 非结构化数据的处理如下
            # 保留从网页爬下来的空间结构 例如：
            '''
            制作工艺(h2)
            绿茶的加工，简单分为杀青、揉捻和干燥三个步骤，其中关键在于杀青。鲜叶通过杀青，酶的活性钝化，内含的各种化学成
            分，基本上是在没有酶影响的条件下，由热力作用进行物理化学变化，从而形成了绿茶的品质特征。
            杀青(h3)
            杀青对绿茶品质起着决定性的作用。通过高温，破坏鲜叶中酶的特性，制止多酚类物质氧化，以防止叶子红变；同时蒸发叶内
            的部分水分，使叶子变软，为揉捻造形创造条件。随着水分的蒸发，鲜叶中具有青草气的低沸点芳香物质挥发消失，从而使茶叶香气得到改善。
            '''
            # 将每一个h2的部分分割出来
            h2_list = row['非结构化数据'][2:].split('@@')
            for h2 in h2_list:
                h2_title = h2.split('\n', maxsplit=1)[0]
                file.write(f'-- {row["标题"]}的{h2_title} --\n')
                
                if '\n' in h2:
                    h2_content = h2.split('\n', maxsplit=1)[1]
                    # 而h2文本下可能含有h3
                    if '##' in h2_content:
                        h3_list = h2_content.split('##')
                        # 将h3之前的内容全部写下
                        if h3_list[0] != '':
                            file.write(h3_list[0]+'\n')
                        # 接着处理h3文本
                        for h3 in h3_list[1:]:
                            h3_title = h3.split('\n', maxsplit=1)[0]
                            h3_content = h3.split('\n', maxsplit=1)[1]
                            file.write(f'~~ {h3_title} ~~\n')
                            file.write(h3_content+'\n')
                    
                    else:
                        file.write(h2_content+'\n')
            
            # 信息来源
            file.write(f'-- {row["标题"]}的信息来源 --\n')
            file.write(f'来源为百度百科，地址为{row['网址']}\n')
            
            # 最后加一个空行
            file.write('\n')
        
    print('转换完成！')
    print(f'保存路径为：{os.path.abspath(txt_path)}')    