#!/usr/bin/python
# -*- coding:utf-8 -*-

from pyspark import SparkContext
from pyspark.sql import HiveContext
import pandas as pd
import numpy as np
import json
import argparse
import pymysql
pymysql.install_as_MySQLdb()
from ZebraPyApi.datasources.mysqldb import connect

import operator
import  sys
import os
import logging
reload(sys)
sys.setdefaultencoding("utf-8")

class Basicmodule:
    _val_status = 0

    # 字典转json
    def Dict_json(self, dict):
        return json.dumps(dict, ensure_ascii=False)

    def data_sql_str(self, table, dimensionlist, measuretarget):
        dimension_str = dimensionlist
        sql_str_list = ["select ", dimension_str, ',' + measuretarget, " from ", table]
        sql_str = ' '.join(sql_str_list)
        return sql_str

    # 数据获取 #
    def exec_hql(self, hql_str, sc):
        df = sc.sql(hql_str)
        return df

    def is_float(self, frac):
        try:
            float(frac)
            return True
        finally:
            return False

    #    def map_to_pandas(self,rdd):
    #        return [pd.DataFrame(list(rdd))]

    #    def toPandas(self,df, n_partitions=None):
    #        if n_partitions is not None:
    #            df = df.repartition(n_partitions)
    #        df_pd = df.rdd.mapPartitions(self.map_to_pandas).collect()
    #        df_pd = pd.concat(df_pd)
    #        df_pd.columns = df.columns
    #        return df_pd

    def Read_data_table(self, table, dimensionlist, measuretarget, frac=None):
        # 生成查询SQL
        sql_str = self.data_sql_str(table, dimensionlist, measuretarget)
        print "执行查询的SQL语句：" + sql_str
        sc = SparkContext().getOrCreate()
        sqlContext = HiveContext(sc)
        spark_dataframe = sqlContext.sql(sql_str)
        print "数据查询表成功，正在处理中...."

        pandas_dataframe = spark_dataframe.toPandas()
        print "数据转换padans 成功。"
        if self.is_float(frac) == True:
            read_dataframe = pandas_dataframe.sample(n=None, frac=frac)
        else:
            read_dataframe = pandas_dataframe
        return read_dataframe

    # ## 初始化mysql 连接 ##
    # loc 线下库：0, 线上库：1
    def exec_mysql(self,request_id,result,prod_env=1):
        sql_str_list = ["update db.table_name set analysis_result = \'", result, "\' where request_id= ", str(request_id)]
        sql_str = ' '.join(sql_str_list)
        print "插入mysql库的sql：" + sql_str
        if prod_env == 1:
            # jdbcRef
            conn = connect("datastat_product")
        else:
            conn = pymysql.connect(
                host="0.0.0.0",
                user="user_name",
                password="password",
                db="databasename",
                port=xxxx
            )
        cursor = conn.cursor()
        cursor.execute(sql_str)
        conn.commit()
        cursor.close()
        conn.close()

    # 初始化 zebra log #
    def init_log(self):
        container_path = os.path.dirname(os.path.abspath(__file__))

        # 这里定制自己的zebra日志logger，并在使用zebra-py-api前初始化，那么zebra会直接使用这个logger
        logger = logging.getLogger("zebra")
        logger.setLevel(logging.INFO)
        #os.system("mkdir -p " + log_dir)
        #os.system("ls -l " + log_dir)
        dir_path=os.path.dirname(container_path) + "/zebra.log"
        print "mysql日志文件:" + dir_path
        #if not os.path.exists(dir_path):
        #    os.makedirs(dir_path)
        fh = logging.FileHandler(dir_path)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)



    def operator_get_truth(self,judge_value, relate, threshold):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '=': operator.eq}
        return ops[relate](judge_value, threshold)




if __name__ == '__main__':


    '''参数变量
        # _val_dimensionlist 维度列表
        # _val_table_name 数据表名
        # _val_cuts 切片维数
        # _val_nclasses 用户聚类数
        # _val_status 执行状态：1->成功；0->失败
        # _val_message 执行信息
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("--table", help="table name")
    parser.add_argument("--column_list", help="column sets")
    parser.add_argument("--measuretarget", help="measuretarget")
    parser.add_argument("--request", help="request id")

    args = parser.parse_args()

    _val_table_name = args.table
    _val_dimensionlist = args.column_list
    _val_measuretarget = args.measuretarget
    # arg_dict['request_id'] = int(args.request)

    _val_status = 0
    _val_message = ''
    _val_frac = False

    print "表名：" + _val_table_name
    print "字段list：：" + _val_dimensionlist

    # 数据读取
    print "开始数据读取...."

    # df = pd.read_csv('/Users/Documents/data_example/ana_baseuser_pboctype.txt', delimiter='\t')
    # column_headers = list(df.columns.values)
    # df = df.sample(n=None, frac=0.0005)

    # df=df.drop(['user_id','customer_no','report_id_new'],axis=1)
    # df=df.select_dtypes(include=None, exclude=[np.float64,np.int64])
    # df_train = df.select_dtypes(include=[np.float64, np.int64], exclude=None)
    # print df_train.info()

    basicmodule = Basicmodule()
    basicmodule.init_log()
    table_data = basicmodule.Read_data_table(_val_table_name, _val_dimensionlist, _val_measuretarget, frac=None)
    print type(table_data)
    table_data = table_data.fillna(0)
    dimensionlist = table_data.columns[0:]
    print dimensionlist
