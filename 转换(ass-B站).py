# python
# -*- coding: utf-8 -*-
# 可以批量转换同文件夹下所有.lrc文件，命名为同名文件
# 去除了口袋ID，只保留弹幕内容

import sys
import re
import os
from pathlib import Path

# 写入ass文件头
info = """
[Script Info]
Title: 口袋直播弹幕（B站字幕用）
Original Script: 小丁
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 852
PlayResY: 480

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,霞鹜文楷,30,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,1,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

#遍历文件找到.lrc后缀
for parent,dirnames,filenames in os.walk("."):
    for filename in filenames:
        if ".lrc" in filename:
            input_file_name = filename
            output_file_name = filename.split('.')[0] + ".ass"

            file_item = Path(input_file_name)
            if not(file_item.exists() or file_item.is_file()) :
                sys.exit(-2)

            if input_file_name==output_file_name :
                output_file_name = input_file_name + ".ass"
        
            output_file = Path(output_file_name)
            if output_file.exists() :
                os.remove(output_file)

            print('{}{}'.format("input: ",input_file_name))
            print('{}{}'.format("output: ",output_file_name))

            ass = open(output_file_name,"w",encoding = "utf-8")
            ass.write(info)
            ass.close()

            # lrc转换ass
            lrc = open(input_file_name,"r",encoding = "utf-8")
            ass = open(output_file_name,"a",encoding = "utf-8")
        
            counter_r=0
            counter_w=0

            timeList = []
            commList = []

            # 写入一行字幕的文本
            def getOneLine(objIndex):
                oneLine=''
                # 开始时间
                startTime=timeList[objIndex]
                # 结束时间
                endTime=timeList[objIndex+1]
                # 说话内容
                comment =commList[objIndex]
                # 字符串
                oneLine += f'Dialogue: 0,{startTime},{endTime},Default,,0,0,0,,{comment}\n'
                return oneLine
                
            # 获取时间和内容
            for line in lrc:
                line = line.strip()
                print('{}{}'.format("R ",line))
                counter_r=counter_r+1

                if not( re.match("^\[[0-9:\.\s]+\].+",line)) :
                    continue
                    
                # 获取时间
                time_str = line.split(']')[0][1:]
                time_str = time_str.split(':')
                time = [0,0,0]
                if len(time_str)>2 :
                    time[0] = int(time_str[0])
                    time[1] = int(time_str[1])       
                    time[2] = float(time_str[2])
                elif len(time_str)==2 :
                    time[1] = int(time_str[0])
                    time[2] = float(time_str[1]) 
                time0 = '{}:{}:{}'.format(time[0],time[1],time[2])
                # 写入时间
                timeList.append(time0)

                # 获取弹幕内容
                comment = line.split(']',2)[1].strip()
                comment = re.sub(r'.*\s+', "", comment)
                # 写入评论
                commList.append(comment)

            #写入ass
            for objIndex in range(0,len(commList)-1):
                assStr=''
                assStr+=getOneLine(objIndex)
                ass.write(assStr)
                objIndex+=1
                counter_w=counter_w+1

            #写入最终结束时间
            LastStartTime = timeList[-1]
            time_str = LastStartTime.split(':')
            time = [0,0,0]
            if len(time_str)>2 :
                time[0] = int(time_str[0])
                time[1] = int(time_str[1])       
                time[2] = float(time_str[2])
            elif len(time_str)==2 :
                time[1] = int(time_str[0])
                time[2] = float(time_str[1]) 
            # 时间进位计算
            time[2] = (time[2])+1  

            if time[2] < 10:
                time[2] = '0' + str(time[2])
            elif time[2] >= 60:
                time[2] = round((time[2]-60),2)
                if time[2] < 10:
                    time[2] = '0' + str(time[2])
                else:
                    time[2] = str(time[2])
                time[1] = time[1] + 1
            if time[1] < 10:
                time[1] = '0' + str(time[1])
            elif time[1] >= 60:
                time[1] = time[1] - 60
                time[0] = time[0] + 1
                if time[1] < 10:
                    time[1] = '0' + str(time[1])
                else:
                    time[1] = str(time[1])
            # 获取结束时间
            LastEndTime = '{}:{}:{}'.format(time[0],time[1],time[2])

            # 写入最终行
            LastLine = ''
            LastLine = f'Dialogue: 0,{LastStartTime},{LastEndTime},Default,,0,0,0,,{commList[-1]}\n'
            ass.write(LastLine)
            counter_w=counter_w+1

            # 结束
            lrc.close()
            ass.close()

            print('\nFinish. W/R={}/{}'.format(counter_w,counter_r))
