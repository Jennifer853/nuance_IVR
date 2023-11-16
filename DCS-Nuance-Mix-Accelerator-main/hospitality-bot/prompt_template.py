# -*- coding: utf-8 -*-
import openai
import requests
openai.api_type = ""
openai.api_base = ""
openai.api_version = ""
openai.api_key = ""
bing_endpoint = ""
bing_key = ""
def form_chatbot_prompt(prompts, responses):
    messages = [
    {"role":"system","content":"I want you to act as a hotelling assistant, before you give your response, you must make sure your response follows these rules: 1. you don't have any information about our hotel's facilities and policies, so do not give any answers about them. 2. You should only answer the question without saying anything else. 3. Do not answer questions if you are not sure"},
    # {"role":"system","content":"I want you to act as a hotelling assistant"},
    ]
    for i in range(1, len(responses)):
        messages.append({"role":"assistant", "content": responses[i]})
        if prompts[i] != '_':
            messages.append({"role":"user", "content": prompts[i]})
    return messages

def summarize_keywords(prompts, responses):
    # task = "You need to read the following conversation, and generate keywords for AI to use search engines. Our hotel locates at London Brixton. \n"
    task = "You need to generate a search enging query based on the following conversation and focus on the customer's latest question. Our hotel locates at Myrtle Beach, SC. \n"

    for i in range(1, len(responses)):
        row = "Assistant: {}\n".format(responses[i])
        task += row
        if prompts[i] != '_':
            row = "Customer: {}\n".format(prompts[i])
            task += row
    response = openai.Completion.create(
                engine="davinci003",
                prompt=task,
                temperature=0,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)
    return response["choices"][0]["text"]

def bing_links(query):
    mkt = "en-US"
    params = {'q':query, 'mkt':mkt}
    headers = { 'Ocp-Apim-Subscription-Key': bing_key }
    endpoint = bing_endpoint + "/v7.0/search"
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    json = response.json()

    return [(r['name'], r['url']) for r in json['webPages']['value']][:1]

def form_chatbot_prompt_v2(prompts, responses, links):
    # txt_links = "\n".join(["Title: {}\nURL: {}\n".format(link[0], link[1]) for link in links])
    txt_links = "\n".join(["URL: {}\n".format(link[1]) for link in links])

    messages = [
    {"role":"system","content":'''You are a hotelling assistant. Use the following sources to answer the question
                                    {},
                                    Before you give your response, you must make sure your response follows these rules: 
                                    1. Do not include any website links or references
                                    2. Summarize your answer within 40 words
                                    3. Ensure your final answer makes sense
                                   '''.format(txt_links)}
                                    # 1. If user asks for our hotel's discounts, tell them to visit our website.
                                    # 2. You don't include any websites in your answer
    # {"role":"system","content":"I want you to act as a hotelling assistant"},
    ]
    for i in range(1, len(responses)):
        messages.append({"role":"assistant", "content": responses[i]})
        if prompts[i] != '_':
            messages.append({"role":"user", "content": prompts[i]})
    return messages