#!/usr/bin/python
# -*- coding:utf-8 -*-

# from typing import List
from collections import deque, Counter
import numpy as np
import pandas as pd


class Cutgrid:
    '''
    将某一阈值下选中的数据格子，划分切出规则的方块，保证涵盖的选中的格子最多。
    '''
    # 方向数组，它表示了相对于当前位置的 4 个方向的横、纵坐标的偏移量.
    directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    def numGridDomain(self, grid):
        """找出完全相邻接的区块的格子，主要是为了后面计算圈出的格子于总的格子的占比是否正常，当前暂时不用。
        :param grid: type: arrary. definition要切分的格子的二维数组.
        :return: domain_count: type:int definition:不相邻格子总共有多少区域
                 domain_dict: type:list definition:每个区域格子数量
                 domain_bitmap :区域位图0,1标识
        """
        row = len(grid)
        col = len(grid[0])
        domain_dict = []  # 每块领域的相邻连接块数量描述
        if row == 0:
            return 0
        domain_bitmap = [0 for i in range(col * row)]
        marked = [[False for _ in range(col)] for _ in range(row)]
        domain_count = 0  # 相邻领域块计数
        domain_grid_count = 0  # 分割区每个连接块，1的个数
        for i in range(row):
            for j in range(col):
                # 只要是1，且没有被访问过的，进行标记
                if not marked[i][j] and grid[i][j] == 1:
                    domain_count += 1
                    domain_grid_count += 1
                    queue = deque()
                    queue.append((i, j))
                    marked[i][j] = True
                    while queue:
                        cur_x, cur_y = queue.popleft()
                        domain_bitmap[cur_x * col + cur_y] = domain_count
                        for direction in self.directions:
                            new_i = cur_x + direction[0]
                            new_j = cur_y + direction[1]
                            # 如果不越界、没有被访问过、并且还要是1，就继续放入队列，放入队列的同时，标记已经访问过
                            if 0 <= new_i < row and 0 <= new_j < col and not marked[new_i][new_j] and grid[new_i][
                                new_j] == 1:
                                queue.append((new_i, new_j))
                                marked[new_i][new_j] = True
                                domain_grid_count = domain_grid_count + 1
                if domain_grid_count > 0:
                    domain_dict.append(domain_grid_count)
                domain_grid_count = 0
        return domain_count, domain_dict, domain_bitmap

    # TODO 行列只有一个格子特殊的
    # 将特殊区域的奇异点先处理掉
    def outlierHandling(self, grid):
        """主要处理一些特殊奇异点，此步骤也可不做
        :param grid: n*m 的0，1二维数组
        :return: grid：处理后的二维数组
        """
        row = len(grid)
        col = len(grid[0])
        if row == 0:
            return 0
        for i in range(row):
            for j in range(col):
                if grid[i][j] == 1:
                    if j + 1 < col:
                        j = j + 1
                    if grid[i][j] == 1:
                        continue
                    elif grid[i][j] == 0:
                        # 当这个0在边上，在以0为中心的2*3方块除了这个0 全为1时，抹除这个0为1
                        if i == 0 and j - 1 >= 0 and sum(sum(grid[i:i + 2, j - 1:j + 2])) == 5:
                            grid[i][j] = 1
                        if i == (row - 1) and i - 1 and j - 1 >= 0 and sum(sum(grid[i - 1:i + 1, j - 1:j + 2])) == 5:
                            grid[i][j] = 1
                        if j == 0 and i - 1 >= 0 and sum(sum(grid[i - 1:i + 2, j:j + 2])) == 5:
                            grid[i][j] = 1
                        if j == (col - 1) and i - 1 >= 0 and sum(sum(grid[i - 1:i + 1, j - 1:j + 1])) == 5:
                            grid[i][j] = 1
                        # 当这个0在中心，在以0为中心的3*3方块除了这个0 全为1时，抹除这个0为1
                        if i - 1 >= 0 and i + 1 < row and j - 1 >= 0 and j + 1 < col and sum(
                                sum(grid[i - 1:i + 2, j - 1:j + 2])) == 8:
                            grid[i][j] = 1
        return grid

    def maxareaHandling(self, grid, usefulrate, usefulbitmap=None):
        """
        :param grid: type:array  definetion:二维0，1数组
        :param usefulrate: type:flaot.definition:每个矩形中的可有格子占比。
        :param usefulbitmap: definition:在初始划分区域最大矩形的时候，为None没有意义。在用户分类划分格子的过程中使用。
        :return: maxarea：type:int definition:最大矩形的格子数量
        """
        # 遍历所有的矩形，求出最大矩形和矩形内90%都是可用点的矩形。
        row = len(grid)
        col = len(grid[0])
        maxarea = 0
        usefularea = pd.DataFrame(
            columns=['x1', 'x2', 'y1', 'y2', 'rectangleGridCnt', 'usefulRectangleCnt', 'usefulRate'])
        if row == 0:
            return 0
        for x1 in range(row):
            for y1 in range(col):
                for x2 in range(x1, row):
                    for y2 in range(y1, col):
                        # 判断格子是否被标记过，标记过则跳过
                        if usefulbitmap is not None and usefulbitmap[x2:x2 + 1, y2:y2 + 1].sum() == 1:
                            continue
                        Rectangle = grid[x1:x2 + 1, y1:y2 + 1]
                        Rectangle[Rectangle != 1] = 0  # 替换其它不相邻模块的数据为0
                        rectangleGridCnt = len(Rectangle) * len(Rectangle[0])
                        usefulRectangleCnt = Rectangle.sum()
                        if usefulRectangleCnt > 0:
                            usefulRate = round((usefulRectangleCnt * 0.01) / (rectangleGridCnt * 0.01), 4)
                            # TODO 设置奇异点占总局必须高于85%
                            if usefulRate >= usefulrate and usefulRectangleCnt >= maxarea:
                                usefularea = usefularea.append(
                                    {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'rectangleGridCnt': rectangleGridCnt,
                                     'usefulRectangleCnt': usefulRectangleCnt, 'usefulRate': usefulRate},
                                    ignore_index=True)
                            if rectangleGridCnt == usefulRectangleCnt:
                                if (usefulRectangleCnt > maxarea):
                                    maxarea = usefulRectangleCnt
                                    MaxRectangle = Rectangle

        usefularea = usefularea.astype(
            dtype={'x1': np.int64, 'x2': np.int64, 'y1': np.int64, 'y2': np.int64, 'rectangleGridCnt': np.int64,
                   'usefulRectangleCnt': np.int64, 'usefulRate': np.float64})

        usefularea = usefularea[~usefularea['usefulRectangleCnt'] < maxarea]

        # 最大面积
        # if len(usefularea) > 0:
        #    maxusefularea = usefularea.loc[usefularea['rectangleGridCnt'].idxmax()]
        return maxarea, usefularea

    # TODO 合并多个区域块
    def unionMaxarea(self, grid, maxdomain, domain_cnt, usefulrate, usefulbitmap=None):
        """
        :param grid: type：array. definition:二维0，1数组
        :param maxdomain: type:int. definition:最大区域块的格子数量，主要用于判断划出来的最大矩形与最大连接块的可用占比
        :param domain_cnt: type：int. definition:区域块数量，当前都为1，没有合并多个区域块的情况
        :param usefulrate: type:float. definition:通过占比来调整最大矩形的容差率。
        :param usefulbitmap:
        :return: rectangleGridCnt：type:int. definition: 最大矩形的格子数量
                 maxusefulbitmap：type：arrary. definition:划分出的最大矩形的位图标识，1为选中
                 handing_cnt：type：int definition:合并的格子数量,当前都为1.
                 maxRecCoordinateList：type:list. definition:选出的最大矩形的坐标。example:[x1, y1, x2, y2, Cnt]-->[0,0,0,0,1]
        """
        row = len(grid)
        col = len(grid[0])
        # 格子位图
        maxusefulbitmap = np.array([[0] * col] * row)
        maxRecCoordinateList = []  # 划分出来的矩形坐标
        rectangleGridCnt = 0  # 最大格子数
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        handing_cnt = 0  # 处理次数,合并格子的次数
        domainusefullrate = 0  # 可用格子占比，来判断是否再次寻找最大矩形进行合并
        while ((domainusefullrate < 0.8) and (handing_cnt < domain_cnt)):
            grid_handling = grid
            maxarea, usefularea = self.maxareaHandling(grid_handling, usefulrate, usefulbitmap)
            if len(usefularea) == 0:
                break
            if handing_cnt == 0:  # 第一次判断不需要位置，之后的格子最好离上一个格子最近
                maxusefularea = usefularea.loc[usefularea['rectangleGridCnt'].idxmax()]
            else:
                maxusefularea_list = usefularea[usefularea['rectangleGridCnt'] == usefularea['rectangleGridCnt'].max()]

                if len(maxusefularea_list) == 1:
                    maxusefularea = usefularea.loc[usefularea['rectangleGridCnt'].idxmax()]

                else:
                    maxusefularea_list['col_instance'] = maxusefularea_list['y2'] - maxusefularea_list['y1']
                    maxusefularea_list['row_instance'] = maxusefularea_list.apply(
                        lambda x: abs(x1 - int(x['x2'])) if x1 >= int(x['x2']) else abs(x2 - int(x['x1'])), axis=1)
                    maxusefularea_list = maxusefularea_list[
                        maxusefularea_list['row_instance'] == maxusefularea_list['row_instance'].min()]
                    maxusefularea = maxusefularea_list.loc[maxusefularea_list['col_instance'].idxmin()]

            # 最大区域块数量
            maxGridCnt = int(maxusefularea['rectangleGridCnt'])

            # 处理合并区域块过程，当前不可用
            if int(maxusefularea['y1']) < y1 <= int(maxusefularea['y2']):
                print  grid[x1:x2 + 1][int(maxusefularea['y1']):y1 + 1]

            elif int(maxusefularea['y1']) <= y2 < int(maxusefularea['y2']):
                missGrid = grid[x1:x2 + 1, y2 + 1:int(maxusefularea['y2']) + 1]

                missGridCnt = len(missGrid) * len(missGrid[0])
                # print missGrid, missGridCnt
                # 如果缺失格子只有一个
                if missGridCnt == 1:
                    maxusefulbitmap[x1:x2 + 1, y2 + 1:int(maxusefularea['y2']) + 1] = 1
                    rectangleGridCnt = rectangleGridCnt + missGridCnt
                # 如果缺失格子占比小于50%
                elif ((missGrid.sum() * 0.01) / (missGridCnt * 0.01)) >= 0.5:
                    maxusefulbitmap[x1:x2 + 1, y2 + 1:int(maxusefularea['y2']) + 1] = 1
                    rectangleGridCnt = rectangleGridCnt + missGridCnt
                    # 如果缺失格子占比大于50%
                    y2 = int(maxusefularea['y2']) - 1

            x1 = int(maxusefularea['x1'])
            x2 = int(maxusefularea['x2'])
            y1 = int(maxusefularea['y1'])
            y2 = int(maxusefularea['y2'])

            # 对最大区域块赋值为1
            maxusefulbitmap[x1:x2 + 1, y1:y2 + 1] = 1
            rectangleGridCnt = rectangleGridCnt + maxGridCnt
            handing_cnt = handing_cnt + 1
            # 对已经处理过的格子置为0，此作用只在多次合并的时候可用
            grid[x1:x2 + 1, y1:y2 + 1] = 0
            domainusefullrate = round((rectangleGridCnt * 0.01) / (maxdomain * 0.01), 4)
            # 当前只有一个最大矩形，所有该list只有一个数组
            coordinate = [x1, y1, x2, y2, rectangleGridCnt]
            maxRecCoordinateList.append(coordinate)
        return rectangleGridCnt, maxusefulbitmap, handing_cnt, maxRecCoordinateList

    # TODO 切出最大区块结果
    def GridUsefullValue(self, maxusefulbitmap, grid, maxRecCoordinateList):
        """根据选中的最大矩形的位图显示，切出原有数值格子内的数值和最大的矩形。
        :param maxusefulbitmap: type：array二维0，1数值. definition:选中的最大矩形的位图显示.
        :param grid: type：array二维小于1的float数值. definition:用户占比格子
        :param maxRecCoordinateList: type:list. definition:选出的最大矩形的坐标。example:[x1, y1, x2, y2, Cnt]-->[0,0,0,0,1]
        :return: usefvalue: type:list,一维数组. definition:用于存放选中格子的数值， 做用户聚类分析.
                 usefullgridlist: type:array 二维数组. definition:切出选中矩形的区域， 做格子聚类分析，此时坐标产生偏移，左上角的坐标变为(0,0).
        """
        usefullRateValue = []
        for m in range(len(maxusefulbitmap)):
            for n in range(len(maxusefulbitmap[0])):
                if maxusefulbitmap[m][n] == 1:
                    usefullRateValue.append(grid[m][n])
        # 当前coordinate_list只有一个值
        x1 = maxRecCoordinateList[0][0]
        y1 = maxRecCoordinateList[0][1]
        x2 = maxRecCoordinateList[0][2]
        y2 = maxRecCoordinateList[0][3]
        usefullRateGrid = grid[x1:x2 + 1, y1:y2 + 1]
        return usefullRateValue, usefullRateGrid

    def CutGridClassify(self,pd_resul_classify_grid, nclasses, offset_coordinate_list=None):
        """
        :param pd_resul_classify_grid: type:array. definition:通过用户占比数值分类后的格子标识
        :param nclasses: type:int. definition:用户分类数.
        :param coordinate_list: type:list. definition:偏移的坐标标识。即从全量矩形中划分出的矩形的左上角坐标。
        :return:classes_bitmap: type:array. definiton:聚类之后的类别标识，0，1，2，3，4...
                classify_coordinate_list: type:list definiton: 聚类后每个矩形的坐标list
                classify_coordinate_Offset_list: type:list definiton: 聚类后每个矩形的偏移之后的坐标list
        """
        row = len(pd_resul_classify_grid)
        col = len(pd_resul_classify_grid[0])

        classes_bitmap = np.array([[0] * col] * row)
        classify_coordinate_list = []  # 用户聚类后所占的矩形区域的坐标list
        classify_coordinate_Offset_list = []  # 用户聚类后所占的矩形区域的坐标list，偏移坐标。即已左上角顶点为(0,0)的偏移坐标

        for i in range(1, nclasses+1):
            pd_result_domain = np.where(pd_resul_classify_grid == i, 1, 0)
            cutgrid = Cutgrid()
            result, dict, islands = cutgrid.numGridDomain(pd_result_domain)
            if len(dict) == 0:
                return
            maxdomain = max(dict)  # 最大连接快数量
            maxGridCntmaxGridCnt, maxusefulbitmap, handing_cnt, coordinate_list = cutgrid.unionMaxarea(pd_result_domain,maxdomain,domain_cnt=1, usefulrate=1,usefulbitmap=classes_bitmap)
            if coordinate_list is not None:
                if len(coordinate_list) == 0:
                    continue
            classify_coordinate_list.extend(coordinate_list)

            for m in range(row):
                for n in range(col):
                    if maxusefulbitmap[m][n] == 1:
                        classes_bitmap[m][n] = i

        # 没有赋值的格子标识
        for m in range(row):
            for n in range(col):
                if pd_resul_classify_grid[m][n] > 0 and classes_bitmap[m][n] == 0:
                    classes_bitmap[m][n] = -9


        #处理没有赋值的格子
        #mis_value = 0
        #mis_cnt = 0
        #if -99 in classes_bitmap:
        #    for m in range(row):
        #        for n in range(col):
        #            if classes_bitmap[m][n] == -9:
        #                mis_cnt = mis_cnt + 1
        #                mis_value = mis_value + pd_result_grid[m][n]
        # classes_bitmap[classes_bitmap == -99] = round(float(mis_value) / float(mis_cnt))

        if offset_coordinate_list is not None:
            if len(offset_coordinate_list) > 0:
                Offset_x1 = offset_coordinate_list[0][0]
                Offset_y1 = offset_coordinate_list[0][1]
                print Offset_x1, Offset_y1
                for i in range(len(classify_coordinate_list)):
                    x1 = classify_coordinate_list[i][0] - Offset_x1
                    y1 = classify_coordinate_list[i][1] - Offset_y1
                    x2 = classify_coordinate_list[i][2] - Offset_x1
                    y2 = classify_coordinate_list[i][3] - Offset_y1
                    gridcnt = classify_coordinate_list[i][4]
                    classify_coordinate_Offset_list.append([x1, y1, x2, y2, gridcnt])

        return classes_bitmap, classify_coordinate_list, classify_coordinate_Offset_list


if __name__ == '__main__':
    grid1 = [[0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]]
    grid3 = [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
             [0, 0, 0, 1, 0, 0, 1, 1, 1, 1],
             [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
             [0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
             [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]]

    grid2 = [[0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0],
             [0, 0, 0, 1, 1],
             [0, 0, 1, 1, 1],
             [1, 1, 1, 1, 0],
             [1, 1, 1, 0, 0],
             [1, 0, 0, 0, 0]]

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

    cutgrid = Cutgrid()
    result, dict, islands = cutgrid.numGridDomain(grid3)
    print(result, dict)
    maxdomain = max(dict)  # 最大连接快数量
    print grid3

    islands_bit = np.array(islands[0:120]).reshape(12, 10)
    islands_bit = np.array(islands[0:120]).reshape(12, 10)
    print islands_bit
    islands_bit[islands_bit>1]=1

    grid_handling = cutgrid.outlierHandling(islands_bit)
    print "元数据："
    print grid_handling

    maxrectangle, maxarea = cutgrid.maxareaHandling(grid_handling, 0.9, usefulbitmap=None)
    print maxrectangle,maxarea # 处理的矩形区域块


    rectangleGridCnt, maxusefulbitmap, handing_cnt, maxRecCoordinateList = cutgrid.unionMaxarea(grid_handling, maxdomain, domain_cnt=1,usefulrate=0.9,
                                                                    usefulbitmap=None)

    print rectangleGridCnt, maxusefulbitmap, handing_cnt, maxRecCoordinateList

    gridusefullvalue=cutgrid.GridUsefullValue(maxusefulbitmap,grid_handling,maxRecCoordinateList)
    print gridusefullvalue

    classes_bitmap, classify_coordinate_list, classify_coordinate_Offset_list = cutgrid.CutGridClassify(maxusefulbitmap, 2)
    print "第二次分类结果："
    print classes_bitmap, classify_coordinate_list, classify_coordinate_Offset_list
