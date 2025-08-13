from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List


#-------------------------------------------------------------------------------------------------------------------------

# define output Format
class LeagueOutputFormat(BaseModel):
    trending_leagues_and_tours: List[str] = Field(
        ...,
        description="List of currently ongoing cricket leagues and international tours",
    )


class Cricketquestionformat(BaseModel):
    question: str = Field(..., description="Well-formed cricket-related question suitable for browser search.",)
    

class Cricketresponsebrowser(BaseModel):
    result: str = Field(..., description="well-formed, accurate information and present it clearly in a user-friendly format.",)
    
    
    
class extract_chips_from_user_history(BaseModel):
    chips: List[str] = Field(
        ...,
        description="List of chips extracted from the user's chat history.",
    )

formatted_output = PydanticOutputParser(pydantic_object=Cricketquestionformat)
formatted_browser_response = PydanticOutputParser(pydantic_object=Cricketresponsebrowser)
# create a paerser
formatted_extract_chips = PydanticOutputParser(pydantic_object=extract_chips_from_user_history)

output_parser = PydanticOutputParser(pydantic_object=LeagueOutputFormat)

#-------------------------------------------------------------------------------------------------------------------------

