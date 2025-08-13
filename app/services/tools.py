from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.tools import BraveSearch
from langchain_tavily import TavilySearch
from langchain_core.tools import Tool,tool
import os, requests

load_dotenv()

api_key = os.getenv("BRAVE_API_KEY")
travily_api_key = os.getenv("TAVILY_API_KEY")

#---------------------------------------------------------------------------------------------


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=512)


brave_tool = BraveSearch.from_api_key(api_key=api_key, search_kwargs={"count": 20})


tavily = TavilySearch(
    api_key=travily_api_key,
    max_results=25,
    topic="general",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
    search_depth="advanced",
    time_range="day",
    include_domains=["cricbuzz.com", "espncricinfo.com", "icc-cricket.com"],
    exclude_domains=None,
)


#----------------------------------------------------------------------------------------------------------------


llm_realtime = ChatOpenAI(model="gpt-4.1-mini", output_version="responses/v1")


# ------------------- brave search with API tool --------------------------------------



BRAVE_API_KEY = "BSA6O_eholKiceJBLaxW5LsaYX2Ag_E"  

def brave_web_search_fn(query: str) -> str:
    """
    Uses Brave Search API to search the web and returns summarized descriptions.
    Useful for getting up-to-date real-world information.
    """
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "result_filter": "web",
        "count": 20 
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        data = response.json()
        print("this is the dasta ******************************* ", data)

        snippets = [r["description"] for r in data.get("web", {}).get("results", [])]
        combined_text = "\n".join(snippets)
        # return combined_text if combined_text else "No web results found."
        return data
    except Exception as e:
        return f"Search failed: {str(e)}"




brave_search_tool = Tool.from_function(
    func=brave_web_search_fn,
    name="brave_web_search",
    description="Search the web in real time using Brave Search. Input should be a query string."
)




def llm_websearch(query:str) -> str:
    builtin_web_tool = {"type": "web_search_preview"}
    llm_with_tools = llm_realtime.bind_tools([builtin_web_tool,brave_search_tool])

    result = llm_with_tools.invoke(query)
    return result.content if hasattr(result, "content") else str(result)
