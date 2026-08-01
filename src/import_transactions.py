from pathlib import Path
import pandas as pd
import os
import pymysql
from dotenv import load_dotenv

# 全局变量
# 根文件路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 数据文件路径
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_sample_1M.csv"
RAW_INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "LI-Small_Trans.csv"
# 环境文件路径
ENV_FILE = PROJECT_ROOT / ".env"

# 全局只加载一次环境变量
load_dotenv(ENV_FILE)


# 加载交易数据
def load_transactions() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, dtype=str)
    df.columns = [
        "transaction_time",
        "from_bank",
        "from_account",
        "to_bank",
        "to_account",
        "amount_received",
        "receiving_currency",
        "amount_paid",
        "payment_currency",
        "payment_format",
        "is_laundering"
    ]
    df['transaction_time'] = pd.to_datetime(df['transaction_time'], format="%Y/%m/%d %H:%M")
    df['is_laundering'] = df['is_laundering'].astype(int)
    return df


# 创建数据库连接
def create_connection() -> pymysql.connections.Connection:

    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    return connection


# 数据插入函数
def insert_transactions(connection,df: pd.DataFrame,batch_size: int = 5000,) -> None:
    insert_sql = """
    INSERT INTO transactions (
        transaction_time,
        from_bank,
        from_account,
        to_bank,
        to_account,
        amount_received,
        receiving_currency,
        amount_paid,
        payment_currency,
        payment_format,
        is_laundering
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """

    connection.begin()  # 开始事务
    try:
        with connection.cursor() as cursor:
            for start in range(0, len(df), batch_size):
                batch = df.iloc[start : start + batch_size]
                records = list(batch.itertuples(index=False, name=None))
                cursor.executemany(insert_sql, records)
                print(f" {start + len(batch)} 条数据已插入数据库中")
        connection.commit()  # 提交事务
    except pymysql.MySQLError as e:
        connection.rollback()  # 回滚事务
        print("MySQL error occurred:", e)
        raise


def main():
    df = load_transactions()
    print(df.head(), df.dtypes, df.shape[0])
    connection = None
    try:
        connection = create_connection()
        insert_transactions(connection, df)
        print("successful")
    except pymysql.MySQLError as e:
        print("MySQL connection failed:", e)
    finally:
        if connection is not None:
            connection.close()

    
if __name__ == "__main__":
    main()