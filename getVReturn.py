'''
Created on Aug 3, 2017
'''

import xlrd
import xlwt
import pickle
import requests
import settings

def readVReturn(filename):
    #输入为文件名
    #返回excel中表头和所有数据的二维列表

    workbook = xlrd.open_workbook(filename)
    table = workbook.sheets()[0]

    header = []

    for j in range(table.ncols):
        header.append(table.cell(0,j).value)

    data = []
    for i in range(1, table.nrows):
        temp = []
        for j in range(table.ncols):
            temp.append(table.cell(i,j).value)

        data.append(temp)

    return header, data

def writeVReturn(filename, header, data):
    #输入文件名、表头、数据
    #将结果写回excel

    w = xlwt.Workbook(encoding= 'utf-8', style_compression = 0)
    ws = w.add_sheet('download')

    j = 0
    for item in header:
        ws.write(0, j, item)
        j += 1

    i = 1
    for row in data:
        j = 0
        for item in row:
            ws.write(i, j, item)
            j += 1
        i += 1

    w.save(filename)
    print('done')

def VReturn2Dict(header, data):
    #输入表头和VR数据
    #输出为点的list，每个点以dict形式存储

    result = []
    #可以用header做一些更变通的处理
    #现在只加入：index, vendor_code, city, address, carton, units, weight, cube, c_date
    header
    for i in range(len(data)):
        if True:
            #看是否需要筛选
            temp = {}
            temp['index'] = i
            temp['vendor_code'] = data[i][5]
            temp['city'] = data[i][7]
            temp['address'] = data[i][8]

            if temp['address'][0:2] == '河北' and temp['city'][0:2] == '北京':
                temp['city'] = ''

            temp['carton'] = data[i][9]
            temp['units'] = data[i][10]
            temp['weight'] = data[i][11]
            temp['cube'] = data[i][12]
            temp['c_data'] = data[i][2]#不知道有没有用

            result.append(temp)

    return result

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
    #读取数据，获取经纬度，写入tempV.txt
    V_header, V_data = readVReturn(filename)
    V_data_dict = VReturn2Dict(V_header, V_data)

    geocode(V_data_dict)

    with open('tempV.txt', 'wb') as f:
        pickle.dump(V_header, f, True)
        pickle.dump(V_data, f, True)
        pickle.dump(V_data_dict, f, True)

def main2():
    with open('tempV.txt', 'rb') as f:
        V_header = pickle.load(f)
        V_data = pickle.load(f)
        V_data_dict = pickle.load(f)

    print(V_header)
    print(V_data[0])
    print(V_data_dict[0])
    for item in V_data_dict:
        if 'failure' in item.keys():
            print(item)

if __name__ == '__main__':
    #main1()
    main2()

    #用于输出推荐结果
    '''
    filename = r'output.xls'
    writeVReturn(filename, V_header, V_data)
    '''

    print('VReturn done')
