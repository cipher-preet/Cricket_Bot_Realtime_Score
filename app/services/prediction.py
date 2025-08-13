from app.services.Prompt_services import generate_cricket_prompt, generate_prompt_for_custom_question, generate_prompt_for_browser_result_formatting,generate_chips_from_user_history_prompt
from app.utils.pydantic_validation import output_parser, formatted_output, formatted_browser_response,formatted_extract_chips
from app.services.tools import llm
import re




# from app.utils.helper import (
#     generate_Query_For_Brave_Search,
#     get_Global_results_from_brave_search,
#     combine_final_response_with_brave_results,
# )


# ---------------------------------------------------------------------------------------------------------


def extract_ongoing_cricket_leagues(search_snippets: str):
    prompt = generate_cricket_prompt(
        search_snippets, format_instruction_func=output_parser.get_format_instructions
    )
    response = llm.invoke(prompt).content
    try:
        parsed_output = output_parser.parse(response)
        return parsed_output.model_dump()
    except Exception as e:
        return {"error": "Failed to parse response", "raw_output": response}



#------------------------------------------------------------------------------------------------------------------
# function is used to extract the chips from the user history

def extract_chips_from_user_history(user_history: str):
    prompt = generate_chips_from_user_history_prompt(history_snippets=user_history, format_instruction_func=formatted_extract_chips.get_format_instructions)
    
    response = llm.invoke(prompt).content
    try:
        parsed_output = formatted_extract_chips.parse(response)
        return parsed_output.model_dump()
    except Exception as e:
        return {"error": "Failed to parse response", "raw_output": response}

#------------------------------------------------------------------------------------------------------------------


# generate query for brave search 

def prompt_question_for_browser_search(user_input:str):
    prompt = generate_prompt_for_custom_question(user_input, format_instruction_func=formatted_output.get_format_instructions)
    
    response = llm.invoke(prompt).content.strip()
    print("response", response)
    if response.lower() == ("The input is not related to cricket.").lower():
        return {"not_related":True, "response":"The question must relate to cricket, whether past or present."}
    try:
        parsed_output = formatted_output.parse(response)
        return parsed_output.model_dump()
    except Exception as e:
        return {"error": "Failed to parse response", "raw_output": response}


def chatting_response_formatter(browser_resposne:str):
    prompt = generate_prompt_for_browser_result_formatting(browser_resposne, format_instruction_func=formatted_browser_response.get_format_instructions)
    response = llm.invoke(prompt).content
    try:
        parsed_output = formatted_browser_response.parse(response)
        return parsed_output.model_dump()
    except Exception as e:
        return {"error": "Failed to parse response", "raw_output": response}
    
# ---------------------------------------------------------------------------------------------------------


def check_if_response_outdated(response: str) -> bool:
    response_lower = response.lower()

    outdated_indicators = [
        "don't have the capability to provide live",
        "unable to provide live",
        "do not have real-time",
        "currently don't have the capability",
        "cannot provide real-time",
        "not updated live",
        "check the live score",
        "check live updates",
        "visit espn",
        "visit cricbuzz",
        "official icc website",
        "real-time scores",
        "check official site",
        "for up-to-date info",
        "for latest updates",
        "you can check",
        "you may visit",
        "please visit"
    ]

    # Basic string-based check
    for phrase in outdated_indicators:
        if phrase in response_lower:
            return True

    # Optional: detect old years
    import re
    old_dates = re.findall(r'\b(20[0-1][0-9]|202[0-3])\b', response)
    if old_dates:
        return True

    return False



def extract_ongoing_cricket_leagues_By_tavily_search(search_snippets: str):
    prompt = generate_cricket_prompt(
        search_snippets, format_instruction_func=output_parser.get_format_instructions
    )
    response = llm.invoke(prompt).content
    try:
        parsed_output = output_parser.parse(response)
        return parsed_output.model_dump()
    except Exception as e:
        return {"error": "Failed to parse response", "raw_output": response}


# ---------------------------------------------------------------------------------------------------------


# def generate_output_for_brave_search_plus_llmIntelegence():



