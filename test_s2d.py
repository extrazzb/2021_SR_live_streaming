import source2cdn as s2d
import matplotlib.pyplot as plt
import numpy as np

def test(user_id):
    video_source ="sports"
    video_trace = s2d.Trace(video_source=video_source)
    cdn_arrive_time = []
    s2d.Trace.upload_next_50_frame(video_trace, 3, cdn_arrive_time)
    s2d.Trace.upload_next_50_frame(video_trace, 3, cdn_arrive_time)
    with open('./dataset/network_trace/')

    return cdn_arrive_time

a = test('aaa')


print(a)