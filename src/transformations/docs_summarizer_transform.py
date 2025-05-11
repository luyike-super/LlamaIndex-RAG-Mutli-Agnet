import asyncio
import traceback

from llama_index.core.schema import TransformComponent
from llama_index.core.bridge.pydantic import Field
from llama_index.core.response_synthesizers import TreeSummarize
from src.models import LLMFactory, LLMProviderType

class DocsSummarizerTransform(TransformComponent):
  """对当前文档页面进行摘要。"""


  async def generate_summary(self, node, summarizer, prompt):
      print(f"===== 开始获取节点 {node.id_} 的摘要 =====")
      try:
          summary = await summarizer.aget_response(prompt, [node.text])
          print(f"节点 {node.id_} 摘要生成成功: {summary[:50]}...")
          # 确保metadata是字典类型
          if not isinstance(node.metadata, dict):
              node.metadata = {}
          node.metadata['summary'] = summary
      except Exception as e:
          print(f"节点 {node.id_} 摘要生成失败: {str(e)}")
          # 记录完整堆栈信息
          traceback.print_exc()
  
  async def process_nodes(self, nodes, summarizer, prompt):
    print(f"===== 开始处理 {len(nodes)} 个节点的摘要 =====")
    tasks = []
    for node in nodes:
      task = asyncio.create_task(
         self.generate_summary(node, summarizer, prompt)
      )
      tasks.append(task)
    print(f"创建了 {len(tasks)} 个异步任务")
    try:
        await asyncio.gather(*tasks)
        print("所有摘要任务已完成")
    except Exception as e:
        print(f"处理节点摘要时发生错误: {str(e)}")
        traceback.print_exc()
  
  
  def __call__(self, nodes, **kwargs):
    print('===== DocsSummarizerTransform.__call__ 开始执行 =====')
    print(f"接收到 {len(nodes)} 个节点进行处理")
    # 创建新的事件循环并在其中运行异步任务
    try:
      loop = asyncio.get_event_loop()
      print(f"获取到事件循环: {loop}")
      # 如果当前线程没有事件循环或事件循环已关闭
      if loop.is_closed():
        print("当前事件循环已关闭，创建新的事件循环")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
      # 在事件循环中运行异步方法
      print("准备执行异步摘要生成操作...")
      result = loop.run_until_complete(self.acall(nodes, **kwargs))
      print("异步摘要生成操作已完成")
      return result
    except Exception as e:
      print(f"===== 摘要生成过程中出错: {str(e)} =====")
      # 打印详细的堆栈跟踪
      traceback.print_exc()
      # 出错时也要返回节点，确保流程不中断
      return nodes
    finally:
      print('===== DocsSummarizerTransform.__call__ 执行完毕 =====')

  async def acall(self, nodes, **kwargs):
    print("===== DocsSummarizerTransform.acall 开始执行 =====")
    try:
      print("初始化 TreeSummarize...")
      summarizer = TreeSummarize(
        verbose=True,
        llm=LLMFactory.create_llm(LLMProviderType.QIANWENOPENAI,temperature=0.5,max_tokens=100)
      )
      print("TreeSummarize 初始化完成")

      SUMMARY_PROMPT = "给我一个不超过100字的简短摘要。这里有很多页面，这只是其中一个。这个100字的摘要必须简明扼要地涵盖这个特定文档页面中讨论的所有内容，以便阅读这个简短摘要的人能够全面了解如果他们阅读整个页面将会学到什么。"

      # 获取事件循环
      # 运行直到完成
      #   self.process_nodes(nodes, summarizer, SUMMARY_PROMPT)
      # )
      print("开始异步处理节点...")
      await self.process_nodes(nodes, summarizer, SUMMARY_PROMPT)
      print("节点处理完成")

      return nodes
    except Exception as e:
      print(f"acall 方法执行过程中出错: {str(e)}")
      traceback.print_exc()
      raise
    finally:
      print("===== DocsSummarizerTransform.acall 执行完毕 =====")