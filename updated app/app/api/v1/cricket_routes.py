from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json
from app.models.chathistory_model import chathistory
from app.models.foundational_model import bookmark_history
from langchain_core.runnables import RunnableWithMessageHistory
from app.database.mongodb import get_memory
from app.services.Prompt_services import tool_for_livesearch, generate_core_chain_agent_executor_for_runnablehistory

from app.api.repository.mongo_repo import chathistoryrepo


from app.services.prediction import (
    extract_ongoing_cricket_leagues,
    extract_chips_from_user_history
    # prompt_question_for_browser_search,
    # chatting_response_formatter,
    # check_if_response_outdated
)
from app.utils.helper import brave_cricket_search  
from app.services.prediction import extract_ongoing_cricket_leagues
from app.api.repository.mongo_repo import HandleSessionLogic,GetchatApis,BookmarkApis,ChatRepository



# router = APIRouter(prefix="/api/v1", tags=["cricket"])
router = APIRouter(tags=["cricket"])
historycollection =  os.getenv("COLLECTION_NAME")

# ------------------------ Health Check Route ----------------------------


@router.get("/health", summary="Health Check", tags=["Monitoring"])
async def health_check():
    return JSONResponse(
        status_code=200, content={"status": "ok", "message": "Service is healthy"}
    )


# ------------------------ get trending cricket leagues route fro Home Page ----------------------------


@router.get(
    "/get_trending_cricket_leagues",
    summary="Get Trending Cricket Leagues",
    description="Returns a list of currently trending or ongoing cricket leagues using Brave search and custom extract logic.",
)
def get_trending_cricket_leagues():
    try:
        search_snippets = brave_cricket_search.invoke("")
        response = extract_ongoing_cricket_leagues(search_snippets)

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))


# ---------------------------------------------------------------------------------------------------------


# gety trending leagues using Tavily search
# @router.get(
#     "/get_trending_cricket_leagues_tavily",
#     summary="Get Trending Cricket Leagues using Tavily",
#     description="Returns a list of currently trending or ongoing cricket leagues using Tavily search.",
# )
# def get_trending_cricket_leagues_tavily():
#     try:
#         search_snippets = tavily_cricket_search.invoke("")
#         response = extract_ongoing_cricket_leagues_By_tavily_search(search_snippets)

#         return JSONResponse(status_code=200, content=response)

#     except Exception as e:
#         return JSONResponse(status_code=500, content=str(e))


# router for post data to database for history track


# @router.post(
#     "/custom_search_conversation",
#     summary="Post custom query for search",
#     description="custom query by user for perticular search about the cricket, The AI's response and session details.",
# )
# async def send_custom_query_for_search(message: chathistory):
#     try:
#         # message = message.model_dump()
#         print("\+++++++++++++++++++++++++++++++++ ", message)
        
#         core_chain = core_chain_for_runnablehistory()

#         with_history_chain = RunnableWithMessageHistory(
#             runnable=core_chain,
#             get_session_history=get_memory,
#             input_messages_key="input",
#             history_messages_key="history",
#         )
#         print(type(message.content)) 
#         ai_response = await with_history_chain.ainvoke(
#             {"input": json.dumps(message.content)},
#             config={"configurable": {"session_id": message.sessionId}},
#         )


#         # make the history output as question for brave
#         browser_ques = prompt_question_for_browser_search(ai_response)
        
#         is_outdated = check_if_response_outdated(ai_response)
        
#         if is_outdated or browser_ques.get("not_related"):
#             if browser_ques.get("not_related"):
#                 return JSONResponse(
#                     status_code=200,
#                     content={"success": True, "message": str(browser_ques.get('response', 'No related information.'))}
#                 )
#             # get the data from brave search
#             # browser_response_data = brave_browser_search(str(browser_ques.get('question')))  
#             # browser_response_data = tavily_browser_search(str(browser_ques.get('question')))  
#             # browser_response_data = llm_websearch(str(browser_ques.get('question')))  
#             browser_response_data = brave_web_search_fn(str(browser_ques.get('question')))  
#             print("------------------------------",browser_response_data)
            
#             # make the output to show to user
#             final_output = chatting_response_formatter(browser_response_data)

#             # make history again
#             doc = {
#                 "SessionId": message.sessionId,
#                 "History": json.dumps({
#                     "type": "ai",
#                     "data": {
#                         "content": final_output.get('result'),
#                         "additional_kwargs": {},
#                         "response_metadata": {},
#                         "type": "ai",
#                         "name": "None",
#                         "id": "None",
#                         "example": "False"
#                     }
#                 })
#             }
#             insertedcustomchat = chathistoryrepo.insertone_custom_data(doc)
            
            
#             # send the output to user
#             print(str(final_output.get('result')))
#             return JSONResponse(
#                 status_code=200, content={"success": True, "message": final_output.get('result')}
#             )

#             # return JSONResponse(
#             #     status_code=200,
#             #     content={"success": True, "message": browser_ques.get('response', 'No related information.')}
#             # )
#         print(str(ai_response))
#         return JSONResponse(
#             status_code=200, content={"success": True, "message": ai_response}
#         )
        
        
#     except Exception as e:
#         print("Error in send_custom_query_for_search:", e)
#         return JSONResponse(status_code=500, content=str(e))




@router.post(
    "/chatwithstumpzydashboard",
    summary="Post chatting query for search",
    description="chatting query by user for perticular search about the cricket, The AI's response and session details.",
)
async def send_chatting_query_for_search(message: chathistory):
    try:
        
        # message = remove_censored_words(message.content)
        
        core_chain = generate_core_chain_agent_executor_for_runnablehistory()
        
        with_history_chain = RunnableWithMessageHistory(
            runnable=core_chain,
            # get_session_history=get_memory,
            get_session_history=lambda session_id: get_memory(session_id),
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="output"
        )
        
        ai_response = await with_history_chain.ainvoke(
            {"input": message.content},
            config={"configurable": {"session_id": message.sessionId}},
        )
       
        
        output = ai_response.get("output", "").strip()

        if not output:
            print("Agent response is empty. Full response:", ai_response)
            return JSONResponse(
                status_code=200,
                content={"success": False, "message": "Empty response from agent."}
            )

         
        #------------------- add Logic to change session name-------------------------------------------
        chat_repo = ChatRepository()
        upadted_name = HandleSessionLogic()        
        chat_count  = chat_repo.count_documents({"SessionId": message.sessionId})
        if chat_count  == 2:
            upadted_name.updated_session_chat_name(message.sessionId, output)

        #----------------------------------------------------------------------------------------------
    
        return JSONResponse(
            status_code=200, content={"success": True, "message": output}
        )
        
    
    except Exception as e:
        print("Error in initializing core chain:", e)
        return JSONResponse(status_code=500, content=str(e))

# -------------------------------experimental API for custom search conversation ( PREET )--------------------------------------


# @router.post(
#     "/custom_search_conversation_experimental",
#     summary="Post custom query for search (Experimental)",
#     description="Custom query by user for particular search about cricket, The AI's response and session details.",
# )
# async def send_custom_query_for_search_experimental(message: chathistory):
#     try:

#         # chain = generate_output_for_brave_search_plus_llmIntelegence({})

#         # with_history_chain = RunnableWithMessageHistory(
#         #     runnable=chain,
#         #     get_session_history=get_memory,
#         #     input_messages_key="input",
#         #     history_messages_key="history",
#         # )

#         get_history = get_chat_history_for_runnable_ai("abtestc123")
#         # print("Chat history for session:", get_history)


#         # ai_response = await with_history_chain.ainvoke(
#         #     {"input": message.content},
#         #     config={"configurable": {"session_id": message.session_id}},
#         # )

#         return JSONResponse(
#             status_code=200, content={"success": True, "message": get_history}
#         )

#     except Exception as e:
#         print("Error in send_custom_query_for_search_experimental:", e)
#         return JSONResponse(status_code=500, content=str(e))


# --------------------------------------------------------------------------------------------------------------------------------



@router.get("/getChatHistorybysessionid", summary="fetch chat History of the user by its session Id", description="API is used to fetch the chat history by thr user Session ID with pagination")
def get_chat_history_title(SessionId: str,page:int):
    try:
        response = chathistoryrepo.get_user_chat_history(SessionId,page) 
        return JSONResponse(
            status_code=200, content={"success": True, "message": response}
        )
        
    except Exception as e:
        print("Error in get ChatHistory by user session ID :", e)
        return JSONResponse(status_code=500, content=str(e))
        
    
    
# ------------------------------------- create New Chat API ---------------------------------------------------------------

@router.post("/createnewchat",summary="create new Chat by the user", description="API is used to create new chat with new session Id")
def create_new_chat(userId:str):
    try:
               
        sessionrepo = HandleSessionLogic()
        sessionrepo.create_new_session_chat(userId)
               
        return JSONResponse(
            status_code=200, content={"success": True, "message": "new Chat created"}
        )
        
    except Exception as e:
        print("Error in create new chat :", e)
        return JSONResponse(status_code=500, content=str(e))
    
    
    
    
# -------------------------------------- API to getchat sesssion by user Id -------------------------------------
@router.get("/getchatsession",summary="get chat sessions by user ID", description="API is used to get the chat session based upon the used Id for side Bar")
def get_chat_session(userId:str,page:int):
    try:
        getSessionData = GetchatApis()
        
        result = getSessionData.get_chat_session(userId,page)
        
        return JSONResponse(
            status_code=200,content={"success":True,"data":result}
        )
        
    except Exception as e:
        print("Error while fetching chat sessions :", e)
        return JSONResponse(status_code=500, content=str(e))
    



#---------------------------------- Mark the bookmark ----------------------------------------------

@router.post("/markbookmark", summary="user can bookmark the prompt", description="API is used to bookmark the prompt from the used to use in future prompt")
def post_bookmark(data:bookmark_history):
    try:
        bookmark_class = BookmarkApis()
        bookmark_class.create_bookmark_list(data)
        
        return JSONResponse(
            status_code=200,content={"success":True,"message": "mark as Bookmark sucessfully"}
        )
    
    
    except Exception as e:
        print("error while posting the book mark :" ,e)
        return JSONResponse(status_code=500, content=str(e))





@router.get("/getbookmarkbuuserId", summary=" get the bookMark by user Id", description="API is used to get the bookmark history for partucular user by user Id")
def get_bookmark(userId:str):
    try:
        bookmark_class = BookmarkApis()
        result = bookmark_class.get_bookmark_data(userId)
        
        return JSONResponse(
          status_code=200,content={"success":True,"data": result}  
        )
    
    except Exception as e:
        print("error while getting the bookmark data :",e)
        return JSONResponse(status_code=500, content=str(e))




# ------------------------  DELETE THE BOOKMARK BY ID ------------------------------------

@router.delete("/deletebookmarkbyid", summary="delete the bookmark by Id", description="API is used to delete the bookmark by its Id")
def delete_bookmark_by_id(bookmarkId: str):
    try:
        
        bookmark_class = BookmarkApis()
        bookmark_class.delete_bookmark_by_id(bookmarkId)
        
        return JSONResponse(
            status_code=200, content={"success": True, "message": "Bookmark deleted successfully"}
        )
    
    except Exception as e:  
        print("error while deleting the bookmark by Id :", e)
        return JSONResponse(status_code=500, content=str(e))


  

#-------------------------------------------------------------------------------------------------------


# API TO GET THE CHIPS IN THE CONTEXT OF THE CHAT HISTORY
@router.get("/getchipsbycontext", summary="get chips by context", description="API is used to get the chips by the cotntext of the chat history")
def get_chips_by_context(sessionId: str):
    try:
        
        chat_history = get_memory(sessionId)
        response = extract_chips_from_user_history(chat_history)
        
        if not response:
            return JSONResponse(
                status_code=200, content={"success": True, "message": "No chips found in the context"}
            )
            
        return JSONResponse(status_code=200, content=response)
           
    except Exception as e:
        print("error while getting the chips by context :", e)
        return JSONResponse(status_code=500, content=str(e))



#-------------------------------------------------------------------------------------------------------




@router.post("/chatwithme")
def chat_with_me(message:chathistory):
    try:
        core_chain = tool_for_livesearch()
        
        with_history_chain = RunnableWithMessageHistory(
            runnable=core_chain,
            get_session_history=get_memory,
            input_messages_key="input",
            history_messages_key="history",
        )
   
        result = with_history_chain.invoke({"input": message.content}, config={"configurable": {"session_id": message.sessionId}})
        return {"result": result.content}
    
    except Exception as e:
        print("error while chatting with me : ", e)
