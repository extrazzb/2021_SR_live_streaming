import numpy as np
import random
import datetime
import fixed_env as fixed_env
import load_trace as load_trace
import time as tm
import os

MILLISECONDS_IN_SECOND = 1000.0
B_IN_MB = 1024.0*1024.0
BITS_IN_BYTE = 8.0

def upload(user_id):
    NETWORK_TRACE = 'high'
    VIDEO_TRACE = 'AsianCup_China_Uzbekistan'
    network_trace_dir = './dataset/network_trace/' + NETWORK_TRACE + '/'
    video_trace_prefix = './dataset/video_trace/' + VIDEO_TRACE + '/frame_trace_'

    # load the trace
    #all_cooked_time, all_cooked_bw, all_file_names = load_trace.load_trace(network_trace_dir)
    cooked_time = []
    cooked_bw = []
    with open('./dataset/network_trace/' + NETWORK_TRACE + '/'+'0') as f:
        for line in f:
            parse = line.split()
            cooked_time.append(float(parse[0]))
            cooked_bw.append(float(parse[1]))
    random_seed = 2
    count = 0
    trace_count = 1
    FPS = 25
    frame_time_len = 0.04
    reward_all_sum = 0
    run_time = 0
    cdn_arrive_time = []
    
    #store the frame size data
    video_frame_size = {}
    frame_encoded_time = []
    frame_encoded_trace = []
    timestep = -2.00
    video_trace_1 = './dataset/video_trace/sports/frame_trace_'
    for i in range(4):
        #print('test point1: '+str(i))
        video_frame_size[i] = []
        with open(video_trace_1+str(i)) as f:
            for line in f:
                if i == 0:
                    frame_encoded_time.append(timestep)
                    frame_encoded_trace.append(float(line.split()[0]))
                    timestep+=0.04
                video_frame_size[i].append(float(line.split()[1]))
    #now calculate the total size for the same frame.
    video_frame_size[4] = []
    for frame in range(len(frame_encoded_time)):
        sum_of_size = 0.0
        for bitrate in range(4):
            sum_of_size += video_frame_size[bitrate][frame]
        video_frame_size[4].append(sum_of_size)
        #print("chunks size, start upload time, arrive_time", video_frame_size[4][frame], frame_encoded_time[frame], frame)
    #calculate the arrive time
    duration = 0
    time = 0.0
    cnt_huge_latency = 0
    add = 0.53575
    
    differ = 0
    cnt = 0
    for frame in range(len(frame_encoded_time)):
        if int(time / 0.5) >= len(cooked_bw):
            break
        #if the frame has been encoded
        if time>=frame_encoded_time[frame]:
            throughput = (cooked_bw[int(time / 0.5)]+add)* B_IN_MB
            duration = float(video_frame_size[4][frame] / throughput)
            time+=duration
            cdn_arrive_time.append(time)
        else:
            duration = frame_encoded_time[frame] - time #wait
            time+=duration
            throughput = (cooked_bw[int(time / 0.5)]+add) * B_IN_MB
            duration = float(video_frame_size[4][frame] / throughput)
            time+=duration
            cdn_arrive_time.append(time)
        if (frame_encoded_time[frame]-cdn_arrive_time[frame])<=-0.1:
            cnt_huge_latency +=1
            '''print("chunks size, start upload time, arrive_time", video_frame_size[4][frame],throughput, frame_encoded_time[frame],
              frame_encoded_time[frame]-cdn_arrive_time[frame], duration)'''
        print("simulate_arrive_time, timestep_in_set, real_time, differ, frame", cdn_arrive_time[frame], frame_encoded_trace[frame],
              frame_encoded_time[frame], cdn_arrive_time[frame]-frame_encoded_trace[frame],frame)
        differ+=(cdn_arrive_time[frame]-frame_encoded_trace[frame])
        cnt+=1
    return [cnt_huge_latency, cnt_huge_latency*0.04, differ/cnt]
        
a = upload('aaa')
print(a)
                
        
    


















    
