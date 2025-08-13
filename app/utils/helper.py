# from langchain_community.tools import BraveSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from app.services.tools import llm
from langchain_core.output_parsers import StrOutputParser
from app.database.mongodb import get_memory
# import http.client
import os, requests
 


from app.services.tools import brave_tool, tavily


# ------------------------ define tool for get-Trending-Cricket-League --------------------------------------------
@tool
def brave_cricket_search(_input: str = "") -> str:
    """
    Performs a globally refined Brave search for currently live or ongoing cricket leagues and tours.
    Filters out previews, news, and non-authoritative content.
    """
    query = (
        '"live cricket match" OR '
        '"today cricket schedule" OR '
        '"ongoing cricket series" OR '
        '"domestic cricket tournament India" OR '
        '"international cricket fixtures today" OR '
        '"T20 league live score"'
        "-preview -opinion "
        "site:cricbuzz.com OR site:espncricinfo.com OR site:icc-cricket.com"
    )
    return brave_tool.run(query)


# ----------------------------------------------------------------------------------------------------------------


# ------------------------ define tool for get-Trending-Cricket-League using Tavily search --------------------------
@tool
def tavily_cricket_search(_input: str = "") -> str:
    """
    Performs a Tavily search for currently live or ongoing cricket leagues and tours.
    Filters out previews, news, and non-authoritative content.
    """
    return tavily.invoke(
        {
            "query": (
                '"live cricket match" OR '
                '"today cricket schedule" OR '
                '"ongoing cricket series" OR '
                '"domestic cricket tournament India" OR '
                '"international cricket fixtures today" OR '
                '"T20 league live score"'
            ),
            "include_domains": None,
            "exclude_domains": None,
        }
    )


# ------------------------ modify user query using llm suitable for brave search --------------------------------------
def generate_Query_For_Brave_Search(input: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a precise and intelligent assistant that refines user inputs into clean, search-optimized queries for Brave Search. "
                "Your job is to preserve the user's original cricket-related intent (e.g., match results, player stats, team news, tournament updates), and rephrase the input clearly and concisely. "
                "Do NOT invent or assume details like names, dates, or match events. Do NOT add extra context not present in the original input. "
                "Only clarify, clean, and enhance the wording for better search engine understanding. "
                "If the input is already clear, make only minor adjustments. Focus exclusively on cricket-related queries.",
            ),
            ("user", "{input}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": input})


# ---------------------------------------------------------------------------------------------------------------------


def get_Global_results_from_brave_search(query: str) -> str:
    """
    Enhances the search query with global cricket context and fetches results from Brave Search.
    """
    # enriched_query = (
    #     f"{query} cricket news OR live score OR match update OR player stats "
    #     f"site:icc-cricket.com OR site:espncricinfo.com OR site:cricbuzz.com"
    # )
    # return brave_tool.run(enriched_query)
    return brave_tool.arun(query)


# -----------------------------------------------------------------------------------------------------------------------


def combine_final_response_with_brave_results(
    input: str, search_results
) -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a highly knowledgeable cricket assistant that provides smart, structured answers by combining real-time search results with your internal understanding of the sport. "
                "Your primary task is to interpret the user's cricket-related query — such as match outcomes, player performance, stats, records, pitch reports, or predictions — and deliver a well-formatted response "
                "using both the provided Brave Search data and your own intelligence.\n\n"
                "Here's how you should respond:\n"
                "- Extract useful facts from the Brave Search results when available (e.g., scores, team news, recent events).\n"
                "- Use your own knowledge to fill in gaps, provide predictions, context, or comparisons.\n"
                "- If suitable, present structured content using **tables**, **bullet points**, or **numbered lists** for clarity.\n"
                "- Highlight important players, statistics, or match details clearly.\n"
                "- Your tone should be expert but accessible — imagine explaining cricket to an informed fan.\n"
                "- Never hallucinate data. If real-time data is unclear or missing, say so transparently.\n"
                "- Only answer questions directly related to cricket. Politely decline anything off-topic.\n\n"
                "Final answers must be structured, insightful, and should combine factual accuracy with intelligent synthesis. Use formatting and concise language to make your responses engaging and easy to understand.",
            ),
            ("placeholder", "{history}"),
            ("user", "User query: {input}\n\nBrave Search Results: {search_results}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": input, "search_results": search_results})


# ----------------------------------------------------------------------------------------------------------------------

# get chat history for runnable ai


def get_chat_history_for_runnable_ai(session_id: str):
    """
    Retrieves chat history for a given session ID.
    """
    print("Retrieving chat history for session:", session_id)
    memory = get_memory(session_id)
    chat_history = memory.messages
    return chat_history
    



# get the data from brave for custom search query

@tool
def brave_browser_search(input: str = "") -> str:
    """
        Enhances the search query for proper search.
    """
     
    return brave_tool.run(input)


@tool
def get_cricbuzz_data() -> str:
    """
    Fetches cricket data from Cricbuzz.
    """
    # url = "https://www.cricbuzz.com/api/html/cricket-scorecard"
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Failed to fetch data: {str(e)}"


def get_live_cricket_matches(_input: str = "") -> str:
    """
    Fetches a list of live cricket matches from the Cricbuzz RapidAPI.
    This tool should be used for all live cricket score queries.
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_CRICBUZZ_KEY"),
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Return a structured string representation of the JSON to help the LLM
        live_matches_data = response.json()
        
        # Simple formatting to make it readable for the LLM
        # formatted_output = "Live Cricket Matches:\n"
        # for match in live_matches_data.get("typeMatches", []):
        #     match_info = match.get("matchInfo", {})
        #     series_name = match_info.get("seriesName", "N/A")
        #     match_desc = match_info.get("matchDesc", "N/A")
        #     match_status = match_info.get("status", "N/A")
        #     formatted_output += f"- Series: {series_name}, Match: {match_desc}, Status: {match_status}\n"
            
        return live_matches_data
    
    except requests.exceptions.RequestException as e:
        return f"An API request error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


#-------------------------------------------------------------------------------------------------

@tool
def tavily_browser_search(query: str) -> str:
    """
    Performs a Tavily search for currently live or ongoing cricket leagues and tours.
    Filters out previews, news, and non-authoritative content.
    """
    return tavily.invoke(
        {
            "query": query,
            "include_domains": None,
            "exclude_domains": None,
        }
    )
    
    
    

