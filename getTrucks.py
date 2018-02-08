'''
Created on Aug 3, 2017
'''

import pickle

def main1():
    #读取truck的csv数据，以dict形式存储

    with open(r'TRUCK.csv', encoding = 'utf-8') as f:
        data = f.readlines()

    result = {}
    for item in data[1:]:
        item_list = item.replace('\n','').split(',')
        result[item_list[0]] = {}
        result[item_list[0]]['cube']        = float( item_list[1] )
        result[item_list[0]]['weight']      = float( item_list[2] )
        result[item_list[0]]['truckType']   = item_list[-1]

    with open('tempT.txt', 'wb') as f:
        pickle.dump(result, f, True)

def main2():
    with open('tempT.txt', 'rb') as f:
        trucks = pickle.load(f)

    print(trucks)

if __name__ == '__main__':
    #main1()
    main2()


    print('Trucks done')
