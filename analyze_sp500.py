import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def clean_and_load(path):
    df = pd.read_csv(path, encoding='utf-8-sig')
    # 표제 한글 -> 영문 컬럼
    df = df.rename(columns={
        '날짜': 'Date', '종가': 'Close', '시가': 'Open', '고가': 'High', '저가': 'Low', '거래량': 'Volume', '변동 %': 'Change%'
    })
    # 날짜 문자열의 공백 제거 (e.g. '2019- 11- 14' -> '2019-11-14')
    df['Date'] = df['Date'].astype(str).str.replace(' ', '')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')

    # 숫자형 컬럼 정리: 쉼표 제거, 퍼센트 기호 제거
    for col in ['Close', 'Open', 'High', 'Low']:
        df[col] = df[col].astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Change%' in df.columns:
        df['Change%'] = df['Change%'].astype(str).str.replace('%', '').str.replace(',', '')
        df['Change%'] = pd.to_numeric(df['Change%'], errors='coerce')

    # 거래량은 비어있을 수 있음
    if 'Volume' in df.columns:
        df['Volume'] = df['Volume'].astype(str).str.replace(',', '')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

    # 날짜를 인덱스로 설정하고 과거->현재 순으로 정렬
    df = df.dropna(subset=['Date'])
    df = df.set_index('Date')
    df = df.sort_index()
    return df


def analyze(df, start='2000-01-01', end='2019-12-31'):
    df = df.loc[start:end].copy()
    df = df.dropna(subset=['Close'])

    # 수익률
    df['DailyReturn'] = df['Close'].pct_change()
    total_return = df['Close'].iloc[-1] / df['Close'].iloc[0] - 1
    years = (df.index[-1] - df.index[0]).days / 365.25
    cagr = (df['Close'].iloc[-1] / df['Close'].iloc[0]) ** (1 / years) - 1
    ann_vol = df['DailyReturn'].std() * np.sqrt(252)

    # 연간 수익률
    annual = df['Close'].resample('Y').last().pct_change().dropna()

    # 최대 낙폭
    running_max = df['Close'].cummax()
    drawdown = df['Close'] / running_max - 1
    max_drawdown = drawdown.min()

    # 이동평균
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    summary = {
        'start': str(df.index[0].date()),
        'end': str(df.index[-1].date()),
        'observations': len(df),
        'total_return': float(total_return),
        'cagr': float(cagr),
        'annualized_volatility': float(ann_vol),
        'max_drawdown': float(max_drawdown)
    }

    return df, summary, annual, drawdown


def plot_close_with_ma(df, out_path):
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['Close'], label='Close', color='black')
    if 'MA50' in df.columns:
        ax.plot(df.index, df['MA50'], label='MA50', color='tab:blue', linewidth=1)
    if 'MA200' in df.columns:
        ax.plot(df.index, df['MA200'], label='MA200', color='tab:orange', linewidth=1)
    ax.set_title('S&P500 Close (2000-2019)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close')
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main():
    base = os.path.dirname(__file__)
    csv_path = os.path.join(base, 'S&P 500 과거 데이터.csv')
    out_dir = os.path.join(base, 'analysis_outputs')
    os.makedirs(out_dir, exist_ok=True)

    df = clean_and_load(csv_path)
    df_period, summary, annual, drawdown = analyze(df, start='2000-01-01', end='2019-12-31')

    # 저장
    df_period.to_csv(os.path.join(out_dir, 'sp500_2000_2019_cleaned.csv'))
    pd.Series(summary).to_csv(os.path.join(out_dir, 'sp500_summary_2000_2019.csv'))
    annual.to_csv(os.path.join(out_dir, 'sp500_annual_returns_2000_2019.csv'))
    drawdown.to_csv(os.path.join(out_dir, 'sp500_drawdown_2000_2019.csv'))

    fig_path = os.path.join(out_dir, 'sp500_close_ma_2000_2019.png')
    plot_close_with_ma(df_period, fig_path)

    # 콘솔 출력
    print('Summary:')
    for k, v in summary.items():
        print(f'{k}: {v}')
    print('\nAnnual returns:')
    print(annual)
    print('\nPlot saved to:', fig_path)


if __name__ == '__main__':
    main()
