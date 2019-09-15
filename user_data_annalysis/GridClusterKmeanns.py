#!/usr/bin/python
# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd


class GridKmeanns:

    def isRectangleOverlap(self, rec1, rec2):

        return not (rec1['y2'] < rec2['y1'] or  # rigth
                    rec1['x2'] < rec2['x1'] or  # bottom
                    rec1['y1'] > rec2['y2'] or  # left
                    rec1['x1'] > rec2['x2'])  # top  #重合返回TRUE

    def isRectangleOverlap_list(self, rec1, rec2_list):
        for i in range(len(rec2_list)):
            if not (rec1['y2'] < rec2_list[i]['y1'] or  # rigth
                    rec1['x2'] < rec2_list[i]['x1'] or  # bottom
                    rec1['y1'] > rec2_list[i]['y2'] or  # left
                    rec1['x1'] > rec2_list[i]['x2']  # top  #重合返回TRUE
            ):
                return True
        return False

    def singleGirdIterator(self, grid):
        row = len(grid)
        col = len(grid[0])
        usefularea = pd.DataFrame(
            columns=['x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'RectangleVar', 'RectangleVar_t'])
        for x1 in range(row):
            for y1 in range(col):
                for x2 in range(x1, row):
                    for y2 in range(y1, col):
                        Rectangle = grid[x1:x2 + 1, y1:y2 + 1]
                        rectangleGridCnt = len(Rectangle) * len(Rectangle[0])
                        RectangleVar = Rectangle.var()
                        usefularea = usefularea.append(
                            {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'rectangleGridCnt': rectangleGridCnt,
                             'RectangleVar': RectangleVar, 'RectangleVar_t': rectangleGridCnt * RectangleVar},
                            ignore_index=True)

        usefularea = usefularea.astype(
            dtype={'x1': np.int64, 'x2': np.int64, 'y1': np.int64, 'y2': np.int64, 'rectangleGridCnt': np.int64,
                   'RectangleVar': np.float, 'RectangleVar_t': np.float})
        usefularea = usefularea.reset_index()
        return usefularea

    def MultipleGirdIterator(self, usefularea, target):

        size = len(usefularea)
        if size == 0:
            return []
        path = []
        res = []
        candidates = np.array(usefularea['rectangleGridCnt'])
        self.__dfs(candidates, 0, size, path, res, target, usefularea)
        return res

    def __dfs(self, candidates, begin, size, path, res, target, usefularea):
        # print begin
        if target == 0:
            res.append(path[:])
            return
        if target < 0:
            return

        if len(path) > 10:
            return

        for index in range(begin, size):
            # print "循环内：" + str(index) + str(begin)
            # TODO 不能删除
            # if begin - 1 >= 0:
            # if self.isRectangleOverlap(usefularea.ix[index], usefularea.ix[begin - 1]):
            #    continue
            if len(path) > 0:
                rec2_list = []
                for i in range(len(path)):
                    dict1 = path[i]
                    for (k, v) in dict1.items():
                        rec2_list.append(usefularea.ix[k])
                if self.isRectangleOverlap_list(usefularea.ix[index], rec2_list):
                    continue

            dict = {}
            dict[index] = candidates[index]
            path.append(dict)
            self.__dfs(candidates, index + 1, size, path, res, target - candidates[index], usefularea)
            path.pop()

    def Girdkmeans(self, res, usefularea):
        usefularea_result = pd.DataFrame(
            columns=['class_type', 'nclasses', 'x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'RectangleVar'])
        print type(res)
        for j, row in enumerate(res):
            gridcnt = len(row)
            for i in range(len(row)):
                dict = row[i]
                for (k, v) in dict.items():
                    usefularea_result = usefularea_result.append({
                        'class_type': j, 'nclasses': gridcnt,
                        'x1': usefularea.ix[k]['x1'], 'x2': usefularea.ix[k]['x2'],
                        'y1': usefularea.ix[k]['y1'], 'y2': usefularea.ix[k]['y2'],
                        'rectangleGridCnt': usefularea.ix[k]['rectangleGridCnt'],
                        'RectangleVar': usefularea.ix[k]['RectangleVar'],
                        'RectangleVar_t': usefularea.ix[k]['RectangleVar_t']},
                        ignore_index=True)
            grouped_cnt = usefularea_result.groupby('class_type')
            piecewise_result_info = grouped_cnt['RectangleVar_t'].agg({'var_': sum})
            # print piecewise_result_info
        return usefularea_result, piecewise_result_info


if __name__ == '__main__':
    grid0 = [[1, 1, 1, 1]]

    grid1 = [[0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]]
    grid4 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 1, 4, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 1, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 2, 2, 3, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 1, 2, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 2, 4, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 2, 2, 2, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 1, 3, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 2, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 1, 1, 2, 2]
        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 1]]

    pd_result1 = np.array(grid4)
    # print pd_result1.size
    gridkmeanns = GridKmeanns()
    singleGirdIterator = gridkmeanns.singleGirdIterator(pd_result1)
    # 求均值
    arr_mean = np.mean(pd_result1)
    # 求方差
    arr_var = np.var(pd_result1)
    # print arr_var
    print singleGirdIterator

    # print singleGirdIterator.ix[1]
    # print np.array(singleGirdIterator['rectangleGridCnt'])

    rec1 = singleGirdIterator.ix[5]
    # rec2 = singleGirdIterator.ix[2]

    rec2_list = [singleGirdIterator.ix[0], singleGirdIterator.ix[4]]

    # rec2.append(singleGirdIterator.ix[1])
    # print rec1
    # print rec2
    print gridkmeanns.isRectangleOverlap_list(rec1, rec2_list)

    # print gridkmeanns.isRectangleOverlap(rec2, rec1)

    result2 = gridkmeanns.MultipleGirdIterator(singleGirdIterator, 400)
    print result2
    print len(result2)

    # result3,piecewise_result_info = gridkmeanns.Girdkmeans(result2, singleGirdIterator)
    # print result3,piecewise_result_info
