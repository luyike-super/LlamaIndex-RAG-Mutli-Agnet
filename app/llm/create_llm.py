import os
from llama_index.llms.deepseek import DeepSeek
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.core import Settings
from app.core.config import settings

def llm_deepseek(model=None, temperature=0.1):

    """创建一个DeepSeek LLM客户端实例

    Args:
        model (str, optional): 使用的模型名称. 如不指定则使用环境变量中的配置.
        temperature (float, optional): 生成文本的随机性. Defaults to 0.1.

    Returns:
        DeepSeek: 初始化好的DeepSeek客户端实例
    """

    # 优先使用传入的model参数，其次使用settings中的配置
    model = model or settings.DEEPSEEK_MODEL
    return DeepSeek(
        model=model,
        api_key=settings.DEEPSEEK_API_KEY,
        api_base=settings.DEEPSEEK_API_BASE,
        temperature=temperature
    )

def llm_qwen(model="qwen-plus", temperature=0.5):
    """创建一个QWen LLM客户端实例

    Args:
        model (str, optional): 使用的模型名称. 默认使用 "qwen-plus" 模型.
        temperature (float, optional): 生成文本的随机性. 默认为 0.1.

    Returns:
        OpenAILike: 初始化好的 QWen LLM 客户端实例
    """

    return OpenAILike(
        model=model,
        api_base=settings.DASHSCOPE_API_BASE,
        api_key=settings.DASHSCOPE_API_KEY,
        temperature=temperature,
        is_chat_model=True
    )

def llm_qwen_embeding(model="text-embedding-v2"):
    embedder = DashScopeEmbedding(
        model_name=model,
        api_key=settings.DASHSCOPE_API_KEY
    )
    return embedder
    
def init_setting():
    Settings.llm = llm_qwen()
    Settings.embed_model = llm_qwen_embeding()


# 创建默认客户端实例
client_deepseek = llm_deepseek()
client_qwen = llm_qwen()

client_qwen_embeding = llm_qwen_embeding()

