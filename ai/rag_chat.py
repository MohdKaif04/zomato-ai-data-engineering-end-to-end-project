import os
import time
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-flash-latest"
NEW_REVIEWS = 500
TOP_K = 5
CACHE_FILE = "review_embeddings.parquet"

# The free-tier embedding quota allows only a handful of requests per
# MINUTE (much stricter than it sounds), regardless of how many texts
# each request contains. So the fix has two parts:
#   1) Make batches as large as the API allows, to minimize request COUNT.
#   2) Deliberately pace those requests well below the per-minute limit.
EMBED_BATCH_SIZE = 100
SECONDS_BETWEEN_BATCHES = 12  # keeps us under ~5 requests/minute
MAX_RETRIES = 6

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)


def read_reviews_from_snowflake():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = f"""
        SELECT REVIEW_ID, CITY, RATING, COMMENT
        FROM ZOMATO.STAGING.STG_REVIEWS
        SAMPLE ({NEW_REVIEWS} ROWS)
    """
    df = conn.cursor().execute(query).fetch_pandas_all()
    conn.close()

    df.columns = [col.lower() for col in df.columns]
    return df


def _embed_batch_with_retry(batch):
    """Call embed_content for one batch, retrying with exponential
    backoff if we hit a 429 RESOURCE_EXHAUSTED quota error."""
    delay = 15  # start higher since the embedding RPM limit is very low
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch
            )
            return [e.values for e in response.embeddings]
        except genai_errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < MAX_RETRIES - 1:
                st.warning(
                    f"Rate limit hit, waiting {delay}s before retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES})..."
                )
                time.sleep(delay)
                delay *= 2  # exponential backoff
            else:
                raise


def embed(texts):
    """Embed a list of texts using the Gemini embedding model, in batches.

    NOTE: the correct call is client.models.embed_content(...), NOT
    client.embeddings.create(...) (that is the OpenAI SDK style, which
    does not exist on the google-genai Client).

    IMPORTANT: embed_content accepts a LIST of texts in `contents`, so we
    batch many reviews into one request instead of one request per
    review. This is what avoids the 429 RESOURCE_EXHAUSTED quota error
    (free tier caps you at ~100 requests/minute, not 100 texts/minute).
    """
    embeddings = []
    total_batches = (len(texts) - 1) // EMBED_BATCH_SIZE + 1
    progress = st.progress(0.0, text="Embedding reviews...")

    for batch_num, i in enumerate(range(0, len(texts), EMBED_BATCH_SIZE)):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        embeddings.extend(_embed_batch_with_retry(batch))
        progress.progress(
            (batch_num + 1) / total_batches,
            text=f"Embedded batch {batch_num + 1}/{total_batches}"
        )
        # Deliberate pause between batches — this is what actually keeps
        # us under the free-tier requests-per-minute limit. Skip the
        # wait after the very last batch.
        if batch_num + 1 < total_batches:
            time.sleep(SECONDS_BETWEEN_BATCHES)

    progress.empty()
    return embeddings


@st.cache_data()
def load_reviews():
    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)

    df = read_reviews_from_snowflake()
    df['embedding'] = embed(df['comment'].tolist())
    df.to_parquet(CACHE_FILE)
    return df


st.title("Chat with your Zomato Reviews")
st.caption(f"Searching {NEW_REVIEWS} reviews, answering with {CHAT_MODEL} model")


def cosine_similarity(vec_a, vec_b):
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))


def find_similar_reviews(question, df):
    question_vector = embed([question])[0]

    scores = []
    for review_vector in df['embedding']:
        scores.append(cosine_similarity(question_vector, review_vector))

    df = df.copy()
    df['score'] = scores
    return df.nlargest(TOP_K, 'score')


def ask_llm(question, top_reviews):
    context = ""

    for _, row in top_reviews.iterrows():
        context += f" ({row['city']}, {row['rating']} stars) {row['comment']}\n"

    system_prompt = (
        "Answer ONLY using the customer reviews provided. "
        "Be concise. If the reviews don't cover it, say so."
    )

    user_prompt = f"Question: {question}\n\nReviews:\n{context}"

    # google-genai does not expose an OpenAI-style
    # client.chat.completions.create(...) method. The correct call for
    # Gemini text generation is client.models.generate_content(...).
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
        ],
        config={"temperature": 0.2},
    )
    return response.text


review_df = load_reviews()

question = st.text_input(
    "Ask a question about your reviews:",
    placeholder="e.g. What are the most common complaints about delivery?"
)

if question:
    top_reviews = find_similar_reviews(question, review_df)
    answer = ask_llm(question, top_reviews)

    st.markdown("**Answer:**")
    st.write(answer)

    with st.expander("Reviews used to build this answer"):
        st.dataframe(top_reviews[['city', 'rating', 'comment']], hide_index=True)