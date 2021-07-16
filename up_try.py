
current_frame = 0
bitrate_frame_size = {}
frame_encoded_time = []
last_bitrate = 3
source_side_time = -2.00
cooked_time = []
cooked_bw = []
bw_all = 0
with open('./dataset/new_network_trace/' + 'middle' + '/' + '0') as f:
    for line in f:
        parse = line.split()
        cooked_time.append(float(parse[0]))
        cooked_bw.append(float(parse[1]))
        bw_all += cooked_bw[-1]
print(bw_all/(len(cooked_bw)))


















