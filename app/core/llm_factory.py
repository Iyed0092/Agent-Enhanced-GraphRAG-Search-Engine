import os
from openai import OpenAI
from llama_cpp import Llama
from app.core import settings

# Global vars to hold the model in memory
current_path = None
loaded_model = None

def get_groq_client():
    # connecting to groq api
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=settings.GROQ_API_KEY)

def get_lm_studio_client():
    return OpenAI(base_url=settings.LOCAL_SERVER_URL, api_key="lm-studio")

def load_file_model(target_path):
    global current_path, loaded_model
    
    # if the model is already loaded, we just return it
    if current_path == target_path and loaded_model:
        return loaded_model
    
    print("Loading Local GGUF: " + os.path.basename(target_path) + "...")
    
    # clear memory if needed
    if loaded_model:
        del loaded_model
        loaded_model = None
        
    loaded_model = Llama(
        model_path=target_path,
        n_gpu_layers=-1,
        n_ctx=2048,
        verbose=False
    )
    current_path = target_path
    return loaded_model


def ask_llm(role, prompt, system="You are a helpful assistant"):
    
    # check for online models first
    if role == "coder" or role == "writer":
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model=settings.MODEL_WRITER,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Groq Error: " + str(e))
            return None

    # check for chunking task
    if role == "chunking" and settings.MODEL_CHUNKING_PATH is None:
        client = get_lm_studio_client()
        res = client.chat.completions.create(
            model="local-model", 
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return res.choices[0].message.content

    # otherwise use local gguf files
    path_to_use = settings.MODEL_ROUTER_PATH
    if role == "reranker":
        path_to_use = settings.MODEL_RERANKER_PATH
    
    my_llm = load_file_model(path_to_use)
    if not my_llm: 
        return "Error loading local file."
    
    # manual template formatting
    full_prompt = f"<|system|>\n{system}\n<|user|>\n{prompt}\n<|assistant|>\n"
    
    output = my_llm(full_prompt, max_tokens=1024, stop=["<|user|>"], temperature=0.1, echo=False)
    return output["choices"][0]["text"].strip()