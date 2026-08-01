from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "figures"

LARGE_RESULT_PATH = PROJECT_ROOT / "大额交易与洗钱关系.csv"
HIGH_FREQUENCY_PATH = PROJECT_ROOT / "高频交易与洗钱率.csv"
SENSITIVITY_PATH = PROJECT_ROOT / "末端敏感性分析.csv"

BLUE = "#4C78A8"
RED = "#D65F5F"
LIGHT_BLUE = "#9EC1E6"
LIGHT_RED = "#E8A1A1"
TEXT = "#243447"
GRID = "#DCE3EA"
BACKGROUND = "#F7F9FC"


def configure_style() -> None:
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    for font_name in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC"):
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name]
            break

    plt.rcParams.update(
        {
            "axes.unicode_minus": False,
            "axes.edgecolor": GRID,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": TEXT,
            "figure.facecolor": BACKGROUND,
            "axes.facecolor": "white",
            "font.size": 11,
        }
    )


def load_results() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    large = pd.read_csv(LARGE_RESULT_PATH)
    high_frequency = pd.read_csv(HIGH_FREQUENCY_PATH).rename(
        columns={
            "交易总数": "transaction_count",
            "洗钱交易数": "laundering_count",
            "洗钱率%": "laundering_rate_pct",
        }
    )
    sensitivity = pd.read_csv(SENSITIVITY_PATH)

    large = large.set_index("amount_type").loc[["other", "large"]].reset_index()
    high_frequency = (
        high_frequency.set_index("frequency_type")
        .loc[["other", "high_frequency"]]
        .reset_index()
    )
    sensitivity = (
        sensitivity.set_index("frequency_type")
        .loc[["other", "high_frequency"]]
        .reset_index()
    )
    return large, high_frequency, sensitivity


def style_axis(axis: plt.Axes, y_limit: float) -> None:
    axis.set_ylim(0, y_limit)
    axis.set_ylabel("洗钱率（%）")
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0, colors="#607080")
    axis.tick_params(axis="x", length=0, colors=TEXT)


def add_value_labels(axis: plt.Axes, bars, digits: int = 4) -> None:
    for bar in bars:
        value = bar.get_height()
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.{digits}f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color=TEXT,
        )


def plot_two_group_chart(
    values: list[float],
    labels: list[str],
    colors: list[str],
    title: str,
    subtitle: str,
    output_name: str,
    digits: int = 4,
) -> None:
    figure, axis = plt.subplots(figsize=(8.2, 5.4))
    bars = axis.bar(labels, values, width=0.55, color=colors)
    style_axis(axis, max(values) * 1.35)
    add_value_labels(axis, bars, digits)
    axis.set_title(title, loc="left", fontsize=16, fontweight="bold", pad=22)
    axis.text(
        0,
        1.02,
        subtitle,
        transform=axis.transAxes,
        color="#607080",
        fontsize=10,
        va="bottom",
    )
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / output_name, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_sensitivity_chart(
    high_frequency: pd.DataFrame, sensitivity: pd.DataFrame
) -> None:
    periods = ["9月1日至10日", "全部日期"]
    other_values = [
        high_frequency.loc[0, "laundering_rate_pct"],
        sensitivity.loc[0, "laundering_rate_pct"],
    ]
    high_values = [
        high_frequency.loc[1, "laundering_rate_pct"],
        sensitivity.loc[1, "laundering_rate_pct"],
    ]

    figure, axis = plt.subplots(figsize=(8.6, 5.4))
    positions = [0, 1]
    width = 0.32
    other_bars = axis.bar(
        [position - width / 2 for position in positions],
        other_values,
        width=width,
        color=LIGHT_BLUE,
        label="普通组",
    )
    high_bars = axis.bar(
        [position + width / 2 for position in positions],
        high_values,
        width=width,
        color=RED,
        label="高频组",
    )
    axis.set_xticks(positions, periods)
    style_axis(axis, max(high_values) * 1.35)
    add_value_labels(axis, other_bars)
    add_value_labels(axis, high_bars)
    axis.set_title(
        "加入异常尾部后，高频交易结论仍然稳定",
        loc="left",
        fontsize=16,
        fontweight="bold",
        pad=22,
    )
    axis.text(
        0,
        1.02,
        "全日期仅使两组洗钱率小幅上升，高频组仍约为普通组的 2.3 倍",
        transform=axis.transAxes,
        color="#607080",
        fontsize=10,
        va="bottom",
    )
    axis.legend(frameon=False, ncols=2, loc="upper left")
    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "sensitivity_analysis.png", dpi=220, bbox_inches="tight"
    )
    plt.close(figure)


def plot_summary_dashboard(
    large: pd.DataFrame,
    high_frequency: pd.DataFrame,
    sensitivity: pd.DataFrame,
) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(17, 5.8))

    large_values = large["laundering_rate_pct"].tolist()
    large_ratio = large_values[1] / large_values[0]
    large_bars = axes[0].bar(
        ["其他交易", "大额交易"], large_values, color=[LIGHT_BLUE, RED], width=0.58
    )
    style_axis(axes[0], max(large_values) * 1.38)
    add_value_labels(axes[0], large_bars, digits=3)
    axes[0].set_title(
        f"大额交易组约为其他交易的 {large_ratio:.2f} 倍",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axes[0].text(
        0,
        1.01,
        "基于100万条样本",
        transform=axes[0].transAxes,
        color="#607080",
        fontsize=9,
    )

    high_values = high_frequency["laundering_rate_pct"].tolist()
    high_ratio = high_values[1] / high_values[0]
    high_bars = axes[1].bar(
        ["普通组", "高频组"], high_values, color=[LIGHT_BLUE, RED], width=0.58
    )
    style_axis(axes[1], max(high_values) * 1.38)
    add_value_labels(axes[1], high_bars)
    axes[1].set_title(
        f"高频组约为普通组的 {high_ratio:.2f} 倍",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axes[1].text(
        0,
        1.01,
        "高频定义：每日交易次数前1%的账户日",
        transform=axes[1].transAxes,
        color="#607080",
        fontsize=9,
    )

    periods = ["9月1日至10日", "全部日期"]
    positions = [0, 1]
    width = 0.32
    other_values = [
        high_frequency.loc[0, "laundering_rate_pct"],
        sensitivity.loc[0, "laundering_rate_pct"],
    ]
    sensitivity_high_values = [
        high_frequency.loc[1, "laundering_rate_pct"],
        sensitivity.loc[1, "laundering_rate_pct"],
    ]
    other_bars = axes[2].bar(
        [position - width / 2 for position in positions],
        other_values,
        width=width,
        color=LIGHT_BLUE,
        label="普通组",
    )
    high_bars = axes[2].bar(
        [position + width / 2 for position in positions],
        sensitivity_high_values,
        width=width,
        color=RED,
        label="高频组",
    )
    axes[2].set_xticks(positions, periods)
    style_axis(axes[2], max(sensitivity_high_values) * 1.38)
    add_value_labels(axes[2], other_bars)
    add_value_labels(axes[2], high_bars)
    axes[2].set_title(
        "异常尾部不改变主要结论",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axes[2].text(
        0,
        1.01,
        "敏感性分析",
        transform=axes[2].transAxes,
        color="#607080",
        fontsize=9,
    )
    axes[2].legend(frameon=False, ncols=2, loc="upper left")

    figure.suptitle(
        "AML交易风险特征分析",
        x=0.04,
        y=1.02,
        ha="left",
        fontsize=20,
        fontweight="bold",
        color=TEXT,
    )
    figure.text(
        0.04,
        0.01,
        "注：洗钱率均为交易层面的标签比例；数据为合成AML数据，结果表示关联而非因果。",
        color="#607080",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.02, 0.05, 1, 0.96), w_pad=2.6)
    figure.savefig(
        OUTPUT_DIR / "aml_risk_summary.png", dpi=220, bbox_inches="tight"
    )
    plt.close(figure)


def main() -> None:
    configure_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    large, high_frequency, sensitivity = load_results()

    large_values = large["laundering_rate_pct"].tolist()
    large_ratio = large_values[1] / large_values[0]
    plot_two_group_chart(
        large_values,
        ["其他交易", "大额交易"],
        [LIGHT_BLUE, RED],
        f"大额交易组洗钱率约为其他交易的 {large_ratio:.2f} 倍",
        "各货币内部按交易金额排名前1%定义为大额交易；结果基于100万条样本",
        "large_transaction_risk.png",
        digits=3,
    )

    high_values = high_frequency["laundering_rate_pct"].tolist()
    high_ratio = high_values[1] / high_values[0]
    plot_two_group_chart(
        high_values,
        ["普通账户日", "高频账户日"],
        [LIGHT_BLUE, RED],
        f"高频组洗钱率约为普通组的 {high_ratio:.2f} 倍",
        "高频定义：每日交易次数排名前1%的账户日；分析范围为9月1日至10日",
        "high_frequency_risk.png",
    )

    plot_sensitivity_chart(high_frequency, sensitivity)
    plot_summary_dashboard(large, high_frequency, sensitivity)
    print(f"图表已保存至：{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
