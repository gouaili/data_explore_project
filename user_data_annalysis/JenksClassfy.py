#!/usr/bin/python
# -*- coding:utf-8 -*-
from jenkspy import jenks_breaks
import numpy as np
import pandas as pd
from Cutgrid import Cutgrid
from sklearn.cluster import KMeans

class JenksClassfy:
    gvf=0.0
    def goodness_of_variance_fit(self, array, classes):
        """对一维数据进行聚类
        :param array: type：array. definition:一维数组
        :param classes: type：int. definition:聚类的个数
        :return: gvf:（The Goodness of Variance Fit）type:float. definiti:方差拟合优度,值越大效果越好。
                 classes:聚类的阈值区间
        """
        # get the break points
        classes=classes
        classes = jenks_breaks(array, classes)
        classified = np.array([self.classify(i, classes) for i in array])
        # 获取区间最大值
        maxz = max(classified)
        zone_indices = [[idx for idx, val in enumerate(classified) if zone + 1 == val] for zone in range(maxz)]
        # 与阵列平均值的平方偏差之和
        sdam = np.sum((array - array.mean()) ** 2)
        array_sort = [np.array([array[index] for index in zone]) for zone in zone_indices]
        sdcm = sum([np.sum((classified - classified.mean()) ** 2) for classified in array_sort])
        gvf = (sdam - sdcm) / sdam
        return gvf, classes

    def classify(self, value, breaks):
        for i in range(1, len(breaks)):
            if value < breaks[i]:
                return i
        return len(breaks) - 1

    def dataframe_classify(self, df,maxusefulbitmap, classes):
        classes_len = len(classes)  #list长度为5，类型为4
        firstclassifyresult=np.array([[int(0)] * len(maxusefulbitmap[0])] * len(maxusefulbitmap))
        for m in range(len(maxusefulbitmap)):
            for n in range(len(maxusefulbitmap[0])):
                if maxusefulbitmap[m][n]==1:
                    for i in range(classes_len - 1):
                        if i < classes_len - 2:
                            if df[m][n] >= classes[i] and  (df[m][n] < classes[i + 1]):
                                firstclassifyresult[m][n]= i + 1
                        elif i == classes_len - 2:
                              if df[m][n]>= classes[i] and df[m][n] <= classes[i + 1]:
                                firstclassifyresult[m][n]= i + 1
                else:
                    firstclassifyresult[m][n]=-9    #先将不需要的空间置为-9999，以免影响下次判断
        firstclassifyresult[firstclassifyresult==-9]=0
        print firstclassifyresult
        return firstclassifyresult




if __name__ == '__main__':
    jenksclassfy = JenksClassfy()
    nclasses=4
    array = np.array(
        [0.0137, 0.0092, 0.0097, 0.0092, 0.0, 0.0097, 0.0098, 0.0084, 0.0053, 0.0034, 0.0103, 0.0084, 0.0077, 0.0056,
         0.0052, 0.0078, 0.0067, 0.0049, 0.0046, 0.0045, 0.0066, 0.006, 0.0057, 0.004, 0.002, 0.0057, 0.0047, 0.0037,
         0.0034, 0.0022, 0.0031, 0.0017, 0.0024, 0.0019, 0.0013])

    while jenksclassfy.gvf < .8 and nclasses<=20:
        jenksclassfy.gvf, classes = jenksclassfy.goodness_of_variance_fit(array, nclasses)
        # print(nclasses, gvf)
        nclasses += 1
        # print classes

    print nclasses, classes

    array_result_1 = np.array(
        [0.0137, 0.0092, 0.0097, 0.0092, 0.0, 0.0097, 0.0098, 0.0084, 0.0053, 0.0034, 0.0103, 0.0084, 0.0077, 0.0056,
         0.0052, 0.0078, 0.0067, 0.0049, 0.0046, 0.0045, 0.0066, 0.006, 0.0057, 0.004, 0.002, 0.0057, 0.0047, 0.0037,
         0.0034, 0.0022, 0.0031, 0.0017, 0.0024, 0.0019, 0.0013])

    reslut_array = np.array(array_result_1).reshape(7, 5)
    print reslut_array
    #pd_result = pd.DataFrame(reslut_array)
    #print pd_result

    # 背景颜色
    result_pd = pd.DataFrame(reslut_array)
    result_pd.style.applymap(lambda x: 'background-color: grey' if x >= 0 and x < 0.0037 else (
        'background-color: yellow' if x >= 0.0037 and x < 0.0067 else (
            'background-color: green' if x >= 0.0067 and x < 0.0103 else (
                'background-color: red' if x >= 0.0103 and x <= 0.0137 else ''))), subset=pd.IndexSlice[:, :])

    maxusefulbitmap=np.array([[1] * len(reslut_array[0])] * len(reslut_array))
    #print "-------------"
    #print maxusefulbitmap
    pd_result = jenksclassfy.dataframe_classify(reslut_array,maxusefulbitmap, classes)
    #pd_result = pd_result.values
    #print "第一次分类结果"
    #print pd_result

    cutgrid=Cutgrid()
    classes_bitmap = cutgrid.CutGridClassify(pd_result, 4)

    #print classes_bitmap
    kmeans = KMeans(n_clusters=1, init='k-means++', random_state=0).fit(array_result_1)

