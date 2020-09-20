# coding: utf-8

import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression  #sklearn中已经废弃cross_validation,将其中的内容整合到model_selection中；将sklearn.cross_validation 替换为 sklearn.model_selection
from sklearn.ensemble import AdaBoostClassifier,AdaBoostRegressor

import urllib
import time
import pickle
import html

class WAF(object):
    def __init__(self):
        good_query_list = self.get_query_list('goodqueries.txt')
        bad_query_list = self.get_query_list('badqueries.txt')
        
        good_y = [0 for i in range(0,len(good_query_list))]
        bad_y = [1 for i in range(0,len(bad_query_list))]

        queries = bad_query_list+good_query_list
        y = bad_y + good_y

        #converting data to vectors  定义矢量化实例
        self.vectorizer = TfidfVectorizer(tokenizer=self.get_ngrams)

        # 把不规律的文本字符串列表转换成规律的 ( [i,j],tdidf值) 的矩阵X
        # 用于下一步训练分类器 lgs
        X = self.vectorizer.fit_transform(queries)

        # 使用 train_test_split 分割 X y 列表
        # X_train矩阵的数目对应 y_train列表的数目(一一对应)  -->> 用来训练模型
        # X_test矩阵的数目对应 	 (一一对应) -->> 用来测试模型的准确性
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=20000, random_state=42, stratify=y)

        # 定理逻辑回归方法模型
        self.lgs = AdaBoostRegressor()

        # 使用逻辑回归方法训练模型实例 lgs
        self.lgs.fit(X_train, y_train)

        # 使用测试值 对 模型的准确度进行计算
        print('模型的准确度:{}'.format(self.lgs.score(X_test, y_test)))
    
    # 对 新的请求列表进行预测
    def predict(self,new_queries):
        new_queries = [urllib.parse.unquote(url) for url in new_queries]
        X_predict = self.vectorizer.transform(new_queries)
        res = self.lgs.predict(X_predict)
        res_list = []
        for q,r in zip(new_queries,res):
            tmp = '正常请求'if r == 0 else '恶意请求'
            # print('{}  {}'.format(q,tmp))
            q_entity = html.escape(q)
            res_list.append({'url':q_entity,'res':tmp})
        print("预测的结果列表:")
        for i in res_list:
            print(i)
        return r,str(res_list)
        

    # 得到文本中的请求列表
    def get_query_list(self,filename):
        directory = str(os.getcwd())
        # directory = str(os.getcwd())+'/module/waf'
        filepath = directory + "/" + filename
        data = open(filepath,'r',encoding="utf-8").readlines()
        query_list = []
        for d in data:
            d = str(urllib.parse.unquote(d))   #converting url encoded data to simple string
            # print(d)
            query_list.append(d)
        return list(set(query_list))


    #tokenizer function, this will make 3 grams of each query
    # www.foo.com/1 转换为 ['www','ww.','w.f','.fo','foo','oo.','o.c','.co','com','om/','m/1']
    def get_ngrams(self,query):
        tempQuery = str(query)
        ngrams = []
        for i in range(0,len(tempQuery)-3):
            ngrams.append(tempQuery[i:i+3])
        return ngrams

def Predict(url):
    with open(r'C:\Users\30285\PycharmProjects\Equipment_management_system\user\lgstest6.pickle', 'rb') as input:
        w = pickle.load(input)

    # X has 46 features per sample; expecting 7  youqude  cuowu
    return w.predict([url])

if __name__ == '__main__':
#     # 若 检测模型文件lgs.pickle 不存在,需要先训练出模型
#
#     # w = WAF()
#     # with open('lgstest3.pickle','wb') as output:
#     #     pickle.dump(w,output)
#
    with open('lgstest6.pickle','rb') as input:
        w = pickle.load(input)
#     #
#     # # X has 46 features per sample; expecting 7  youqude  cuowu
#     # w.predict(['id=4 and payload'])

    w.predict([r"/\xd0\x97\xd0\xb4\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb2'\xd1\x8f/", 'www.foo.com/name=admin\' or 1=1',
               'abc.com/admin.php',
               '"><svg onload=confirm(1)>', 'test/q=<a href="javascript:confirm(1)>', 'q=../etc/passwd'])