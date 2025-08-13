from typing import Callable
from app.prompts.prediction_prompt import CRICKET_LIVE_EVENTS_TEMPLATE, CRICKET_LIVE_INFORMATION, CRICKET_LIVE_BROWSER_RESPONSE_FORMATTER,GENERATE_CHIPS_FROM_USER_HISTORY
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import BraveSearch
from app.services.tools import llm_websearch
from langchain.tools import Tool
from app.services.tools import llm
import os,json
from langchain_core.runnables import RunnableLambda
from app.utils.helper import get_live_cricket_matches





# ---------------------------------------------------------------------------------------------------------
def generate_cricket_prompt(
    search_snippets: str, format_instruction_func: Callable[[], str]
) -> str:
    """
    Formats the cricket prompt with search snippets and format instructions.
    """
    return CRICKET_LIVE_EVENTS_TEMPLATE.format(
        search_snippets=search_snippets, format_instructions=format_instruction_func()
    )


# make the history output as question for brave for custom message/question
def generate_prompt_for_custom_question(search_string: str, format_instruction_func: Callable[[], str]) -> str:
    return CRICKET_LIVE_INFORMATION.format( input=search_string, format_instructions=format_instruction_func()
    )


def generate_prompt_for_browser_result_formatting(browser_response:str,format_instruction_func: Callable[[], str]) -> str:
    return CRICKET_LIVE_BROWSER_RESPONSE_FORMATTER.format( search_response=browser_response, format_instructions=format_instruction_func())
# ---------------------------------------------------------------------------------------------------------

# prompt service for runnable ai response


def core_chain_for_runnablehistory():
    prompt = ChatPromptTemplate.from_messages(
        [MessagesPlaceholder(variable_name="history"), ("human", "{input}")]
    )
    core_chain = prompt | llm | StrOutputParser()
    return core_chain





# function to Handle generate chips from user history
def generate_chips_from_user_history_prompt(history_snippets, format_instruction_func: Callable[[], str]) -> str:
    return GENERATE_CHIPS_FROM_USER_HISTORY.format(
        history_snippets=history_snippets, format_instructions=format_instruction_func()
    )
    

# system_prompt = """
# You are a smart assistant that only answers questions related to cricket and don't use BraveSearch tool again and again for the same question.

# For a direct and live cricket score, you MUST use the CricbuzzLiveMatches tool. 

# Check the current message and recent chat history:


# If any message in the last 20 exchanges was about cricket, then treat the current message as cricket-related, even if it's a follow-up or vague.

# Otherwise, treat it as non-cricket-related.

# If the message is not related to cricket (and there’s no cricket context in recent history), respond:

# "I can't reply to questions that are unrelated to cricket."

# If the question is about live scores, ongoing matches, or current events, you MUST use the BraveSearch tool to find the latest information.

# Do NOT use BraveSearch repeatedly for the same live score question. Cache or reuse recent results if the same question is repeated within a short time (e.g., 5 minutes).

# Respond clearly and concisely based on BraveSearch results if available. Do NOT say you lack access to real-time info if BraveSearch gives you answers.
# """



# system_prompt = """
# You are a smart assistant that ONLY answers questions related to cricket.

# 🔒 Rules:

# 1. If the current user message is not about cricket **and** no cricket-related topic has been discussed in the last 20 exchanges, respond with:
#    ➤ "I can't reply to questions that are unrelated to cricket."

# 2. If any of the last 20 messages were about cricket, treat the current message as cricket-related — even if it's vague or a follow-up.

# 3. For live scores or ongoing match updates:
#    - ✅ You MUST use the CricbuzzLiveMatches tool to fetch accurate, real-time data.
#    - 🔁 Use BraveSearch ONLY if CricbuzzLiveMatches doesn't provide the needed information.
#    - 🚫 DO NOT repeatedly use BraveSearch for the same or similar queries within a short window (e.g., 5 minutes). Reuse recent valid results instead.
#    - ✅ Before responding, always check that the score or match info you’re about to reply with is accurate and up to date — never give outdated, cached, or potentially incorrect info.

# 4. For historical cricket info, player stats, schedules, or general cricket questions:
#    - Use relevant tools or your internal knowledge appropriately.
#    - Ensure responses are factually correct and clearly presented.

# 🧠 Always behave like a helpful, up-to-date cricket expert. Your job is to give accurate, crisp, and relevant answers — only for cricket.
# """


system_prompt = """
You are a smart assistant that ONLY answers questions related to cricket.

🔒 Rules:

1. If the current message is NOT related to cricket AND there has been no cricket discussion in the last 20 messages:
   ➤ Respond with: "I can't reply to questions that are unrelated to cricket."

2. If any message in the last 20 was about cricket, treat the current message as cricket-related — even if it's vague, a follow-up, or missing context.

3. For live scores, ongoing matches, or current cricket events:
   - ✅ Use the CricbuzzLiveMatches tool to fetch accurate, real-time data.
   - 🔁 Use BraveSearch and LLMWebSearch ONLY if CricbuzzLiveMatches doesn't provide the needed info or no information.
   - 🕔 Avoid repeated BraveSearch use for the same or similar queries within 5 minutes — reuse valid, recent results instead.
   - ⚠️ Always ensure live scores or match information are accurate and not outdated before responding.

4. For general cricket queries like:
   - Player stats, match schedules, past match details
   - Team comparisons, strategies, pitch reports
   ➤ Use trusted internal knowledge or tools. Ensure factual accuracy and clarity.

5. If the user asks to create a **Dream11 team** or a team for **any fantasy cricket platform**:
   - ✅ Use up-to-date match details, player form, playing XI, pitch report, and weather when available.
   - ✅ Give a balanced team (captain, vice-captain, player mix) suitable for fantasy points.
   - ⚠️ Clearly mention if any key info like playing XI is not officially confirmed yet.
   - ❌ Do NOT give outdated player picks based on old or irrelevant matches.

🧠 Always act like a helpful, knowledgeable, and current cricket analyst. Your job is to provide sharp, factual, and useful cricket-specific responses — and ONLY for cricket.
"""




brave_raw = BraveSearch.from_api_key(api_key=os.getenv("BRAVE_API_KEY"), search_kwargs={"count": 10})
def generate_core_chain_agent_executor_for_runnablehistory():
    """
    Create a Tool-Calling prompt template.
    """
    
    cricbuzz_tool = Tool(
    name="CricbuzzLiveMatches",
    func=get_live_cricket_matches,
    description="Useful for getting a list of live cricket matches and their current scores and status. Use this tool for all questions about live cricket scores."
)
    
    brave_tool = Tool(
        name="BraveSearch",
        func=brave_raw.run,
        description="Useful for answering questions about current events or real-time information like sports scores, news, or ongoing events."
    )
    
    
    llm_websearch_tool = Tool(
        name="LLMWebSearch",
        func=llm_websearch,
        description="Useful for answering questions about current events or real-time information like sports scores, news, or ongoing events."
    )
    tools = [brave_tool, cricbuzz_tool]

    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", "You are a smart assistant. Use tools like BraveSearch when user asks about current events or unknown topics."),
    #     MessagesPlaceholder(variable_name="history"),
    #     MessagesPlaceholder(variable_name="agent_scratchpad"),
    #     ("human", "{input}")
    # ])
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        ("human", "{input}")
    ])
    # 4. Create the agent using LangChain Agent Runner
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    
    return agent_executor





# ---------------------------------------------------------------------------------------------------

# testing_prompt = """
# You are a sharp, no-nonsense cricket expert.

# For every cricket-related question, you must first perform a live web search using trusted cricket websites (e.g., ESPNcricinfo, Cricbuzz, BBC Sport, The Guardian).

# Ignore old or outdated information from memory or past training. Always rely on the latest web search results to answer.

# Provide clean, accurate, and to-the-point answers based only on what the real-time search returned.

# Do not include links or URLs in your response.

# For prediction questions like match outcome or Dream11:

# Fetch the latest team lineups, form, pitch, and weather using web search.

# Then predict a Dream11-style team with clear reasoning.

# If the question is not about cricket, respond only with:
# "I don't know."

# If live web search fails or gives no useful result, respond:
# "Live data not available right now. Please try again shortly."
# """

testing_prompt = """
You are a sharp and focused cricket assistant.

Your job is to provide accurate, up-to-date cricket information using the web search results provided in the input. These results may include current match scores, upcoming fixtures, team lineups, player stats, news, weather, pitch reports, or anything relevant to ongoing or recent cricket events.

### Rules:

1. Always use the **web search result** given in the input to generate your answer. Do **not guess** or use prior knowledge unless it matches the provided search data.

2. You may use the **conversation history** only to understand the user’s context or follow-up questions, but you **must not fabricate or assume facts** not present in the search result.

3. If the user's query is **not about cricket**, respond with:
> "I can only assist with cricket-related questions."

4. If the web result is **empty or unhelpful**, respond with:
> "Live data not available right now. Please try again shortly."

Keep your answers clear, concise, and fact-based.
"""

def tool_for_livesearch():
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", testing_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    
    def enrich_input_with_websearch(inputs: dict) -> dict:
        user_input = json.dumps(inputs["input"])
        history = inputs.get("history", [])
        search_result = llm_websearch(user_input)
        # search_result = tavily_browser_search(user_input)
        enriched_input = f"{user_input}\n\nWeb result:\n{search_result}"
        return {"input": enriched_input, "history": history}
    
  
    chain = (
        RunnableLambda(enrich_input_with_websearch)
        | prompt
        | llm
    )
    
    return chain



