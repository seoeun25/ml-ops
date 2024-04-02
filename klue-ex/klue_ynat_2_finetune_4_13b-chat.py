#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import os
import pandas as pd
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
    prepare_model_for_int8_training,
    prepare_model_for_kbit_training,
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


import wandb


wandb.login(key='6be8bbf61c4a171c85e3d5cbad51ce3c96c880eb', relogin=True)


# In[2]:


idx = 3

chunk_size = 2048
# chunk_size = 4096


# In[3]:


model_ids = ["/home/jovyan/models/base/Llama-2-7b-hf-16bit",
             "/home/jovyan/models/base/Llama-2-7b-chat-hf-16bit",
             "/home/jovyan/models/base/Llama-2-13b-hf-16bit",
             "/home/jovyan/models/base/Llama-2-13b-chat-hf-16bit"]

model_id = model_ids[idx]


# In[4]:


output_dirs = ["/home/jovyan/models/peft/comefeel/klue_ynat_7b",
               "/home/jovyan/models/peft/comefeel/klue_ynat_7b-chat",
               "/home/jovyan/models/peft/comefeel/klue_ynat_13b",
               "/home/jovyan/models/peft/comefeel/klue_ynat_13b-chat"]

output_dir = output_dirs[idx]


# In[5]:


data_path = "/home/jovyan/datasets/klue_ynat"


# ### Step 1: Load the model and tokenizer

# In[6]:


tokenizer = LlamaTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

model = LlamaForCausalLM.from_pretrained(model_id, load_in_8bit=True, device_map='auto', torch_dtype=torch.float16)


# In[7]:


tokenizer


# ### Step 2: Data Preprocessing

# In[8]:


dataset = load_from_disk(data_path)
dataset


# In[9]:


train_dataset = dataset["train"].train_test_split(train_size=0.01, seed=24)["train"]
test_dataset = dataset["validation"]


# In[10]:


tokeinzed_train_dataset = train_dataset.remove_columns(
    [x for x in train_dataset.column_names if x not in ["input_ids", "attention_mask", "labels"]])
tokeinzed_train_dataset


# In[11]:


buffer = {
    "input_ids": [],
    "attention_mask": [],
    "labels": [],
    }

samples = []

for sample in tqdm(tokeinzed_train_dataset, desc="Concat", unit=' examples'):
    buffer = {k: v + sample[k] for k,v in buffer.items()}
    
    while len(next(iter(buffer.values()))) > chunk_size:
        samples.append({k: v[:chunk_size] for k,v in buffer.items()})
        buffer = {k: v[chunk_size:] for k,v in buffer.items()}

concat_train_dataset = Dataset.from_list(samples)


# In[12]:


tokeinzed_train_dataset


# In[13]:


concat_train_dataset


# In[14]:


print(tokenizer.decode(tokeinzed_train_dataset[0]["input_ids"]))


# In[15]:


print(tokenizer.decode(concat_train_dataset[0]["input_ids"]))


# ### Step 3: Prepare model for PEFT

# In[16]:


model.train()

def create_peft_config(model):

    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules = ["q_proj", "v_proj"]
    )

    # prepare int-8 model for training
    model = prepare_model_for_int8_training(model)
    # model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    return model, peft_config

# create peft config
model, lora_config = create_peft_config(model)


# ### Step 4: Define an optional profiler

# In[17]:


from transformers import TrainerCallback
from contextlib import nullcontext
enable_profiler = False


config = {
    'lora_config': lora_config,
    'learning_rate': 1e-4,
    # 'num_train_epochs': 1,
    'num_train_epochs': 3,
    'gradient_accumulation_steps': 1,
    # 'per_device_train_batch_size': 2,
    'per_device_train_batch_size': 1,
    'gradient_checkpointing': False,
}

# Set up profiler
if enable_profiler:
    wait, warmup, active, repeat = 1, 1, 2, 1
    total_steps = (wait + warmup + active) * (1 + repeat)
    schedule =  torch.profiler.schedule(wait=wait, warmup=warmup, active=active, repeat=repeat)
    profiler = torch.profiler.profile(
        schedule=schedule,
        on_trace_ready=torch.profiler.tensorboard_trace_handler(f"{output_dir}/logs/tensorboard"),
        record_shapes=True,
        profile_memory=True,
        with_stack=True)
    
    class ProfilerCallback(TrainerCallback):
        def __init__(self, profiler):
            self.profiler = profiler
            
        def on_step_end(self, *args, **kwargs):
            self.profiler.step()

    profiler_callback = ProfilerCallback(profiler)
else:
    profiler = nullcontext()


# ### Step 5: Fine tune the model

# In[18]:


torch.cuda.empty_cache()


# In[19]:


# Define training args
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    bf16=True,  # Use BF16 if available
    # logging strategies
    logging_dir=f"{output_dir}/logs",
    logging_strategy="steps",
    logging_steps=10,
    save_strategy="epoch",
    # save_strategy="steps",
    # save_steps=50,
    optim="adamw_torch_fused",
    max_steps=total_steps if enable_profiler else -1,
    **{k:v for k,v in config.items() if k != 'lora_config'}
)

model.config.use_cache = False

with profiler:
    # Create Trainer instance
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=concat_train_dataset,
        data_collator=default_data_collator,
        
    )

    # Start training
    trainer.train()


# ### Step 6: Save the model

# In[20]:


model.save_pretrained(output_dir)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




