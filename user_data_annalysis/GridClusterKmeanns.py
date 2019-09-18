#!/usr/bin/python
# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd

pd.set_option('mode.chained_assignment', None)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class GridKmeans:
    """对格子进行聚类.
    """

    def isRectangleOverlap(self, rec1, rec2):

        """根据2个矩形坐标判断，2个矩形是否重合
        :param rec1: type：字典类型dict或者Series. definition：矩形坐标：x1,y1,x2,y2. example:{'x1':0,'y1':0,'x2':0,'y2':0}
        :param rec2: type：字典类型dict或者Series. definition：矩形坐标：x1,y1,x2,y2. example:{'x1':0,'y1':0,'x2':0,'y2':0}
        :return type: boolean example: Ture/False .definition:Ture:重合，Flase:不重合
        :raise None
        """
        #print type(rec1),type(rec2)
        #print rec1,rec2
        return not (rec1['y2'] < rec2['y1'] or  # rigth
                    rec1['x2'] < rec2['x1'] or  # bottom
                    rec1['y1'] > rec2['y2'] or  # left
                    rec1['x1'] > rec2['x2'])    # top

    def isRectangleOverlap_list(self, rec1, rec2_list):
        """ 根据1个矩形坐标判断，是否和其它所有矩形重合
        :param rec1: type：字典类型dict或者Series. definition：矩形坐标：x1,y1,x2,y2. example:{'x1':0,'y1':0,'x2':0,'y2':0}
        :param rec2_list: type：List. definition：矩形坐标数组 example:[{'x1':0,'y1':0,'x2':0,'y2':0},{'x1':1,'y1':1,'x2':1,'y2':1}]
        :return type: boolean example: Ture/False .definition:Ture:重合，Flase:不重合
        :raise None
        """
        for i in range(len(rec2_list)):
            if not (rec1['y2'] < rec2_list[i]['y1'] or  # rigth
                    rec1['x2'] < rec2_list[i]['x1'] or  # bottom
                    rec1['y1'] > rec2_list[i]['y2'] or  # left
                    rec1['x1'] > rec2_list[i]['x2']     # top
            ):
                return True
        return False

    def singleGirdIterator(self, grid):
        """对一个矩形遍历出的所有的小矩形坐标区域及区域内值的计算
        :param grid: type:arrary 二维数组.  definition：矩形
        :return: usefularea：type: dataframe. definition：所有矩形的可能组合
                 columns=['x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'rectangleValueSum', 'RectangleValueVar'])
                 x1,y1,x2,y2:左上和右下坐标
                 rectangleGridCnt：矩形的格子总数
                 rectangleValueSum：矩形格子内数值的和
                 RectangleValueVar：矩形格子内数值的方差
        :raise None
        """
        row = len(grid)       #格子行数
        col = len(grid[0])    #格子列数
        usefulGirdArea = pd.DataFrame(
            columns=['x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'rectangleValueSum', 'RectangleValueVar'])
        for x1 in range(row):
            for y1 in range(col):
                for x2 in range(x1, row):
                    for y2 in range(y1, col):
                        Rectangle = grid[x1:x2 + 1, y1:y2 + 1]                  #遍历获取的格子坐标
                        rectangleGridCnt = len(Rectangle) * len(Rectangle[0])   #获取的格子坐标总数
                        rectangleValueSum = Rectangle.sum()                          #格子内数值方差
                        RectangleValueVar = Rectangle.var()                          #格子内数值方差
                        usefulGirdArea = usefulGirdArea.append(
                            {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'rectangleGridCnt': rectangleGridCnt,
                             'rectangleValueSum': rectangleValueSum, 'RectangleValueVar': RectangleValueVar},
                            ignore_index=True)

        usefulgirdarea = usefulGirdArea.astype(
            dtype={'x1': np.int64, 'x2': np.int64, 'y1': np.int64, 'y2': np.int64, 'rectangleGridCnt': np.int64,
                   'rectangleValueSum': np.float, 'RectangleValueVar': np.float})

        #usefularea = usefularea.reset_index()
        return usefulGirdArea


    def MultipleGirdIterator(self, usefulGirdArea, target, nclasses,containCoordinateList=None,ratelimit=None):
        """根据矩形要求的总的格子数量，找出所有可能的矩形组合
        :param usefulGirdArea: type:pd.dataframe.  definition:对一个矩形遍历出的所有的小矩形坐标区域及区域内值的计算.
        :param target: type:int.   definition:矩形格子的数量和的目标值
        :param nclasses: type:int. definition:组合成大矩形的细分格子数量。example：例如对一个矩形切成4份有多少种组合
        :param containCoordinateList : type:list. definition：组合中需要包含的坐标组合。example:[[],[]]
        :param ratelimit: type:float. 每个切分的格子的最小含有的格子数量。使用target*ratelimit获得数量。
        :return: candidatesGridComb: type:list. definition:可用的格子组合.example:[{},{}]
                 candidatesGirdArea：近等价于candidatesGirdArea，暂时无使用地方
        """
        searchPath = []
        candidatesGridComb = []
        candidatesGirdArea=usefulGirdArea
        print "初始可用格子的预选组合是：" +str(len(candidatesGirdArea))
        # 搜索广度剪枝 1
        if containCoordinateList is not None:
            print "候选的格子需要包含如下坐标组合:" +str(containCoordinateList)
            max_cnt = 0
            candidates_df=pd.DataFrame()
            for i in range(len(containCoordinateList)):
                x1 = containCoordinateList[i][0]
                y1 = containCoordinateList[i][1]
                x2 = containCoordinateList[i][2]
                y2 = containCoordinateList[i][3]
                max_cnt = max(max_cnt, containCoordinateList[i][4])
                # 从初选的格子中剔除掉和当前选中格子列表中不重复的格子。
                # 当前选中的格子的标识：
                candidates_df_tmp = candidatesGirdArea[
                    (candidatesGirdArea['x1'] <= x1) & (candidatesGirdArea['y1'] <= y1) & (candidatesGirdArea['x2'] >= x2) & (
                            candidatesGirdArea['y2'] >= y2)]

                if len(candidates_df_tmp)==0:
                    continue
                #过滤过程
                if len(containCoordinateList)==1:
                    candidates_df=candidates_df_tmp
                else:
                    for j in range(len(containCoordinateList)):
                        if j==i:
                            continue
                        else:
                            rec1={}
                            rec1['x1']  = containCoordinateList[j][0]
                            rec1['y1']  = containCoordinateList[j][1]
                            rec1['x2']  = containCoordinateList[j][2]
                            rec1['y2']  = containCoordinateList[j][3]
                            candidates_df_tmp['is_overlap'] = candidates_df_tmp.apply(lambda row: self.isRectangleOverlap(row, rec1), axis=1)
                            if len(candidates_df_tmp)==0:
                                continue

                            candidates_df_tmp=candidates_df_tmp[~candidates_df_tmp.is_overlap]
                            candidates_df = candidates_df.append([candidates_df_tmp])


            if len(candidates_df)>0:
                candidates_df=candidates_df.drop_duplicates(subset=None, keep='first', inplace=False) #删除重复项
                #candidates_df=candidates_df[(candidates_df['rectangleGridCnt']<=(target-max_cnt))]    #删除与当前最大格子的和大于总格子数量的格子
                candidatesGirdArea = candidates_df.reset_index()

            print "最终的格子选择数：" + str(len(candidatesGirdArea))
            print nclasses
            print candidatesGirdArea

        # 搜索广度剪枝 2
        if ratelimit is not None:
            print "限制每个格子的数量必须在" + str(target * ratelimit) + "以上（包括）"
            candidatesGirdArea = candidatesGirdArea.loc[(candidatesGirdArea['rectangleGridCnt'] >= target * ratelimit) & (
                    candidatesGirdArea['rectangleGridCnt'] <= (target * (1 - ratelimit))), :]
            candidatesGirdArea = candidatesGirdArea.reset_index()
            #print candidatesGirdArea

        candidatesGridCnt = np.array(candidatesGirdArea['rectangleGridCnt'])   # 候选可用的格子的数量列表

        size = len(candidatesGridCnt)
        print "候选可用的格子的数量列表" +str(size)
        print candidatesGridCnt
        #print candidatesGirdArea

        # 如果没有可用的格子则返回
        if size == 0:
            return []
        self.__dfs(candidatesGridCnt, 0, size, searchPath, candidatesGridComb, target, nclasses, candidatesGirdArea)
        # print candidatesGridComb,candidatesGirdArea
        return candidatesGridComb, candidatesGirdArea

    def __dfs(self, candidatesGridCnt, begin, size, searchPath, candidatesGridComb, target, nclasses, candidatesGirdArea):
        """ 递归遍历，找到所有的可用的矩形组合
        :param candidatesGridCnt: type:list. definetion:可用的格子数量的列表.
        :param begin: type:int.   definetion:搜索的启示坐标.
        :param size:  type：int.  definetion:可用的格子数量的列表的大小.
        :param searchPath:  type:list. definetion:搜索路径(组合列表). example:[{index:gird_cnt},{index:gird_cnt}]
        :param candidatesGridComb: type:liest. definetion: 所有满足要求的路径列表. example:[{index:gird_cnt},{index:gird_cnt}]
        :param target: type:int.   definition:矩形格子的数量和的目标值
        :param nclasses: type:int. definition:组合成大矩形的细分格子数量。example：例如对一个矩形切成4份有多少种组合
        :param candidatesGirdArea: type:pd.dataframe definetion:所有矩形的坐标组合
        :return: None
        """
        if target == 0:
            candidatesGridComb.append(searchPath[:])
            return
        if target < 0:
            return
        # 搜索深度剪枝
        if len(searchPath) > nclasses:
            return
        for index in range(begin, size):
            # TODO 不能删除，此为和上一个初始根节点是否重合的判断
            # if begin - 1 >= 0:
            # if self.isRectangleOverlap(usefularea.ix[index], usefularea.ix[begin - 1]):
            #    continue
            if len(searchPath) > 0:
                rec2_list = []
                for i in range(len(searchPath)):
                    dict1 = searchPath[i]
                    for (k, v) in dict1.items():
                        rec2_list.append(candidatesGirdArea.ix[k])
                # 此为和此分支上面的所有根节点的矩形是否重合的判断
                if self.isRectangleOverlap_list(candidatesGirdArea.ix[index], rec2_list):
                    continue
            dict = {}
            dict[index] = candidatesGridCnt[index]
            searchPath.append(dict)
            #剪枝--->从当前跟点的下一个节点开始遍历
            self.__dfs(candidatesGridCnt, index + 1, size, searchPath, candidatesGridComb, target - candidatesGridCnt[index], nclasses, candidatesGirdArea)
            searchPath.pop()

    def Girdkmeans(self, candidatesGridComb, candidatesGirdArea):
        """根据找到的矩形组合找到合适的组合：当前选用方差和最小的
        :param candidatesGridComb: type:list. definition:可用的矩形的id组合.example:[{},{}],只有标识矩形的id。
        :param candidatesGirdArea: type:pd.dataframe. definition: 存放所有矩形的详细信息。
        :return:gridCombResult: 返回所有组合可能的矩形的详细信息
                gridCombClassInfo: 存放每个聚合类别的方差值
        """
        gridCombResult = pd.DataFrame(
            columns=['classid', 'nclasses', 'x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'RectangleValueVar'])
        gridCombClassInfo=pd.DataFrame()
        for j, row in enumerate(candidatesGridComb):
            nclasses = len(row)
            for i in range(len(row)):
                dict = row[i]
                for (k, v) in dict.items():
                    gridCombResult = gridCombResult.append({
                        'classid': j, 'nclasses': nclasses,
                        'x1': candidatesGirdArea.ix[k]['x1'], 'x2': candidatesGirdArea.ix[k]['x2'],
                        'y1': candidatesGirdArea.ix[k]['y1'], 'y2': candidatesGirdArea.ix[k]['y2'],
                        'rectangleGridCnt': candidatesGirdArea.ix[k]['rectangleGridCnt'],
                        'RectangleValueVar': candidatesGirdArea.ix[k]['RectangleValueVar']},
                        ignore_index=True)
            grouped_cnt = gridCombResult.groupby(['classid', 'nclasses'])
            gridCombClassInfo = grouped_cnt['RectangleValueVar'].agg({'group_var_sum': sum},
                                                                      {'group_var_mean': np.mean})
        return gridCombResult, gridCombClassInfo



    def GirdkmeansClassify(self, gird, cluster_result_info, gridCombClassInfo, nclasses, coordinate_list=None):
        """ 根据所有可用矩形的组合结果，依据方差和找到方差最小的聚类组合
        :param gird: 划分聚类的格子。
        :param cluster_result_info: type:pd.dataframe. 所有组合可能的矩形的详细信息.
        :param gridCombClassInfo: type:pa.dataframe.每个聚合类别的方差值.
        :param nclasses: type:int. definetion:划分的聚类的类别.
        :param coordinate_list: type:list. definetion:偏移坐标,主要针对划分聚类的格子不是从0，坐标开始的话，需要+偏移量
        :return:clusterGridCoordinate: type:pa.dataframe. 组合矩形的坐标标识.
                classifyresult_bitmap: type:array. 聚类位图结果标识.

        """
        #偏移坐标标识
        if coordinate_list is None:
            Offset_x1 = 0
            Offset_y1 = 0
        else:
            Offset_x1 = coordinate_list[0][0]
            Offset_y1 = coordinate_list[0][1]
        #分类结果的位图标识：0为无分类标识
        classifyresult_bitmap = np.array([[int(0)] * len(gird[0])] * len(gird))
        if len(gridCombClassInfo) == 0:
            print "当前分类无结果，请重新选择分类用户或者分类个数"
            exit(0)

        nclasses_result = gridCombClassInfo.query('nclasses==' + str(nclasses))

        if len(nclasses_result) == 0:
            print "当前分类无结果，请重新选择分类用户或者分类个数"
            exit(0)
        #选择方差和最小的聚类
        finalclusterclass = nclasses_result.sort_values("group_var_sum", inplace=False).head(1)
        classid = finalclusterclass.index[0][0]

        clusterGridCoordinate = cluster_result_info[cluster_result_info['classid'] == classid]
        i = 0
        for index, row in clusterGridCoordinate.iterrows():
            i += 1
            x1 = int(row["x1"]) + Offset_x1
            x2 = int(row["x2"]) + Offset_x1
            y1 = int(row["y1"]) + Offset_y1
            y2 = int(row["y2"]) + Offset_y1
            classifyresult_bitmap[x1:x2 + 1, y1:y2 + 1] = i
        return clusterGridCoordinate, classifyresult_bitmap


if __name__ == '__main__':
    grid0 = [[0.0059, 0.0027,3,4],
             [0.0058, 0.0000,3,4],
             [0.0058, 0.0000,3,4],
             [0.0058, 0.0000,3,4]]

    grid1 = [[0.0059, 0.0027, 0.0033, 0.0053, 0.0000],
             [0.0058, 0.0000, 0.0065, 0.0000, 0.0000],
             [0.0064, 0.0067, 0.0053, 0.0016, 0.0000],
             [0.0052, 0.0032, 0.0037, 0.0018, 0.0000],
             [0.0038, 0.0029, 0.0038, 0.0025, 0.0012]]
    grid4 = [[0.0061, 0.0052, 0.0109, 0.0011, 0.0000],
             [0.0059, 0.0027, 0.0033, 0.0053, 0.0000],
             [0.0058, 0.0000, 0.0065, 0.0000, 0.0000],
             [0.0064, 0.0067, 0.0053, 0.0016, 0.0000],
             [0.0052, 0.0032, 0.0037, 0.0018, 0.0000],
             [0.0038, 0.0029, 0.0038, 0.0025, 0.0012],
             [0.0034, 0.0027, 0.0039, 0.0021, 0.0010],
             [0.0016, 0.0014, 0.0022, 0.0020, 0.0005],
             [0.0031, 0.0000, 0.0000, 0.0036, 0.0056],
             [0.0031, 0.0024, 0.0029, 0.0008, 0.0011]]

    print len(grid0) * len(grid0[0])

    pd_result1 = np.array(grid0)
    gridkmeanns = GridKmeans()
    singleGirdIterator = gridkmeanns.singleGirdIterator(pd_result1)

    result2, candidates_df = gridkmeanns.MultipleGirdIterator(singleGirdIterator, target=16, nclasses=4,containCoordinateList=None,ratelimit=None)
    print result2
    print len(result2)

    result3, piecewise_result_info = gridkmeanns.Girdkmeans(result2, candidates_df)
    print result3
    print piecewise_result_info.sort_values("group_var_sum", inplace=False)

    classifyresult_bitmap = gridkmeanns.GirdkmeansClassify(grid1, result3, piecewise_result_info, 3)
    print classifyresult_bitmap
