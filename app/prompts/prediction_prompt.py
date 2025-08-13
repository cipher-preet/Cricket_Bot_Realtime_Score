from langchain.prompts import ChatPromptTemplate


# ---------------------------------------------------------------------------------------------------------------------

CRICKET_LIVE_EVENTS_TEMPLATE = ChatPromptTemplate.from_template(
    """
You are a cricket data assistant.

From the following web search result snippets, extract the names of all **currently ongoing or live cricket leagues, tournaments, or international tours**.

🎯 Your goal is to identify **active** events happening **right now** across:
- ✅ International level (e.g., "India Tour of England", "ICC World Test Championship")
- ✅ Domestic leagues (e.g., "Vitality Blast", "CPL", "BBL", "PSL")
- ✅ Indian domestic cricket (e.g., "Ranji Trophy", "Duleep Trophy", "Syed Mushtaq Ali Trophy", "Vijay Hazare Trophy", "Deodhar Trophy", "Irani Cup", "CK Nayudu Trophy", "Women's T20 Trophy")
- ✅ National-level tournaments or bilateral series (e.g., "Sri Lanka vs Bangladesh", "India Women vs South Africa Women")

✅ Include:
- Any league, tournament, or tour clearly mentioned as **live**, **in progress**, **ongoing**, or currently providing **live scores**
- Competitions actively taking place in **any country**, especially **India’s domestic cricket** (Men’s or Women’s cricket)

🚫 Exclude:
- Future or upcoming events (e.g., "IPL 2026", "India Tour of Australia 2026")
- Past or recently concluded series
- Match previews or one-off matches (e.g., "2nd T20 preview", "Final match preview")
- Rankings, scorecards, or statistical pages

📦 Return the data in **pure JSON format only** (no explanation or comments) as:

{format_instructions}

📄 Search Snippets:
{search_snippets}
"""
)



CRICKET_LIVE_INFORMATION = ChatPromptTemplate.from_template(
    """
You are a cricket-aware query rewriter for a search assistant.

Your job is to:

1. Carefully read the user input below, which may be a paragraph, informal explanation, or direct/indirect request related to cricket.

2. Extract the user’s actual intent or question related to cricket (such as match scores, team stats, player performance, news, schedules, etc.).

3. Rewrite this intent as a clear, standalone natural-language question.

4. If relevant, expand it into a proper cricket context question without mentioning specific tournaments.

5. Return ONLY one of the following:

   - If the input IS related to cricket, output ONLY a valid JSON object formatted exactly as described in the {format_instructions} placeholder below. No additional text or explanation.

   - If the input IS NOT related to cricket, respond ONLY with this exact sentence (no quotes and no extra text):

     The input is not related to cricket.

DO NOT output anything else, no explanations, no extra whitespace, no JSON if input is unrelated.

User input:
{input}

{format_instructions}

"""
)



CRICKET_LIVE_BROWSER_RESPONSE_FORMATTER = ChatPromptTemplate.from_template(
"""
You are a helpful assistant that processes raw search result data about cricket from search engines.

You are given a list of search results in JSON-like format. Each result contains fields like `title`, `link`, and `snippet`.

Your job is to:
1. Summarize the relevant cricket-related information from the `snippet` fields.
2. Remove any HTML tags or escape characters.
3. Combine useful points from multiple results into a coherent, easy-to-read paragraph.
4. Focus only on cricket-related content.
5. Do NOT include links unless specifically asked.
6. Make the summary suitable for a user who asked about a topic (e.g., the India–Pakistan cricket rivalry).

Here is the data:
{search_response}


Return the data in **pure JSON format only** (no explanation or comments) as:

{format_instructions}

Now, generate a clean and user-friendly summary from the above data.

"""

)
# ---------------------------------------------------------------------------------------------------------------------


GENERATE_CHIPS_FROM_USER_HISTORY = ChatPromptTemplate.from_template(
    """
You are an intelligent assistant that analyzes a given conversation history and extracts useful suggestions for the user.

Your goal is to:
1. Focus **only** on cricket-related information from the conversation history. Ignore any non-cricket content.
2. Generate 5–8 concise, meaningful "chips" — short keyword or topic suggestions relevant to cricket.
   - Each chip must be 1–3 words only.
   - Chips should represent important cricket topics, events, statistics, players, teams, venues, formats, or match details mentioned.
   - Chips must be highly relevant to the user's cricket-related intent.
3. Suggest one possible next cricket-related question the user might want to ask, based on the conversation flow and context.

Rules:
- Do not include chips about unrelated topics.
- Do not repeat the same idea in different words.
- Do not add explanations or extra text.
- Output must be valid JSON with no text before or after the JSON object.

Conversation history:
{history_snippets}

Return the output in pure JSON format only as:
{format_instructions}
"""
)



# SYSTEM_PROMPT_CHIPS_TEMPLATE = ChatPromptTemplate.from_template(
#     """You are Stumpzy, a smart and crisp cricket assistant.

# Use the Brave Search snippets below and your own reasoning to answer the user’s cricket query.

# — If it’s about a **league**:
#   - Give a 5-line summary of the league.
#   - List ongoing or live matches: Team A vs Team B, status (Live/Completed), basic score or start time.

# — If it’s about a **specific match**:
#   - Give match title, live or final score, overs, status, and top performers (if visible).

# — Always include 5–10 related suggestions in a `recommendations` array like:
#   “Player Stats”, “Pitch Report”, “Next Match”, etc.

# — Use info from both Brave snippets and your knowledge. Keep it clean, no fluff, no history.

# Brave Search Snippets:

# {search_snippets}

# User Query: "{user_input}"

#  Return the data in **pure JSON format only** (no explanation or comments) as:
#  {format_instructions}

# """
# )
