'''
Created on Aug 3, 2017
'''

import xlrd
import pickle
import requests
import settings

def readAITS(filename):
    #输入为文件名
    #返回dict，key是车牌号，value是AITS点的list

    #由于不需要往回写，所以直接读需要的信息就好
    #只读取车牌号为京字开头的信息
    #对地址和城市信息做出预处理

    workbook = xlrd.open_workbook(filename)
    table = workbook.sheets()[1]

    data = {}

    for i in range(1, table.nrows):
        name = table.cell(i, 0).value
        truck = table.cell(i, 2).value
        if truck[0] == '京' and name != '北京库房' and int( table.cell(i, 8).value ) > 0:
            temp = {}
            #temp['vendor_code'] = table.cell(i, j).value 暂时没有，看要不要放vendor name
            if table.cell(i, 3).value == '三河':#三河不是city级别
                temp['city'] = '廊坊'
            else:
                temp['city'] = table.cell(i, 3).value
            temp['address'] = table.cell(i, 4).value

            if temp['address'][0:2] == '河北' and temp['city'][0:2] == '北京':
                temp['city'] = ''

            temp['carton'] = int( table.cell(i, 8).value )
            #temp['units'] = table.cell(i, j).value 暂时也没有，也不知道有没有用
            temp['weight'] = float( table.cell(i, 16).value )
            temp['cube'] = float( table.cell(i, 15).value )
            #temp['c_data'] = table.cell(i, j).value#不知道有没有用
            temp['arrive_time'] = table.cell(i, 6).value
            temp['leave_time'] = table.cell(i, 7).value

            if truck in data.keys():
                data[truck].append(temp)
            else:
                data[truck] = [temp]

    return data

def geocode(item_list):
    #输入为点的list
    #无返回值，对输入值添加lat和lng属性

    #针对订单列表求取经纬度
    #选择使用高德

    for item in item_list:
        #每个item为一条订单
        #lng 经度
        #lat 纬度
        key = settings.key
        address = item['address'].replace(' ','').replace('\n', '')
        city = item.get('city', '')

        parameters = {'address': address, 'key': key, 'output': 'json', 'city': city}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        response = requests.get(base, parameters)
        answer = response.json()

        if len(answer['geocodes']) == 0:#看是不是由于city不对导致的
            city = ''
            parameters = {'address': address, 'key': key, 'output': 'json', 'city': city}
            base = 'http://restapi.amap.com/v3/geocode/geo'
            response = requests.get(base, parameters)
            answer = response.json()

        try:
            location = answer['geocodes'][0]['location'].split(',')

            item['lng'] = float(location[0])
            item['lat'] = float(location[1])
            item['formatted_address'] = answer['geocodes'][0]['formatted_address']
        except (KeyError, IndexError) as e:
            #e.g. 地址写的“自提”
            item['failure'] = True
            print(e)
            print(answer)
            print(item)


def main1(filename):
   
    depot = {}
    depot['address'] = '北京市通州区光机电一体化产业基地 兴光2街2号'
    depot['city'] = '北京'
    depot['lng'] = 116.567710
    depot['lat'] = 39.825670
    depot['formatted_address'] = "北京市通州区兴光2街|2号"

    A_data = readAITS(filename)

    for k in A_data.keys():
        geocode(A_data[k])

    with open('tempA.txt', 'wb') as f:
        pickle.dump(depot, f, True)
        pickle.dump(A_data, f, True)

def main2():
    with open('tempA.txt', 'rb') as f:
        depot = pickle.load(f)
        A_data = pickle.load(f)

    print(depot)

    for k in A_data.keys():
        print(k, len(A_data[k]))
        for item in A_data[k]:
            if 'failure' in item.keys():
                print(item)
    print(k, A_data[k][0])

if __name__ == '__main__':
    #main1()
    main2()


    print('AITS done')
