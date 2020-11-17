import re
import pandas as pd
import os
import datetime
import csv

def deal_dumpSFalwarys(path):
    dir_name = os.listdir(path)
    print(dir_name)
    for n in range(len(dir_name)):
        sub_path=os.path.join(path,dir_name[n])
        print(sub_path)
        if os.path.isdir(sub_path):
            sub_fname = os.listdir(sub_path)
            print(sub_fname)
            if 'analysis' not in sub_fname:
                os.makedirs(sub_path+'/analysis')
            if 'log' in sub_fname:
                try:
            #确认log文件存在，进行关键内容的提取。
                    if 'dumpSFalwarys.log' in os.listdir(sub_path+'/log'):
                        print('exist')
                        #将文本内容按行保存在dict['content']中
                        with open(sub_path+'/log'+'/dumpSFalwarys.log',encoding='utf-8') as f:
                            vlist = []
                            dict = {'content':vlist}
                            for num,value in enumerate(f):
                                vlist.append(value.strip())         
                        f.close()

                        #时间time所在行号存在num[]中
                        num =[]
                        for i in range(len(dict['content'])):
                            if dict['content'][i].endswith('CST 2020'):
                                num.append(i)
                        num.append(len(dict['content']))

                        #以time所在行号作为循环读取关键内容的标识符，若存在所需字段则将其添加至line列表。
                        total_list = []
                        for k in range(1,len(num)):
                            line = []
                            layers = []
                            blist = []
                            for j in range(num[k-1],num[k]):
                                if dict['content'][j].endswith('CST 2020'):
                                    time = '2020-' + dir_name[n] + ' ' + dict['content'][j].split(" ")[-3]
                                    line.append(time)              
                                if dict['content'][j].startswith('Total allocated'):
                                    total_allocated = dict['content'][j].split(":")[-1].strip().split(" ")[0]
                                    line.append(total_allocated)
                                if dict['content'][j] == "Display 1 HWC layers:":
                                    layers.append(j)
                                if dict['content'][j] == "Display 0 HWC layers:":
                                    layers.append(j)
                                if dict['content'][j].startswith('h/w'):
                                    layers.append(j) 
                                if dict['content'][j] == "Allocated buffers:":
                                    blist.append(j)
                                if dict['content'][j].startswith('Total allocated'):
                                    blist.append(j)
                            #计算主屏display1和虚屏display0的层数
                            if len(layers) != 0:
                                    display1_layers = int(((layers[1]-layers[0])-6)/3)
                                    display0_layers = int(((layers[2]-layers[1])-6)/3)
                                    line.append(display1_layers)
                                    line.append(display0_layers)
                            #计算buffers
                            if len(blist) == 2:
                                buffers = int((blist[1]-blist[0])-1)
                                line.append(buffers)
                            total_list.append(line)
                        
                        #从total_list列表中删除字段信息不完整的数据
                        del_number = []   
                        for m in range(len(total_list)):
                            if len(total_list[m]) != 5:  
                                del_number.append(m)
                        for num in list(reversed(del_number)):
                            total_list.pop(num)
                        print(total_list)

                        #按行将每个具有完整字段信息的时间点以及所提取的关键内容写到指定位置的csv文件中
                        with open(sub_path+'/analysis/dumpSFalwarys.csv','w',newline='') as f_csv:
                            csv_writer = csv.writer(f_csv,dialect='excel')
                            csv_writer.writerow(['time','total_allocated(KB)','display_1_layer','display_0_layer','buffers'])
                            for info in total_list:
                                csv_writer.writerow(info)
                        f_csv.close()
                except:
                    continue


def deal_meminfo(path):
    dir_name = os.listdir(path)
    print(dir_name)
    for n in range(len(dir_name)):
        sub_path=os.path.join(path,dir_name[n])
        print(sub_path)
        if os.path.isdir(sub_path):
            sub_fname = os.listdir(sub_path)
            print(sub_fname)
            if 'log' in sub_fname:
                try:
            #确认log文件存在，进行关键内容的提取
                    if 'meminfo.log' in os.listdir(sub_path+'/log'):
                        print('exist')
                        with open(sub_path+'/log'+'/meminfo.log',encoding='utf-8') as f:
                            vlist = []
                            dict = {'content':vlist}
                            for num,value in enumerate(f):
                                vlist.append(value.strip())         
                        f.close()
                        # print(dict)

                        num =[]
                        for i in range(len(dict['content'])):
                            if dict['content'][i].endswith('GMT 2020'):
                                num.append(i)
                        num.append(len(dict['content']))
                        # print(num)

                        total_list = []
                        for k in range(1,len(num)):
                            line = []
                            for j in range(num[k-1],num[k]):
                                if dict['content'][j].endswith('GMT 2020'):
                                    time = '2020-' + dir_name[n] + ' ' +dict['content'][j].split(" ")[-3]
                                    line.append(time) 
                                if dict['content'][j].endswith('/ram/highmem.0 contig len'):
                                    contig_len = dict['content'][j].split("MB")[0].strip()
                                    line.append(float(contig_len))
                                if dict['content'][j].endswith('/ram/highmem.0 non-contig len'):
                                    non_contig_len = dict['content'][j].split("MB")[0].strip()
                                    line.append(float(non_contig_len))
                            total_list.append(line)

                        del_number = []   
                        for m in range(len(total_list)):
                            if len(total_list[m]) != 3 or total_list[m][1] > 1400 or total_list[m][2] > 1400:
                                print(total_list[m])  
                                del_number.append(m)

                        for num in list(reversed(del_number)):
                            total_list.pop(num)
                        print(len(total_list))
                        with open(sub_path+'/analysis/meminfo.csv','w',newline='') as f_csv:
                            csv_writer = csv.writer(f_csv,dialect='excel')
                            csv_writer.writerow(['time','contig_len(MB)','non_contig_len(MB)'])
                            for info in total_list:
                                csv_writer.writerow(info)
                        f_csv.close()
                except:
                    continue


def deal_ionmemalways(path):
    dir_name = os.listdir(path)
    print(dir_name)
    for n in range(len(dir_name)):
        sub_path=os.path.join(path,dir_name[n])
        print(sub_path)
        if os.path.isdir(sub_path):
            sub_fname = os.listdir(sub_path)
            print(sub_fname)
            if 'log' in sub_fname:
                try:
            #2.确认log文件存在，进行关键内容的提取
                    if 'ionmemalways.log' in os.listdir(sub_path+'/log'):
                        print('exist')
                        with open(sub_path+'/log'+'/ionmemalways.log',encoding='utf-8') as f:
                            vlist = []
                            dict = {'content':vlist}
                            for num,value in enumerate(f):
                                vlist.append(value.strip())         
                        f.close()
                        # print(dict)

                        num =[]
                        for i in range(len(dict['content'])):
                            if dict['content'][i].endswith('CST 2020'):
                                num.append(i)
                        num.append(len(dict['content']))

                        total_list = []
                        for k in range(1,len(num)):
                            line = []
                            slist = []
                            for j in range(num[k-1],num[k]):

                                if dict['content'][j].endswith('CST 2020'):
                                    time = '2020-' + dir_name[n] + ' '+ dict['content'][j].split(" ")[-3]   
                                    line.append(time) 

                                if dict['content'][j].startswith('total         '):
                                    total_size = int(dict['content'][j].split(" ")[-1])
                                    line.append(total_size)
                                if dict['content'][j].startswith('surfaceflinger'):
                                    surfaceflinger_size = int(dict['content'][j].split(" ")[-1])
                                    slist.append(surfaceflinger_size)
                            if len(slist) != 0:
                                line.append(slist[0])
                            total_list.append(line)
                        print(total_list)

                        del_number = []   
                        for m in range(len(total_list)):
                            if len(total_list[m]) != 3:  
                                del_number.append(m)

                        for num in list(reversed(del_number)):
                            total_list.pop(num)
                        print(total_list)
                        with open(sub_path+'/analysis/ionmemalways.csv','w',newline='') as f_csv:
                            csv_writer = csv.writer(f_csv,dialect='excel')
                            csv_writer.writerow(['time','total_size(Byte)','surfaceflinger_size(Byte)'])
                            for info in total_list:
                                csv_writer.writerow(info)
                        f_csv.close()

                except:
                    continue

             
if __name__ == "__main__":
    deal_dumpSFalwarys('./')
    deal_meminfo('./')
    deal_ionmemalways('./')
