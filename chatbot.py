from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI()

def chat_node(state: ChatState):
    messages = state['messages']

    response = llm.invoke(messages)
    return {"messages": [response]}

graph = StateGraph(ChatState)
checkpointer = MemorySaver()

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile()

with open("graph.png", "wb") as f:
    f.write(chatbot.get_graph().draw_mermaid_png())
print("Graph saved to graph.png")


thread_id = '1'


initial_state = {
    'messages': [HumanMessage(content='What is the capital of india')]
}
chatbot.invoke(initial_state)['messages'][-1].content

chatbot = graph.compile(checkpointer=checkpointer)

while True:
    user_message = input('Type here: ')

    if user_message.strip().lower() in ['exit', 'quit', 'bye']:
        print("Exiting...")
        break
    config = {'configurable': {'thread_id': thread_id}}
    state = {
        'messages': [HumanMessage(content=user_message)]
    }
    response = chatbot.invoke(state, config = config)['messages'][-1].content
    print(response)