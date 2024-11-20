# SQL-Qry-Analyzer

A desktop application built with Python and PyQt that allows users to execute SQL queries against an Azure SQL Database. The application compares the results of consecutive queries and provides a side-by-side analysis of differences in execution time, the number of records returned, and row/column values.

## Features

- Execute SQL queries against an Azure SQL Database
- Display query results in a readable format
- Show execution time and the number of records returned
- Compare consecutive query results side-by-side
- Display differences in row and column values

## Requirements

- Python 3.6 or higher
- PyQt5
- pyodbc
- pandas
- SQL Server ODBC Driver 17

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/sql-query-executor.git
    cd sql-query-executor
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Add your Azure SQL Database connection details:**
    Open the `app.py` file and update the following line with your connection details:
    ```python
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=your_database_name;UID=your_username;PWD=your_password')
    ```

## Usage

1. **Run the application:**
    ```sh
    python app.py
    ```

2. **Enter your SQL query:**
    - Type your SQL query in the input text box.

3. **Execute the query:**
    - Click the "Execute" button to run the query against the Azure SQL Database.

4. **View the results:**
    - The query results will be displayed in the result display area.
    - Execution time and the number of records returned will be shown below the results.
    - If a previous query was executed, differences in row/column values will be displayed side-by-side in the analysis section.

## Example

```sql
SELECT * FROM your_table_name WHERE column_name = 'value'
