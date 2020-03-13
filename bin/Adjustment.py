#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import re
import pyodbc
import csv
import datetime as dt
import pandasql
input_csv=pd.read_csv("../inputs/2018-20.csv",usecols=('SYMBOL','SERIES','CLOSE','PREVCLOSE','TIMESTAMP'))
input_corporate=pd.read_csv("../inputs/Corporate Actions.csv")
input_csv_1=pd.read_csv("../inputs/2018-20.csv")


def combining_data(input_csv,input_corporate):
 	input_corporate.rename(columns={"Ex-Date":"ExDate","Face Value(Rs.)":"FaceValue"})
 	input_corporate.columns = map(str.lower, input_corporate.columns)
 	input_csv.columns = map(str.lower, input_csv.columns)
 	input_csv['timestamp']= pd.to_datetime(input_csv['timestamp']).dt.date
 	input_corporate['exdate'] = pd.to_datetime(input_corporate['exdate']).dt.date
 	sub_data = pandasql.sqldf("SELECT a.symbol,a.company,a.series,a.facevalue,a.purpose,a.exdate,a.specialdividend,a.interimdividend,a.premium,a.dividend,a.bonus,a.finaldividend,a.rights,a.facevaluesplit,a.distribution,a.fourthdistribution,a.interestpayment,a.returnofcapital,a.capitalreduction,a.consolidation,(SELECT close FROM input_csv WHERE symbol=a.symbol AND series=a.series AND timestamp=a.exdate) AS ext_price,c.prevclose as cum_price,c.timestamp as cum_date from input_corporate a inner join input_csv c on a.symbol=c.symbol AND a.series=c.series AND c.timestamp=(SELECT MAX(timestamp) FROM input_csv WHERE symbol=a.symbol AND series=a.series AND timestamp<a.exdate)", globals())
 	modified_data=sub_data
 	modified_data['interimdividend']=round((modified_data['cum_price']-modified_data['interimdividend'])/(modified_data['cum_price']),3)
 	modified_data['finaldividend']=round((modified_data['cum_price']-sub_data['finaldividend'])/(modified_data['cum_price']),3)
 	modified_data['dividend']=round((modified_data['cum_price']-modified_data['dividend'])/(modified_data['cum_price']),3)
 	# modified_data['finaldividend']=round((modified_data['cum_price']-modified_data['finaldividend'])/(modified_data['cum_price']),3)
 	modified_data['fourthdistribution']=round((modified_data['cum_price']-modified_data['fourthdistribution'])/(modified_data['cum_price']),3)
 	modified_data['distribution']=round((modified_data['cum_price']-modified_data['distribution'])/(modified_data['cum_price']),3)
 	rights_calc=((modified_data['cum_price']+(modified_data['premium']*modified_data['rights']))/(1+modified_data['rights']))
 	modified_data['rights']=rights_calc/modified_data['cum_price']
 	modified_data['rights']=round(modified_data['rights'],3)
 	modified_data['returnofcapital']=round((modified_data['cum_price']-modified_data['returnofcapital'])/(modified_data['cum_price']),3)
 	modified_data['interestpayment']=round((modified_data['cum_price']-modified_data['interestpayment'])/(modified_data['cum_price']),3)
 	modified_data['factors']=round(((modified_data['interimdividend']*modified_data['dividend']*modified_data['finaldividend']*modified_data['returnofcapital']*modified_data['fourthdistribution']*modified_data['distribution']*modified_data['interestpayment']*modified_data['rights']*modified_data['consolidation'])/(modified_data['facevaluesplit']*modified_data['bonus']*modified_data['capitalreduction'])),3)
 	modified_data.loc[modified_data['factors']<=0,'factors']=1
 	modified_data.fillna(1,inplace=True)
 	# modified_data.to_csv('../inputs/cleaned_data.csv',index=False)
 	return modified_data
def adjustment_func(input_csv_1):
	input_csv_1.columns = map(str.lower, input_csv_1.columns)
	input_csv_1['factors']=1
	modified_data=combining_data(input_csv,input_corporate)
	adjustment_function=pandasql.sqldf("SELECT s.*,d3.symbol,d3.series,d3.close,d3.open,d3.high,d3.low,d3.last,d3.timestamp,s.factors*d3.factors as factMul from modified_data s inner join input_csv_1 d3 where s.series=d3.series and s.symbol=d3.symbol and d3.timestamp<s.exdate", locals())
	adjustment_function['last_adj']=round(adjustment_function['last']*adjustment_function['factMul'],3)
	adjustment_function['low_adj']=round(adjustment_function['low']*adjustment_function['factMul'],3)
	adjustment_function['high_adj']=round(adjustment_function['high']*adjustment_function['factMul'],3)
	adjustment_function['open_adj']=round(adjustment_function['open']*adjustment_function['factMul'],3)
	adjustment_function['closea']=round((adjustment_function['close'].astype(float))*(adjustment_function['factMul'].astype(float)),3)
	adjustment_function=adjustment_function['symbol','company','series','open','high','low','close','last','last_adj','low_adj','high_adj','open_adj','closea']
	adjustment_function.to_csv('adjusment.csv',index=False)
	return adjustment_function
def main():
	adjustment=adjustment_func(input_csv_1)
if __name__ == "__main__":
        main()





