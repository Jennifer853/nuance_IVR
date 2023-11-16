import time
import json
import requests_async as requests
import asyncio
import pickle
import numpy as np
async def worker_request(sleeptime):
    cur_text = "Can you recommend what should I bring for the travel"
    payload={"input_text": cur_text,
        "user_input_var": "####_####I want to book two rooms next Monday####{}####".format(cur_text),
        "bot_input_var": "####Thank you for calling Paradise resorts. This call may be recorded for quality purposes.#### Tell me, how can I help you?####Thanks for calling, we booked two rooms for you####"}
    url = "https://nuanceappintegration.azurewebsites.net/qna"
    # url = "http://localhost:8000/qna"
    await asyncio.sleep(sleeptime)

    request_start = time.time()

    resp = await requests.post(url, data=json.dumps(payload), headers={"Content-Type":"application/json"})
    request_gap = time.time() - request_start
    event_list.append([request_start, resp, request_gap])

async def main_concurrency(timespan, n, dist="uniform"):
    tasks = []
    if dist=="uniform":
        for i in range(n):
            tasks.append(worker_request(i*timespan/n))
    elif dist=="norm":
        indices = n_req_normal(n, timespan)
        print(indices)
        for i in range(len(indices)):
            tasks.append(worker_request(indices[i]))
    await asyncio.gather(*tasks)

def n_req_normal(n_req, timespan):
    s = np.sort(np.random.normal(0.5, 0.5, int(1e6)))
    mid, left, right = s[(s>=0) & (s<=1)], s[s<0], s[s>1]
    n_pad = (len(mid)//n_req +1)*n_req - len(mid)
    left_sample = n_pad//2
    right_sample = n_pad - left_sample
    s = np.hstack((left[-left_sample:], mid, right[:right_sample]))
    s = (s-s.min())/(s.max()-s.min()) * timespan
    s = s.reshape(n_req, len(s)//n_req).mean(axis=1)
    return s

if __name__ == "__main__":
    timespan = 60
    for n_calls in range(250, 550, 50):
        event_list = []
        start = time.time()
        asyncio.run(main_concurrency(timespan, n_calls, dist="norm"))
        with open("experiments/async_server_B1_normdist/nuanceappservice_{}_sec_{}_call.pickle".format(timespan, n_calls), 'wb') as f:
            pickle.dump(event_list, f)
        print(time.time()-start)
        time.sleep(60)