"""
    Databricks SQL connector logic to capture the schema from Unity Catalog
"""
from databricks import sql

def set_connection(server_hostname: str, http_path: str, access_token: str):
    """
        Establishes a connection to a Databricks SQL warehouse.

        :param server_hostname: The Databricks workspace hostname (e.g., 'dbc-1234.cloud.databricks.com').
        :param http_path: The HTTP path of the Databricks SQL warehouse.
        :param access_token: A Databricks personal access token (PAT) for authentication.
        :return: A connection object to the Databricks SQL warehouse.
    """

    connection = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )
    return connection

def get_catalog_metadata(catalog_name:str, connection):
    """
        Retrieves metadata about all schemas, tables, and columns in a specified Unity Catalog catalog.

        For each schema in the catalog, it lists all tables and, for each table, lists its columns
        with data types and descriptions (if available). The results are returned as a formatted string.

        :param catalog_name: The name of the Unity Catalog catalog to query (e.g., 'main', 'my_catalog').
        :param connection: An active Databricks SQL connection object.
        :return: A string containing the formatted metadata hierarchy: schemas → tables → columns.
    """
    cursor = connection.cursor()

    cursor.execute(f"SHOW SCHEMAS IN {catalog_name}")
    schemas = [row[0] for row in cursor.fetchall()]

    result_str = f"Schemas and tables in catalog: {catalog_name}\n"
    for schema in schemas:
        result_str += f"\nSchema: {schema}\n"

        # 2. Get tables in the schema
        cursor.execute(f"SHOW TABLES IN {catalog_name}.{schema}")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table.tableName
            result_str += f"  Table: {table_name}\n"

            # 3. Get column metadata
            cursor.execute(
                f"""
                SELECT column_name, data_type, comment
                FROM {catalog_name}.information_schema.columns
                WHERE table_schema = '{schema}' AND table_name = '{table_name}'
                ORDER BY ordinal_position
                """
            )
            columns = cursor.fetchall()
            for col in columns:
                col_name = col.column_name
                data_type = col.data_type
                comment = col.comment or ""
                result_str += f"    - {col_name} ({data_type}) — {comment}\n"

    # Cleanup
    cursor.close()
    connection.close()

    return result_str