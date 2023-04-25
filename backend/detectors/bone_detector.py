import random

import pandas as pd
from sklearn.linear_model import RidgeClassifier

from backend.detectors.tf_idf import *


def addblank(temp):  # 在数字前后添加空白
    strnum = temp.group()  # group()用来提出分组截获的字符串
    return ' ' + strnum + ' '


def textParse(input_string):  # 将文本切分成单个字符
    output_string = []
    input_string = list(input_string)
    for c in input_string:
        if '\u4e00' <= c <= '\u9fff':
            output_string.append(c)
    # input_string=re.sub("[0-9]+",addblank,input_string)  #用re.sub函数将正则表达式匹配到的字符串进行替换
    # listofTokens = re.split(r'[，。、：（）\[\]\s﹝﹞［］]+', input_string)   #将正则表达式中匹配到的字符用作分隔符
    # for tok in listofTokens:  #因为上面分割可能存在多个字符连在一起的情况，所以将其再进一步拆分，例如："今夕不雨" --> "今","夕","不","雨"
    #     if len(tok) > 0:
    #         if len(tok) > 1 and not (re.match('[0-9]+', tok)):
    #             output_string.extend(list(tok))
    #         else:
    #             output_string.append(tok)
    return output_string


def creatVocablist(doclist):  # 创建总的词表
    vocabset = set([])  # 集合（set）是一个无序的不重复元素序列。
    for doc in doclist:
        vocabset = vocabset | set(doc)  # ｜ 集合合并
    return list(vocabset)


def word2vec(vocablist, inputSet):  # 根据词表将词映射为向量，采用 Bag of Words 直接映射
    vec = [0] * len(vocablist)
    for word in inputSet:
        if word in vocablist:
            vec[vocablist.index(word)] = 1
    return vec


def trainModel(trainMat, trainClass):  # 改为KNN分类
    return trainMat, trainClass


def classify(input_vec, trainMat, trainClass, k=3):  # 改为KNN分类
    diffMat = trainMat - input_vec
    sqDiffMat = diffMat ** 2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    sortedDistIndicies = distances.argsort()
    classCount = {}
    for i in range(k):
        voteIlabel = trainClass[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
    sortedClassCount = sorted(classCount.items(), key=lambda x: x[1], reverse=True)
    return sortedClassCount[0][0]


class BoneDetector:
    def __init__(self, path):
        self.oracle_text = pd.read_excel(path)
        self.text_input = list(self.oracle_text['内容'])
        self.text_class = list(self.oracle_text['分类'])
        self.doc_list = []
        self.class_list = []
        self.class_dic = {'祭祀': 0, '农业': 1, '往来': 2, '王事': 3, '军事': 4, '气象': 5, '田猎': 6, '吉凶': 7,
                          '政事': 8,
                          '生育': 9, '疾病': 10}  # 字典用于类别映射
        for i in range(len(self.text_class)):  # 分词
            out_string = textParse(self.text_input[i])
            if len(out_string) >= 4:
                self.doc_list.append(''.join(out_string))
                self.class_list.append(self.class_dic[self.text_class[i]])

    def predict(self, target_str):
        self.doc_list.append(target_str)
        tfidf = TfIdf()
        total_list = tfidf.add_corpus(self.doc_list)
        target_idf = total_list.pop()
        train_list = total_list
        clf = RidgeClassifier()
        clf.fit(train_list, self.class_list)
        val_pred = clf.predict([target_idf])
        result = list(self.class_dic.keys())[list(self.class_dic.values()).index(val_pred)]
        self.doc_list.pop()
        return result, self.get_similar_bones(val_pred)

    def get_similar_bones(self, id):
        similarity = []
        all_similarity = []
        for i in range(len(self.class_list)):
            if self.class_list[i] == id:
                all_similarity.append(i)
        while len(similarity) < 5:
            similarity.append(all_similarity[random.randint(0, len(all_similarity) - 1)])
        return [self.doc_list[i] for i in similarity]


if __name__ == '__main__':
    bone_detector = BoneDetector('../data/oracle_bone.xlsx')
    print(bone_detector.predict('乎先于河'))
