'''
Created on Aug 28, 2017
'''

#AMAP key
key = ''


#VR candidate set
size = 15   #both AITS and VR
radius_bound = 5000 #upper bound

#criterion weighting coefficient
lam = 1

#total time upper bound
#8:30~15:30
upperbound = 25200

#calc service time
def calcServiceTime(carton):
    #根据箱数估算服务时间
    #10件以下15分钟
    #以上每件额外30s
    if carton <= 10:
        result = 900
    else:
        result = 900 + 30 * (carton - 10)

    return result

#VR service time allowance
VR_allowance = 1.1

#travel time allowance
TT_allowance = 1.4
