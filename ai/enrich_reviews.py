import os
import json
import snowflake.connector
from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-flash-latest"
SAMPLE_N = 5

TOPICS = [
    "food quality",
    "delivery",
    "pricing",
    "service",
    "packaging",
    "other",
]

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)

SYSTEM_PROMPT = f"""
You classify customer reviews for a food delivery app.

Return ONLY valid JSON.

Schema:

{{
  "sentiment_label":"positive|negative|neutral",
  "sentiment_score":0.95,
  "topic":"one of {TOPICS}",
  "key_issue":"string or null"
}}

Rules:
- No markdown
- No explanation
- Return ONLY JSON
"""


def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def create_output_table(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS ZOMATO.AI")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ZOMATO.AI.REVIEW_ENRICHED(
        REVIEW_ID STRING,
        SENTIMENT_LABEL STRING,
        SENTIMENT_SCORE FLOAT,
        TOPIC STRING,
        KEY_ISSUE STRING,
        MODEL STRING,
        ENRICHED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """)


def get_reviews_to_enrich(cursor):
    cursor.execute(f"""
        SELECT REVIEW_ID, COMMENT
        FROM ZOMATO.RAW.REVIEWS
        WHERE REVIEW_ID NOT IN
        (
            SELECT REVIEW_ID
            FROM ZOMATO.AI.REVIEW_ENRICHED
        )
        LIMIT {SAMPLE_N}
    """)

    return cursor.fetchall()


def classify_review(comment):

    prompt = f"""
{SYSTEM_PROMPT}

Review:

{comment}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    if response.text is None:
        raise Exception("Empty response from Gemini")

    answer = response.text.strip()

    if answer.startswith("```json"):
        answer = answer.replace("```json", "")

    if answer.startswith("```"):
        answer = answer.replace("```", "")

    if answer.endswith("```"):
        answer = answer[:-3]

    answer = answer.strip()

    return json.loads(answer)


def save_results(cursor, results):

    print(f"Saving {len(results)} enriched reviews...")

    cursor.executemany(
        """
        INSERT INTO ZOMATO.AI.REVIEW_ENRICHED
        (
            REVIEW_ID,
            SENTIMENT_LABEL,
            SENTIMENT_SCORE,
            TOPIC,
            KEY_ISSUE,
            MODEL
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
        """,
        results,
    )


def main():

    conn = get_connection()
    cursor = conn.cursor()

    create_output_table(cursor)

    reviews = get_reviews_to_enrich(cursor)

    if len(reviews) == 0:
        print("No new reviews found.")
        return

    print(f"Enriching {len(reviews)} reviews...")

    results = []

    for review_id, comment in reviews:

        print(f"Review {review_id}: {comment}")

        try:

            labels = classify_review(comment)

            print(labels)

            results.append(
                (
                    review_id,
                    labels["sentiment_label"],
                    float(labels["sentiment_score"]),
                    labels["topic"],
                    labels["key_issue"],
                    MODEL,
                )
            )

        except Exception as e:

            print(f"Review {review_id} failed")
            print(e)

    save_results(cursor, results)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Inserted {len(results)} rows.")


if __name__ == "__main__":
    main()