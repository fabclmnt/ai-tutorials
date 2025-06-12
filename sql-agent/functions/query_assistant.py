"""
    File that defines the functionality for our Unity Catalog metadata assistant agent.
"""
from pydantic import BaseModel
from pydantic_ai.agent import Agent
from pydantic_ai.messages import ModelResponse, TextPart


# ==== Output schema ====
class CatalogQuery(BaseModel):
    code: str


# ==== System prompt ====
system_prompt = (
    """
        You are a SQL assistant specialized in Databricks Unity Catalog.
    
        You help users write SQL queries to explore their data based on the provided metadata.
    
        You have access to the following metadata summary:
        {summary}
    
        Users will ask natural language questions about the actual data stored in these tables.
    
        Always respond in valid JSON with exactly one field:
        - code: (string) — the SQL query that answers the user's question.
    
        Do not include any explanations, markdown, comments, or text outside the JSON.
    
        Assume table and column names are case-sensitive and fully qualified using the format: catalog.schema.table.
    
        Examples:
    
        Question:
        What is the average order value per month?
    
        Response:
        {{
          code: SELECT DATE_TRUNC(`month`, order_date) AS month, AVG(order_value) AS avg_order_value FROM main.sales.orders GROUP BY month ORDER BY month
        }}
    
        Question:
        How many users signed up last year?
    
        Response:
        {{
          "code": SELECT COUNT(*) FROM main.crm.users WHERE signup_date BETWEEN `2023-01-01` AND `2023-12-31`
        }}
    """
)

# ==== Assistant prompt format ====
assistant_prompt = (
    """
    <<QUESTION>>: {question}
    """
)

# ==== Agent Factory ====
def catalog_metadata_agent(system_prompt: str, model: str="openai:gpt-4o") -> Agent:
    return Agent(
        model=model,
        system_prompt=system_prompt,
        output_type=CatalogQuery,
        instrument=True
    )

# ==== Response Adapter ====
def to_model_response(output: CatalogQuery, timestamp: str) -> ModelResponse:
    return ModelResponse(
        parts=[TextPart(f"```sql\n{output.code}\n```")],
        timestamp=timestamp
    )