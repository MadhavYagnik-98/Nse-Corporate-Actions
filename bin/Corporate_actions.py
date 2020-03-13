#!/usr/bin/env python
# coding: utf-8
#importing libraries 
import pandas as pd
from collections import Counter
# from fuzzywuzzy import fuzz
import re
import numpy as np
import logging
import os
import config_reader
import datetime as dt

def create_logger():
    logger = logging.getLogger(__name__)
    if not os.path.exists('../logs'):
        os.makedirs('../logs')
    dt_str = str(dt.datetime.now()).replace(' ', '_' ).replace('-','').replace(':', '').split('.')[0]
    logging.basicConfig(filename='../logs/corporate_actions'+ dt_str+'.log', filemode='a', format='%(process)d  %(asctime)s %(levelname)s %(funcName)s %(lineno)d ::: %(message)s', level=logging.INFO)
    return logger

# importing from config.properties file
def config_imports(logger):
    try:
        config = config_reader.get_config()
        return config
    except Exception as e:
        logger.exception('ERROR:: Some issue in reading the Config...check config_reader.py script in bin Folder....')
        raise e
def special_div(req):
    string_lq=(re.findall('specialdividend\d*\.?\d+',req) or re.findall('spldiv.\d*\.?\d+',req))
    return string_lq
#     print(string_lq)
def interimdiv(req):
    interim_div=(re.findall('interimdividend\d*\.?\d+',req) or re.findall('specialinterimdividend\d*\.?\d+',req) or re.findall('inerimdividend\d*\.?\d+',req) or re.findall('intdiv\d*\.?\d+',req) or re.findall('interimdiv\d*\.?\d+',req) or re.findall('interimdividendre\d*\.?\d+',req) or re.findall('intermdividend\d*\.?\d+',req) or re.findall('intdividend\d*\.?\d+',req))
    return interim_div
def premium(req):
    premium_find=(re.findall('premium\d*\.?\d+',req) or re.findall('premiumof\d*\.?\d+',req))
    return premium_find
def dividend(req):
    dividend_find=(re.findall('/dividend\d*\.?\d+',req) or (re.findall(r'^dividend\d*\.?\d+',req)))
    return dividend_find
def bonus(req):
    bonous_find=re.findall('bonus\d*\d.?\d*',req)
    return bonous_find
def finaldiv(req):
    finaldiv_find=re.findall('finaldividend\d*\.?\d+',req)
    return finaldiv_find
def rights(req):
    rights_find=(re.findall(r'rights\d*\d.?\d*',req) or re.findall(r'rights:\d*\d.?\d*',req))
    return rights_find
def facevaluediv(req):
    facevaluediv_find=re.findall(r'from\d*\d.?\d*\w+',req)
    return facevaluediv_find
def distribution(req):
    distribution_find=re.findall(r'^distribution\d*\d.?\d*',req)
    return distribution_find   
def fourtdistribution(req):
    fourtdistribution_find=re.findall(r'^fourthdistribution\d*\d.?\d*',req)
    return fourtdistribution_find
def interest_payment(req):
    interest_find=re.findall('payment\d*\d.?\d*',req)
    return interest_find
def return_capital(req):
    capital_find=(re.findall('turnofcapitalre\d*\d.?\d*',req) or re.findall('turnofcapital\d*\d.?\d*',req))
    return capital_find
def capital_reduction(req):
    reduction_find=re.findall('capitalduction\d*\.?\d+\w+\d*\.?\d+',req)
    return reduction_find
def consolidation(req):
    consolidation_find=re.findall('consolidation\d*\.?\d+\w+\d*\.?\d+',req)
    return consolidation_find

def main():
	logger = create_logger()
	config = config_imports(logger)
	logger.info('Config == %s', config)
	input_csv=pd.read_csv("../inputs/CA_LAST_24_MONTHS.csv")
	input_csv.rename(columns={"Ex-Date":"ExDate","Face Value(Rs.)":"FaceValue"})
	converting_lower=input_csv['Purpose'].str.lower()
	list_of_converted=list(converting_lower)
	cleared_purpose_list=[]
	for no_val in list_of_converted:
	    if re.search(r'\w+',no_val):
	        for ch in [' re',' rs','-'," "]:
	            no_val=no_val.replace(ch,'').strip()
	        cleared_purpose_list.append(no_val)
	list_spec=[]
	for req in cleared_purpose_list:
	    x=special_div(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    list_spec.append(numeric)
	input_csv['SpecialDividend']=pd.DataFrame(list_spec).astype(float)
	list_interim=[]
	for req in cleared_purpose_list:
	    x=interimdiv(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    list_interim.append(numeric)
	input_csv['InterimDividend']=pd.DataFrame(list_interim).astype(float)
	list_premium=[]
	for req in cleared_purpose_list:
	    x=premium(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    list_premium.append(numeric)
	input_csv['Premium']=pd.DataFrame(list_premium).astype(float)
	list_dividend=[]
	for req in cleared_purpose_list:
	    x=dividend(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    list_dividend.append(numeric)
	input_csv['Dividend']=pd.DataFrame(list_dividend).astype(float)
	list_bonous=[]
	for req in cleared_purpose_list:
	    x=bonus(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    numeric=list(map(int, numeric))
	    list_bonous.append(numeric)
	#     list_rights.append(numeric)
	    final_list_bonous=[]
	    for num in list_bonous:
	        if len(num)==2:
	            result=np.round(((num[1])/num[1]+num[0]),3)
	#             result=list(map(float, result))
	            final_list_bonous.append(result)
	        else:
	            result=1
	#             result=list(map(int, result))
	            final_list_bonous.append(result)
	input_csv['Bonus']=pd.DataFrame(final_list_bonous).astype(float)
	list_finaldiv=[]
	for req in cleared_purpose_list:
	    x=finaldiv(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	    list_finaldiv.append(numeric)
	input_csv['FinalDividend']=pd.DataFrame(list_finaldiv).astype(float)
	list_rights=[]
	for req in cleared_purpose_list:
	    x=rights(req)
	    numeric=re.findall(r'\d*\.?\d+',str(x))
	    numeric=list(map(int, numeric))
	    list_rights.append(numeric)
	    final_list_rights=[]
	    for num in list_rights:
	        if len(num)==2:
	            result=np.round((num[0]/num[1]),3)
	            final_list_rights.append(result)
	        else:
	            final_list_rights.append('1')
	input_csv['Rights']=pd.DataFrame(final_list_rights).astype(float)
	facevaluediv_split=[]
	for req in cleared_purpose_list:
	    x=facevaluediv(req)
	    numeric=re.findall('\d*\.?\d+',str(x))
	#     numeric=numeric.split(':')
	    numeric=list(map(int, numeric))
	    facevaluediv_split.append(numeric)
	    final_list_split=[]
	    for num in facevaluediv_split:
	        if len(num)==2:
	            result=np.round((num[0]/num[1]),3)
	            final_list_split.append(result)
	        else:
	            final_list_split.append('1')
	input_csv['FaceValueSplit']=pd.DataFrame(final_list_split).astype(float)

	distribution_list=[]
	for req in cleared_purpose_list:
	    x=distribution(req)
	    numeric=re.findall('\d*\d.?\d*',str(x).replace('p',' '))
	    distribution_list.append(numeric)
	input_csv['Distribution']=pd.DataFrame(distribution_list).astype(float)
	fourthdistribution_list=[]
	for req in cleared_purpose_list:
	    x=fourtdistribution(req)
	    numeric=re.findall('\d*\d.?\d*',str(x).replace('/',' '))
	    fourthdistribution_list.append(numeric)
	input_csv['FourthDistribution']=pd.DataFrame(fourthdistribution_list).astype(float)
	interest_payment_list=[]
	for req in cleared_purpose_list:
	    x=interest_payment(req)
	    numeric=re.findall('\d*\d.?\d*',str(x).replace('p',' '))
	    interest_payment_list.append(numeric)
	input_csv['InterestPayment']=pd.DataFrame(interest_payment_list).astype(float)
	return_capital_list=[]
	for req in cleared_purpose_list:
	    x=return_capital(req)
	    numeric=re.findall('\d*\d.?\d*',str(x).replace('p',' '))

	    return_capital_list.append(numeric)
	input_csv['ReturnOfCapital']=pd.DataFrame(return_capital_list).astype(float)
	capital_reduction_list=[]
	for req in cleared_purpose_list:
	    x=capital_reduction(req)
	    numeric=re.findall('\d*\.?\d+\d*\.?\d+',str(x).replace('to',','))
	#     consolidation_list.append(numeric)
	    numeric=list(map(float, numeric))
	    capital_reduction_list.append(numeric)
	    final_list_reduction=[]
	    for num in capital_reduction_list:
	        if len(num)==2:
	            result=np.round((num[0]/num[1]),3)
	            final_list_reduction.append(result)
	        else:
	            final_list_reduction.append('1')
	input_csv['CapitalReduction']=pd.DataFrame(final_list_reduction).astype(float)
	consolidation_list=[]
	for req in cleared_purpose_list:
	    x=consolidation(req)
	    numeric=re.findall('\d*\.?\d+\d*\.?\d+',str(x).replace('to.',','))
	#     consolidation_list.append(numeric)
	    numeric=list(map(float, numeric))
	    consolidation_list.append(numeric)
	    final_list_consolidation=[]
	    for num in consolidation_list:
	        if len(num)==2:
	            result=np.round((num[0]/num[1]),3)
	            final_list_consolidation.append(result)
	        else:
	            final_list_consolidation.append('1')
	input_csv["Consolidation"]=pd.DataFrame(final_list_consolidation).astype(float)

	input_csv.fillna(1,inplace=True)
	# input_csv['Factors']=input_csv['SpecialDividend']*input_csv['InterimDividend']*input_csv['Dividend']*input_csv['Bonus']*input_csv['FinalDividend']*input_csv['FaceValueSplit']*input_csv['Distribution']*input_csv['FourthDistribution']*input_csv['InterestPayment']*input_csv['ReturnOfCapital']*input_csv['CapitalReduction']*input_csv['Consolidation']
	input_csv=input_csv.rename(columns={"Ex-Date":"ExDate","Face Value(Rs.)":"FaceValue"})
	input_csv.to_csv('../inputs/Corporate Actions.csv',index=False)
if __name__ == "__main__":
        main()








