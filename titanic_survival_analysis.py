import pandas as pd
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "sans-serif"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
import seaborn as sns


def load_titanic_data() -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    try:
        df = pd.read_csv(url)
        print("Loaded Titanic dataset from web URL.")
        return df
    except Exception as e:
        print(f"웹에서 데이터 로드 실패: {e}")
        print("seaborn 라이브러리에서 titanic 데이터셋을 로드합니다.")
        df = sns.load_dataset("titanic")
        return df


def analyze_survival_by_sex(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={col: col.lower() for col in df.columns})

    if "sex" not in df.columns or "survived" not in df.columns:
        raise ValueError("데이터셋에 'sex' 또는 'survived' 열이 없습니다.")

    grouped = df.groupby("sex")["survived"].agg(total="count", survivors="sum")
    grouped["survival_rate"] = grouped["survivors"] / grouped["total"] * 100
    return grouped.reset_index()


def plot_survival_rate(df: pd.DataFrame):
    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 6))

    colors = {"female": "#1f77b4", "male": "#ff7f0e"}
    bars = plt.bar(
        df["sex"],
        df["survival_rate"],
        color=[colors.get(value, "#1f77b4") for value in df["sex"]],
        edgecolor="black",
    )

    plt.title("타이타닉 성별 생존 비율")
    plt.xlabel("성별")
    plt.ylabel("생존 비율 (%)")
    plt.ylim(0, 100)

    for bar in bars:
        height = bar.get_height()
        plt.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            color="black",
        )

    plt.tight_layout()
    output_path = "titanic_survival_ratio.png"
    plt.savefig(output_path, dpi=150)
    print(f"차트를 '{output_path}' 파일로 저장했습니다.")


def main():
    df = load_titanic_data()
    summary = analyze_survival_by_sex(df)

    print("--- 타이타닉 성별 생존 요약 ---")
    print(summary.to_string(index=False))

    plot_survival_rate(summary)


if __name__ == "__main__":
    main()
