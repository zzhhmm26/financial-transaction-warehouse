from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "LI-Small_Trans.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_sample_1M.csv"
SAMPLE_SIZE = 1_000_000


def create_sample() -> None:
    """Create a fixed development sample from the raw transaction file."""
    # TODO 1: 使用 Pandas 读取 INPUT_PATH 的前 SAMPLE_SIZE 行。
    # 提示：read_csv 有一个参数可以限制读取行数。
    df = pd.read_csv(INPUT_PATH,nrows = SAMPLE_SIZE,dtype = str)
    # TODO 2: 检查读取结果是否恰好包含 SAMPLE_SIZE 行。
    if not df.shape[0] == SAMPLE_SIZE:
        raise ValueError("行数错误")
    # TODO 3: 确保 OUTPUT_PATH 的父目录存在。
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # TODO 4: 保存 CSV，不要额外写入 DataFrame 索引列。
    df.to_csv(OUTPUT_PATH,index = False)
    # TODO 5: 打印实际数据行数和输出路径。
    print(f"行数：{df.shape[0]},输出路径：{OUTPUT_PATH}")


if __name__ == "__main__":
    create_sample()
