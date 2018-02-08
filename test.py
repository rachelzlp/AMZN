'''
Created on Aug 28, 2017
'''
import getAITS, getVReturn, getTrucks, insertVR_new, putResult
import sys
import os

#以命令行的形式调用
#test.py AITS.xlsx VR.xls
AITS_name = sys.argv[1]
VR_name = sys.argv[2]

#读取AITS、VR和货车的数据
getAITS.main1(AITS_name)
print('AITS')
getVReturn.main1(VR_name)
print('VR')
getTrucks.main1()
print('truck')

#派车方案调整、结果输出
insertVR_new.main()
putResult.main()
print('All done')

#需要一些收尾，temp文件删除等工作
os.remove('tempA.txt')
os.remove('tempV.txt')
os.remove('tempT.txt')
os.remove('output.txt')
