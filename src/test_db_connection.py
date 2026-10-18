import psycopg

# Connect to the PostgreSQL database running on your laptop.
with psycopg.connect(
    dbname="f1_telemetry",
    user="postgres",
    host="localhost"
) as conn:

    # Create a cursor to execute SQL commands.
    with conn.cursor() as cur:

        # Ask PostgreSQL which database we're connected to.
        cur.execute("SELECT current_database();")

        # Retrieve the first row returned by the query.
        result = cur.fetchone()

        # Display the database name to verify the connection.
        print(f"Connected to database: {result[0]}")