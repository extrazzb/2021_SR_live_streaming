''' Simulator for ACM Multimedia 2019 Live Video Streaming Challenge
    Author Dan Yang
    Time 2019-01-31
'''
# import the env
import fixed_env as fixed_env
import load_trace as load_trace
# import matplotlib.pyplot as plt
import time as tm
import ABR
import os
import numpy as np
import matplotlib.pyplot as plt


def test(user_id):
    # -- Configuration variables --
    # Edit these variables to configure the simulator

    # Change which set of network trace to use: 'fixed' 'low' 'medium' 'high'
    NETWORK_TRACE = 'fixed'

    # Change which set of video trace to use.
    VIDEO_TRACE = 'sports'

    # Turn on and off logging.  Set to 'True' to create log files.
    # Set to 'False' would speed up the simulator.
    DEBUG = False

    # Control the subdirectory where log files will be stored.
    LOG_FILE_PATH = './log/'

    # create result directory
    if not os.path.exists(LOG_FILE_PATH):
        os.makedirs(LOG_FILE_PATH)

    # -- End Configuration --
    # You shouldn't need to change the rest of the code here.

    network_trace_dir = './dataset/network_trace/' + NETWORK_TRACE + '/'
    video_trace_prefix = './dataset/video_trace/' + VIDEO_TRACE + '/frame_trace_'

    # load the trace
    all_cooked_time, all_cooked_bw, all_file_names = load_trace.load_trace(network_trace_dir)
    # random_seed
    random_seed = 2
    count = 0
    trace_count = 1
    FPS = 25
    frame_time_len = 0.04
    reward_all_sum = 0
    run_time = 0
    delay_counter = 0
    # init
    # setting one:
    #     1,all_cooked_time : timestamp
    #     2,all_cooked_bw   : throughput
    #     3,all_cooked_rtt  : rtt
    #     4,agent_id        : random_seed
    #     5,logfile_path    : logfile_path
    #     6,VIDEO_SIZE_FILE : Video Size File Path
    #     7,Debug Setting   : Debug
    net_env = fixed_env.Environment(all_cooked_time=all_cooked_time,
                                    all_cooked_bw=all_cooked_bw,
                                    random_seed=random_seed,
                                    logfile_path=LOG_FILE_PATH,
                                    VIDEO_SIZE_FILE=video_trace_prefix, VIDEO_TRACE=VIDEO_TRACE,
                                    Debug=DEBUG)

    abr = ABR.Algorithm()
    abr_init = abr.Initial()

    BIT_RATE = [500.0, 850.0, 1200.0, 1850.0]  # kpbs
    TARGET_BUFFER = [0.5, 1.0]  # seconds
    # ABR setting
    RESEVOIR = 0.5
    CUSHION = 2

    cnt = 0
    # defalut setting
    last_bit_rate = 0
    bit_rate = 0
    target_buffer = 0
    latency_limit = 4  # I know this is used to control the latency, but how?

    # QOE setting
    reward_frame = 0
    reward_all = 0
    SMOOTH_PENALTY = 0.02
    REBUF_PENALTY = 1.85
    LANTENCY_PENALTY = 0.005
    SKIP_PENALTY = 0.5
    # past_info setting (I can get that these lists is used to store the data of previous frames, but why we need so many frames?)
    past_frame_num = 7500
    S_time_interval = [0] * past_frame_num
    S_send_data_size = [0] * past_frame_num
    S_chunk_len = [0] * past_frame_num
    S_rebuf = [0] * past_frame_num
    S_buffer_size = [0] * past_frame_num
    S_end_delay = [0] * past_frame_num
    S_chunk_size = [0] * past_frame_num
    S_play_time_len = [0] * past_frame_num
    S_decision_flag = [0] * past_frame_num
    S_buffer_flag = [0] * past_frame_num
    S_cdn_flag = [0] * past_frame_num
    S_skip_time = [0] * past_frame_num
    S_arrive_time = [] # record the arrive time. For plot
    # params setting
    call_time_sum = 0

    get_frame_cnt = 0
    while True:
        get_frame_cnt += 1
        time, time_interval, send_data_size, chunk_len, \
        rebuf, buffer_size, play_time_len, end_delay, \
        cdn_newest_id, download_id, cdn_has_frame, skip_frame_time_len, decision_flag, \
        buffer_flag, cdn_flag, skip_flag, end_of_video, delay_counter = net_env.get_video_frame(bit_rate, target_buffer,
                                                                                                latency_limit)
        if not end_of_video:
            time2 = time
        # S_info is sequential order
        S_time_interval.pop(0)
        S_send_data_size.pop(0)
        S_chunk_len.pop(0)
        S_buffer_size.pop(0)
        S_rebuf.pop(0)
        S_end_delay.pop(0)
        S_play_time_len.pop(0)
        S_decision_flag.pop(0)
        S_buffer_flag.pop(0)
        S_cdn_flag.pop(0)
        S_skip_time.pop(0)

        S_time_interval.append(time_interval)
        S_send_data_size.append(send_data_size)
        S_chunk_len.append(chunk_len)
        S_buffer_size.append(buffer_size)
        S_rebuf.append(rebuf)
        S_end_delay.append(end_delay)
        S_play_time_len.append(play_time_len)
        S_decision_flag.append(decision_flag)
        S_buffer_flag.append(buffer_flag)
        S_cdn_flag.append(cdn_flag)
        S_skip_time.append(skip_frame_time_len)

        # QOE setting
        if end_delay <= 1.0:
            LANTENCY_PENALTY = 0.005
        else:
            LANTENCY_PENALTY = 0.01

        if not cdn_flag:
            reward_frame = frame_time_len * float(BIT_RATE[
                                                      bit_rate]) / 1000 - REBUF_PENALTY * rebuf - LANTENCY_PENALTY * end_delay - SKIP_PENALTY * skip_frame_time_len
        else:
            reward_frame = -(REBUF_PENALTY * rebuf)
        if decision_flag or end_of_video:
            # reward formate = play_time * BIT_RATE - 4.3 * rebuf - 1.2 * end_delay
            reward_frame += -1 * SMOOTH_PENALTY * (abs(BIT_RATE[bit_rate] - BIT_RATE[last_bit_rate]) / 1000)
            # last_bit_rate
            last_bit_rate = bit_rate

            # ----------------- Your Algorithm ---------------------
            cnt += 1
            timestamp_start = tm.time()
            bit_rate, target_buffer, latency_limit = abr.run(time,
                                                             S_time_interval,
                                                             S_send_data_size,
                                                             S_chunk_len,
                                                             S_rebuf,
                                                             S_buffer_size,
                                                             S_play_time_len,
                                                             S_end_delay,
                                                             S_decision_flag,
                                                             S_buffer_flag,
                                                             S_cdn_flag,
                                                             S_skip_time,
                                                             end_of_video,
                                                             cdn_newest_id,
                                                             download_id,
                                                             cdn_has_frame,
                                                             abr_init)
            timestamp_end = tm.time()
            call_time_sum += timestamp_end - timestamp_start  # here is the only position where "call_time_sum" increases
            # -------------------- End --------------------------------

        if end_of_video:
            print("network traceID, network_reward, avg_running_time, count", trace_count, reward_all,
                  call_time_sum / cnt, cnt, delay_counter, get_frame_cnt)
            reward_all_sum += reward_all
            run_time += call_time_sum / cnt
            if trace_count >= 1:
                break
            trace_count += 1







a = test("aaa")
print(a)