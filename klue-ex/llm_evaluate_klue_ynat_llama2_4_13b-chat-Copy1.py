#!/usr/bin/env python
# coding: utf-8

# In[1]:


# get_ipython().system('pip install openpyxl -q')
# # !pip install vllm==0.3.2 -q
# get_ipython().system('pip install vllm -q')
# get_ipython().system('pip uninstall -y pynvml -q')

import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "vllm"])
subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "pynvml"])

# In[2]:


import numpy as np
import openpyxl
import os
import pandas as pd
import time
import torch
from tqdm import tqdm

from contextlib import nullcontext
from datasets import load_dataset, load_from_disk, Dataset

from peft import (
    get_peft_config, 
    PeftModel, 
    PeftConfig, 
    get_peft_model, 
    LoraConfig, 
    TaskType
)
from torch.utils.data import DataLoader
from transformers import (
    LlamaForCausalLM,
    LlamaTokenizer,
    TrainingArguments,
    Trainer,
    default_data_collator,
    DataCollatorForLanguageModeling,
    DataCollatorWithPadding
)

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest


# In[3]:


idx = 3


# In[4]:


# base 모델 경로 입력

model_ids = ["/home/jovyan/models/base/Llama-2-7b-hf-16bit",
             "/home/jovyan/models/base/Llama-2-7b-chat-hf-16bit",
             "/home/jovyan/models/base/Llama-2-13b-hf-16bit",
             "/home/jovyan/models/base/Llama-2-13b-chat-hf-16bit"]

model_id = model_ids[idx]

merged_model_ids = ["/home/jovyan/models/merged/comefeel/klue_ynat_7b",
               "/home/jovyan/models/merged/comefeel/klue_ynat_7b-chat",
               "/home/jovyan/models/merged/comefeel/klue_ynat_13b",
               "/home/jovyan/models/merged/comefeel/klue_ynat_13b-chat"]

model_id = merged_model_ids[idx]


# In[5]:


# peft adapter 모델 경로 입력

peft_model_ids = ["/home/jovyan/models/peft/comefeel/klue_ynat_7b",
               "/home/jovyan/models/peft/comefeel/klue_ynat_7b-chat",
               "/home/jovyan/models/peft/comefeel/klue_ynat_13b",
               "/home/jovyan/models/peft/comefeel/klue_ynat_13b-chat"]

peft_model_id = peft_model_ids[idx]


# In[6]:


# 평가 data 경로 입력

data_path = "/home/jovyan/datasets/klue_ynat"


# In[7]:


eval_file_paths = ["/home/jovyan/evaluation/comefeel/klue_ynat_1_7b.xlsx",
                   "/home/jovyan/evaluation/comefeel/klue_ynat_2_7b-chat.xlsx",
                   "/home/jovyan/evaluation/comefeel/klue_ynat_3_13b.xlsx",
                   "/home/jovyan/evaluation/comefeel/klue_ynat_4_13b-chat.xlsx"]

eval_file_path = eval_file_paths[idx]


# # Step 1: Load the model, tokenizer

# In[8]:


tokenizer = LlamaTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token


# In[9]:


# llm = LLM(model=model_id, enable_lora=True,  tensor_parallel_size=2)
llm = LLM(model=model_id, tensor_parallel_size=2)


# In[10]:


sampling_params = SamplingParams(
    temperature=0.6,
    max_tokens=500,
    top_p=0.3
    
)


# In[11]:


lora_request = LoRARequest("llama2_klue_7b", 1, peft_model_id)


# # Step 2: Load test dataset

# In[12]:


dataset = load_from_disk(data_path)
dataset


# In[13]:


train_dataset = dataset["train"]
test_dataset = dataset["validation"]


# In[14]:


test_dataset.features


# In[15]:


test_dataset


# In[16]:


print(test_dataset[0]["prompt"], "\n\n")
print(test_dataset[0]["response"], "\n\n")


# # Step 3: Generate output w/ lora adapters

# In[17]:


# outputs = llm.generate(
#     test_dataset["prompt"], 
#     sampling_params,
#     lora_request=lora_request
# )

outputs = llm.generate(test_dataset["prompt"], sampling_params)



# In[18]:


outputs[0]


# # Step 4: Compute metric & Write output

# In[19]:


list_result = []

for i in range(len(test_dataset)):
    # print(i)
    
    context = test_dataset[i]["title"]
    generated = tokenizer.decode(outputs[i].outputs[0].token_ids, skip_special_tokens=True)
    true = tokenizer.decode(tokenizer(test_dataset[i]["response"], return_tensors="pt", 
                                      add_special_tokens=False).input_ids[0], skip_special_tokens=True)
    
    metric = (generated == true) * 1

    # print(context)
    # print(generated)
    # print(true)
    # print(metric)
    
    result = {
        "context": context,
        "true_response": true, 
        "gen_response": generated,
        "metric": metric
    }
    
    list_result.append(result)


# In[20]:


df_metric = pd.DataFrame(list_result)


# In[21]:


df_metric.head()


# In[22]:


round(df_metric["metric"].mean(), 3)


# In[ ]:





# In[24]:


df_metric.to_excel(excel_writer=eval_file_path)


# In[ ]:





