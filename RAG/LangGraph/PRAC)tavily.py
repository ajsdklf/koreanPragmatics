from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
print(tool.invoke("What's a 'node' in LangGraph?"))