from datetime import datetime
# from webbrowser import Chrome
from flask import Flask, request
from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# import langchain.embeddings as LlamaCppEmbeddings,CacheBackedEmbeddings
from langchain.memory import ConversationBufferWindowMemory
import datetime as dt


app = Flask(__name__)
# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


custom_prompt_template = """
You are an AI Coding Assitant and your task is to solve coding problems and return code snippets based on given user's query. Below is the user's query.
{history}
Query: {query}

You just return the helpful code.
Helpful Answer:
"""


def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=["history", 'query'])
    return prompt


n_gpu_layers = 1  # Metal set to 1 is enough.
# Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
n_batch = 512


llm = LlamaCpp(
    model_path="./code-ggml-model-q4_0.gguf",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    callback_manager=callback_manager,
    verbose=True,




)


llm_chain = LLMChain(prompt=set_custom_prompt(),
                     llm=llm,
                     memory=ConversationBufferWindowMemory(k=2),

                     )



@app.route("/api/prompt", methods=["POST"])
def prompt_route():
    #   now = datetime.datetime.now()
    now = dt.datetime.now()
    
    user_prompt = request.form.get("user_prompt")
    answer = llm_chain.predict(query=user_prompt)

    prompt_response_dict = {
        "prompt": user_prompt,
        "query": answer,
        "timestamp":now



    }

    return prompt_response_dict


if __name__ == "__main__":

    app.run(debug=False, port=8080)
