'''
Created on Aug 8, 2017
'''

import xlwt
import pickle

def writeVReturn(filename, header, data):
    #输入为文件名、表头和数据
    #将结果写回excel

    w = xlwt.Workbook(encoding= 'utf-8', style_compression = 0)
    ws = w.add_sheet('download')


    #设置一个背景色为红色的style
    style = xlwt.XFStyle()
    pattern = xlwt.Pattern()                 # 创建一个模式
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN     # 设置其模式为实型
    pattern.pattern_fore_colour = 2
    # 设置单元格背景颜色 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta,  the list goes on...
    style.pattern = pattern

    j = 0
    for item in header:
        ws.write(0, j, item)
        j += 1

    i = 1
    for row in data:
        j = 0
        for item in row:
            if j == 14 and item != '':
                ws.write(i, j, item, style)
                #如果被推荐，则调用之前的style，将背景设为红色
            else:
                ws.write(i, j, item)
            j += 1
        i += 1

    w.save(filename)
    print('done')

def main():
    #读取调整的结果和原始数据
    #整合，写入excel提供给调度

    with open('output.txt', 'rb') as f:
        result = pickle.load(f)

    with open('tempV.txt', 'rb') as f:
        V_header = pickle.load(f)
        V_data = pickle.load(f)
        V_data_dict = pickle.load(f)

    for VR in result:
        if 'recommend' in VR.keys():
            V_data[VR['index']][14] = VR['recommend']

    filename = r'output.xls'
    writeVReturn(filename, V_header, V_data)

    print('done')

if __name__ == '__main__':
    main()
