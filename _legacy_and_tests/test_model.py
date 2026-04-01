import asyncio
import logging
import sys
import os
from app_local import PatchedChatOllama
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO)

async def test():
    print("Iniciando prueba de modelo 3b...")
    try:
        llm = PatchedChatOllama(model="qwen2.5-coder:3b", temperature=0)
        messages = [HumanMessage(content="Hola, responde solo 'TEST_OK'")]
        print("Llamando a _agenerate...")
        result = await llm._agenerate(messages)
        print(f"Resultado obtenido: {result}")
        if result:
            print(f"Contenido: {result.generations[0].message.content}")
        else:
            print("ERROR: El resultado es None")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
