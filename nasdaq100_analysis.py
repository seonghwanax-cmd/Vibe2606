import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_FILE = Path('나스닥 100 과거 데이터.csv')
OUTPUT_PLOT = Path('nasdaq100_closing_price.png')

if not INPUT_FILE.exists():
    raise FileNotFoundError(f'파일을 찾을 수 없습니다: {INPUT_FILE}')

# 1) 데이터 로드 및 컬럼명 정리
raw = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
if len(raw.columns) >= 7:
    raw.columns = ['날짜', '종가', '시가', '고가', '저가', '거래량', '변동 %'] + list(raw.columns[7:])

df = raw[['날짜', '종가', '시가', '고가', '저가', '거래량', '변동 %']].copy()

# 2) 타입 변환 및 아티팩트 제거
for col in ['종가', '시가', '고가', '저가']:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('"', '', regex=False)
        .astype(float)
    )

# 거래량 M/B 처리
vol = df['거래량'].astype(str).str.strip().str.replace(',', '', regex=False)
vol = vol.str.replace('M$', 'e6', regex=True)
vol = vol.str.replace('B$', 'e9', regex=True)
vol = vol.str.replace('K$', 'e3', regex=True)
df['거래량'] = vol.astype(float)

# 변동 % 처리
pct = df['변동 %'].astype(str).str.strip().str.replace('%', '', regex=False)
pct = pct.str.replace(',', '', regex=False)
df['변동 %'] = pct.astype(float) / 100.0

# 날짜 처리
# 날짜 형식이 YYYY- MM- DD 같은 공백을 포함할 수 있으므로 먼저 공백 정리
clean_date = df['날짜'].astype(str).str.replace(' ', '', regex=False)
df['날짜'] = pd.to_datetime(clean_date, format='%Y-%m-%d', errors='coerce')

# 순서 정렬
df = df.sort_values('날짜').reset_index(drop=True)

# 3) 기간 필터링
start = pd.Timestamp('2000-01-01')
end = pd.Timestamp('2019-12-31')
mask = (df['날짜'] >= start) & (df['날짜'] <= end)
df_filtered = df.loc[mask].copy()

print('전체 행 수:', len(df))
print('필터된 행 수 (2000-01-01 ~ 2019-12-31):', len(df_filtered))
print('전체 날짜 범위:', df['날짜'].min(), '~', df['날짜'].max())
if not df_filtered.empty:
    print('필터된 날짜 범위:', df_filtered['날짜'].min(), '~', df_filtered['날짜'].max())
else:
    print('요청한 기간 데이터가 없습니다. 현재 데이터는 2000-2019 범위를 포함하지 않습니다.')

# 4) 분석
analysis_df = df_filtered if not df_filtered.empty else df
analysis_df = analysis_df.set_index('날짜')

if not analysis_df.empty:
    analysis_df['일간수익률'] = analysis_df['종가'].pct_change()
    analysis_df['누적수익률'] = analysis_df['종가'] / analysis_df['종가'].iloc[0] - 1
    rolling = analysis_df['일간수익률'].rolling(window=20)
    analysis_df['20일_변동성'] = rolling.std() * (252 ** 0.5)

    max_drawdown = (analysis_df['종가'] / analysis_df['종가'].cummax() - 1).min()
    total_return = analysis_df['종가'].iloc[-1] / analysis_df['종가'].iloc[0] - 1
    avg_daily = analysis_df['일간수익률'].mean()
    annualized_return = (1 + avg_daily) ** 252 - 1 if not pd.isna(avg_daily) else float('nan')

    print('\n=== 분석 요약 ===')
    print('기간:', analysis_df.index.min().date(), '~', analysis_df.index.max().date())
    print('시작 종가:', analysis_df['종가'].iloc[0])
    print('종료 종가:', analysis_df['종가'].iloc[-1])
    print('총 수익률:', f'{total_return:.2%}')
    print('연환산 수익률(근사):', f'{annualized_return:.2%}')
    print('최대 낙폭:', f'{max_drawdown:.2%}')
    print('평균 일일 수익률:', f'{avg_daily:.4%}')
    print('평균 거래량:', f'{analysis_df["거래량"].mean():,.0f}')

    # 연간 수익률 간단 분석
    yearly = analysis_df['종가'].resample('YE').last().pct_change()
    print('\n연도별 마지막 거래일 기준 수익률:')
    print(yearly.dropna().apply(lambda x: f'{x:.2%}'))

    # 5) 종가 라인 그래프
    plt.figure(figsize=(12, 6))
    plt.plot(analysis_df.index, analysis_df['종가'], label='NASDAQ 100 Close')
    plt.title('NASDAQ 100 Close Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.legend()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    print(f'그래프 저장 완료: {OUTPUT_PLOT}')
else:
    print('분석할 데이터가 없습니다.')
