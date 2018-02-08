'''
Created on Aug 8, 2017
'''

import pickle
from math import cos, asin, sqrt
import numpy as np
import requests
from random import shuffle
from copy import deepcopy
import time
import settings

def distance(p1, p2):
    #输入为两个以字典形式存储的点
    #输出两点的直线距离（单位：米）

    lat1 = p1['lat']
    lon1 = p1['lng']
    lat2 = p2['lat']
    lon2 = p2['lng']
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742000 * asin(sqrt(a)) #2*R*asin...
    #to meters

def getDistanceMatrix(point_list):
    #输入为点的列表
    #输出为n*n的距离矩阵

    #计算基于直线距离的cost matrix
    result = []
    for p1 in point_list:
        temp = []
        for p2 in point_list:
            temp.append(distance(p1, p2))
        result.append(temp)

    return result

def trans(data):
    #矩阵（二维列表）转置
    return np.array(data).transpose().tolist()

def getCostMatrix(point_list):
    #输入为点的列表
    #输出为高德得到的距离（单位：米）和时间（单位：秒）矩阵

    #使用高德-距离测量，得到距离和时间

    origins = ''
    for p in point_list:
        origins += (str(p['lng']) + ',' + str(p['lat']) + '|')

    origins = origins[:-1]

    distances = []
    durations = []

    for p in point_list:
        destination = str(p['lng']) + ',' + str(p['lat'])
        key = settings.key
        parameters = {'origins': origins, 'destination': destination, 'key': key}
        base = 'http://restapi.amap.com/v3/distance'
        response = requests.get(base, parameters)
        answer = response.json()
        dis_temp = []
        dur_temp = []

        for result in answer['results']:
            dis_temp.append(int(result['distance']))
            dur_temp.append(int(result['duration']))

        distances.append(dis_temp)
        durations.append(dur_temp)

    return trans(distances), trans(durations)
    #与常用结果可能需要转置
    #已使用trans转置

def calcCost(data, currentsolution):
    #输入
    ####data               时间或距离矩阵
    ####currentsolution    当前路线
    #输出为整条路线的距离或时间

    cost = 0
    currentpoint = currentsolution[0]

    for point in currentsolution[1:]:
        cost += data[currentpoint][point]
        currentpoint = point

    return cost

def solve(data, currentsolution, p_list, VR_list, truck):
    #输入
    ####data                距离矩阵
    ####currentsolution     当前的路线
    ####p_list              全部点的列表
    ####VR_list             VR点索引的列表
    ####truck               当前路线使用truck的信息
    #输出为改进后的路线和总距离

    #采用3-opt方法对路线进行改进

    currentcost = calcCost(data, currentsolution)

    while(True):
        tempcost = currentcost
        tempsolution = currentsolution

        for i in range(1, len(currentsolution) - 2):
            for j in range(i + 1, len(currentsolution) - 1):
                for k in range(j + 1, len(currentsolution)):
                    t1 = currentsolution[i:j]
                    t2 = currentsolution[j:k]
                    head = currentsolution[:i]
                    tail = currentsolution[k:]

                    t1r = list(reversed(t1))
                    t2r = list(reversed(t2))

                    temp_solution_set = []
                    temp_solution_set.append(head + t1 + t2r + tail)
                    temp_solution_set.append(head + t1r + t2 + tail)
                    temp_solution_set.append(head + t2 + t1 + tail)
                    temp_solution_set.append(head + t2r + t1 + tail)
                    temp_solution_set.append(head + t2 + t1r + tail)
                    temp_solution_set.append(head + t2r + t1r + tail)

                    for item in temp_solution_set:
                        feasible = feasibleCapacity(p_list, item, VR_list, truck)
                        #考虑可行性
                        #只考虑了每个点容量

                        if feasible:
                            item_cost = calcCost(data, item)
                            if item_cost < tempcost:
                                tempcost = item_cost
                                tempsolution = item

        if tempcost < currentcost - 0.001:
            currentcost = tempcost
            currentsolution = tempsolution
        else:
            break

    return currentcost, currentsolution

def getCriterion(data, point_list, index, L, truck):
    #输入
    ####data          距离矩阵
    ####point_list    全部点的列表
    ####index         插入的点和位置信息，将k插入i，j之间
    ####L             路线长度
    ####truck         货车信息
    #输出点插入路线后的评价指标，越小越好

    lam = settings.lam # 加权系数

    i = index[0]
    j = index[1]
    k = index[2]

    c_TD = data[i][k] + data[k][j] - data[i][j]

    c1 = point_list[k]['cube'] / truck['cube']
    c2 = point_list[k]['weight'] / truck['weight']
    c_C = max(c1, c2) * L

    c = c_TD - lam * c_C

    return c

def feasibleCalcTravelTime(timeMatrix, route):
    #输入时间矩阵和当前路线
    #返回从第一家vendor到FC的总路途时间

    travel_time = calcCost(timeMatrix, route[1:])
    return travel_time

def point2ServiceTime(point, isVR):
    #输入点的信息和是否为VR
    #根据箱数输出服务时间

    #估算服务时间
    carton = point['carton']
    result = settings.calcServiceTime(carton)

    if isVR:
        return result * settings.VR_allowance
    else:
        return result

def feasibleCalcServiceTime(p_list, route, VR_list):
    #输入点的列表、当前路线和VR索引列表
    #返回整条路线的总服务时间

    service_time = 0
    for i in route[1:-1]:
        if i in VR_list:
            service_time += point2ServiceTime(p_list[i], True)
        else:
            service_time += point2ServiceTime(p_list[i], False)

    return service_time

def feasibleTime(p_list, route, VR_list, timeMatrix):
    #输入点的列表、当前路线、VR索引列表和时间矩阵
    #计算整条路线的总时间
    #返回boolean，是否满足时间可行性

    upperbound = settings.upperbound

    travel_time = feasibleCalcTravelTime(timeMatrix, route)
    service_time = feasibleCalcServiceTime(p_list, route, VR_list)

    total_time = travel_time * settings.TT_allowance + service_time

    if total_time <= upperbound:
        return True
    else:
        return False

def feasibleCapacity(p_list, route, VR_list, truck):
    #输入点的列表、当前路线、VR索引列表和货车信息
    #核算每一个点的货量和容量
    #返回boolean，是否满足容量可行性

    weight = 0
    cube = 0
    weight_bound = 0
    cube_bound = 0

    for i in route[1:-1]:
        if i in VR_list:
            weight += p_list[i]['weight']
            cube += p_list[i]['cube']
        else:
            weight_bound += p_list[i]['weight']
            cube_bound += p_list[i]['cube']

    weight_bound = max(weight_bound, truck['weight'])
    cube_bound = max(cube_bound, truck['cube'])

    for i in route[1:-1]:
        if i in VR_list:
            weight -= p_list[i]['weight']
            cube -= p_list[i]['cube']
        else:
            weight += p_list[i]['weight']
            cube += p_list[i]['cube']

        if not (weight <= weight_bound and cube <= cube_bound):
            return False

    return True

def feasibleCarton(p_list, route, VR_list):
    #输入为点的列表、当前路线、VR索引列表
    #返回boolean，不需要额外搬运工为True

    carton_before = 0
    carton_after = 0

    for i in route[1:-1]:
        carton_after += p_list[i]['carton']
        if i not in VR_list:
            carton_before += p_list[i]['carton']

    loading_before = carton_before // 400
    loading_after = carton_after // 400

    if loading_after > loading_before:
        return False
    else:
        return True


def main():

    print(time.asctime( time.localtime(time.time()) ), 'start')

    #读取数据
    with open('tempV.txt', 'rb') as f:
        V_header = pickle.load(f)
        V_data = pickle.load(f)
        V_data_dict = pickle.load(f)

    with open('tempA.txt', 'rb') as f:
        depot = pickle.load(f)
        A_data = pickle.load(f)

    with open('tempT.txt', 'rb') as f:
        trucks = pickle.load(f)

    #针对每条AITS路线进行调整
    for truck_id in A_data.keys():
        ###获取VReturn set
        candidate = []
        area_r = 2000
        while len(set(candidate)) + len(A_data[truck_id]) < settings.size and area_r <= settings.radius_bound:
            for AITS in A_data[truck_id]:
                for VR in V_data_dict:
                    if ('failure' not in VR.keys()) and ('recommend' not in VR.keys()):
                        d = distance(AITS, VR)
                        if d < area_r:
                            candidate.append(VR['index'])
            area_r += 1000

        candidate = set(candidate)

        ###记录全部点，数据准备
        all_point = []

        for item in A_data[truck_id]:
            all_point.append(item)
        for i in candidate:
            all_point.append(V_data_dict[i])
        all_point.append(depot)

        route0 = [len(all_point) - 1]
        route0.extend(range(len( A_data[truck_id] )))
        route0.append(len(all_point) - 1)

        VR_index = list(range(len(all_point)))
        for p in set(route0):
            VR_index.remove(p)
        #记录all_point中哪些是VR

        distances_s = getDistanceMatrix(all_point)
        distances, durations = getCostMatrix(all_point)

        '''
        with open('./test/' + truck_id + '_data.txt', 'wb') as f:
            pickle.dump(distances, f, True)
            pickle.dump(durations, f, True)
            #再放一些别的
            pickle.dump(all_point, f, True)
            pickle.dump(VR_index, f, True)
        '''

        ###生成AITS派车初始解
        route_set = []
        cost_set = []

        for i in range(len(route0)):
            temp = route0[1:-1]
            shuffle(temp)
            temp = [route0[0]] + temp + [route0[-1]]
            cost, solution = solve(distances_s, temp, all_point, VR_index, trucks[truck_id])
            route_set.append(solution)
            cost_set.append(cost)

        cost_AITS = min(cost_set)
        route_AITS = route_set[ cost_set.index(min(cost_set)) ]

        ###完成准备工作
        residual_point = deepcopy(VR_index)
        current_route = route_AITS
        current_cost = cost_AITS

        ###开始选择VR插入
        while True:
            insert_index = []
            for k in residual_point:
                i = current_route[0]
                for j in current_route[1:]:
                    temp_index = current_route.index(i) + 1
                    temp_route  = current_route[:temp_index] + [k] + current_route[temp_index:]

                    #检查可行性
                    carton_count = feasibleCarton(all_point, temp_route, VR_index)
                    feasible_time = feasibleTime(all_point, temp_route, VR_index, durations)
                    feasible_capacity = feasibleCapacity(all_point, temp_route, VR_index, trucks[truck_id])

                    feasible_insert = carton_count and feasible_time and feasible_capacity
                    if feasible_insert:
                        #计算criterion并比较
                        if insert_index == []:
                            insert_index = [i, j, k]
                            criterion = getCriterion(distances_s, all_point, insert_index,
                                                     current_cost, trucks[truck_id])
                        else:
                            temp_insert_index = [i, j, k]
                            temp_criterion = getCriterion(distances_s, all_point, temp_insert_index,
                                                          current_cost, trucks[truck_id])
                            if temp_criterion < criterion:
                                criterion = temp_criterion
                                insert_index = temp_insert_index

                    i = j
                    #一个可能插入点判断结束

            if insert_index == []:
                #如果没有可以插入，则调整结束
                break

            #路线调整
            index_j = current_route.index(insert_index[0]) + 1
            current_route.insert(index_j, insert_index[2])#插入j前面
            residual_point.remove(insert_index[2])
            #最好把k再加到一个列表里，以便后续推荐

            all_point[insert_index[2]]['recommend'] = truck_id    #记回字典

            #更新插入结果，线路优化
            new_cost, new_route = solve(distances_s, current_route, all_point, VR_index, trucks[truck_id])
            current_cost = new_cost
            current_route = new_route

        ###本路线插入结束，收尾工作
        '''
        with open('./test/' + truck_id + '_result.txt', 'wb') as f:
            pickle.dump(all_point, f, True)
            pickle.dump(VR_index, f, True)
            pickle.dump(current_route, f, True)
            pickle.dump(current_cost, f, True)
        '''

        print(time.asctime( time.localtime(time.time()) ), truck_id + ' done', len(VR_index) - len(residual_point))


    ###全部路线完成，输出最后结果
    with open('output.txt', 'wb') as f:
        pickle.dump(V_data_dict, f, True)

    print(time.asctime( time.localtime(time.time()) ), 'all done')


if __name__ == '__main__':
    main()
