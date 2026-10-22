"""PCSX2 녹화 영상에서 초마다 실제로 바뀐 프레임 수(게임 렌더링 fps)를 센다: python tools/fps.py video.mp4"""
import sys, av, numpy as np
c = av.open(sys.argv[1]); prev = None; per = {}
for fr in c.decode(video=0):
    t = int(fr.time)
    img = fr.to_ndarray(format='gray')[::4, ::4].astype(np.int16)
    if prev is not None:
        per.setdefault(t, [0, 0]); per[t][1] += 1
        if np.abs(img - prev).mean() > 0.5: per[t][0] += 1
    prev = img
v = [per[t][0] for t in sorted(per) if per[t][1] > 40]
print('frames/s per second:', v)
print('mean %.1f  min %d  p10 %.1f' % (np.mean(v), min(v), np.percentile(v, 10)))
