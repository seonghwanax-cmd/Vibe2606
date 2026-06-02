import sys
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager


def find_font():
    # Windows 기본 한글 폰트 우선 사용
    candidates = ["Malgun Gothic", "Microsoft YaHei", "AppleGothic", "NanumGothic"]
    for f in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
        name = font_manager.FontProperties(fname=f).get_name()
        if name in candidates:
            return name
    return None


def load_and_clean(path: Path) -> pd.DataFrame:
    # 엑셀 로드
    df = pd.read_excel(path, engine='openpyxl')

    # 컬럼명 정리(양쪽 공백 제거)
    df.columns = [str(c).strip() for c in df.columns]

    # 워이드 포맷(열이 연도인 경우) 확인: 컬럼명이 4자리 연도인 항목이 많으면 워이드로 판단
    year_cols = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    if len(year_cols) >= 5:
        # 첫 번째 컬럼에 지표명이 있음(예: '기본항목별')
        id_col = df.columns[0]
        # 출생아수 관련 행 찾기
        birth_row = df[df[id_col].astype(str).str.contains('출생', na=False)].iloc[0]
        # 연도별 값 추출
        data = []
        for yc in year_cols:
            y = int(yc)
            val = birth_row[yc]
            try:
                val = float(str(val).replace(',', '').strip())
            except Exception:
                val = pd.NA
            data.append({'Year': y, 'Births': val})
        out = pd.DataFrame(data)
        out = out.dropna(subset=['Births'])
        out = out[(out['Year'] >= 1970) & (out['Year'] <= 2024)]
        out = out.sort_values('Year').reset_index(drop=True)
        return out

    # 롱 포맷 처리 (기존 로직)
    # 연도 컬럼 자동 탐지: '년' 포함 또는 'Year' 또는 숫자형 값이 연속된 컬럼
    year_col = None
    for col in df.columns:
        if '년' in col or re.search(r'year|Year', col):
            year_col = col
            break
    if year_col is None:
        # 숫자형으로 변환 가능한 컬럼 중 값이 1900~2050 범위가 많은 컬럼 선택
        for col in df.columns:
            try:
                nums = pd.to_numeric(df[col], errors='coerce')
                valid = nums.dropna().between(1900, 2050)
                if valid.sum() >= 5:
                    year_col = col
                    break
            except Exception:
                continue
    if year_col is None:
        raise RuntimeError('연도 컬럼을 자동으로 찾지 못했습니다. 컬럼명을 확인하세요.')

    # 출생아수 컬럼 자동 탐지: '출생' 또는 '출생아' 포함하거나 숫자형 컬럼 중 합계로 보이는 컬럼
    births_col = None
    for col in df.columns:
        if '출생' in col or '출생아' in col or '출생아수' in col:
            births_col = col
            break
    if births_col is None:
        # 숫자형으로 변환 가능한 컬럼 중 결측이 적고 값 범위가 현실적인(0~1e7) 컬럼 찾기
        candidates = []
        for col in df.columns:
            nums = pd.to_numeric(df[col], errors='coerce')
            if nums.dropna().between(0, 10_000_000).sum() >= 5:
                candidates.append((col, nums.dropna().count()))
        if candidates:
            candidates.sort(key=lambda x: -x[1])
            births_col = candidates[0][0]
    if births_col is None:
        raise RuntimeError('출생아수 컬럼을 자동으로 찾지 못했습니다. 컬럼명을 확인하세요.')

    # 연도 컬럼 정수형으로 변환
    df['Year'] = pd.to_numeric(df[year_col].astype(str).str.extract(r'(\d{4})')[0], errors='coerce').astype('Int64')

    # 출생아수 숫자형으로 변환 (콤마 제거 등)
    df['Births'] = pd.to_numeric(df[births_col].astype(str).str.replace(',', '').str.replace('\s+', '', regex=True), errors='coerce')

    # 필요한 연도 범위만 사용
    df = df.dropna(subset=['Year'])
    df = df[(df['Year'] >= 1970) & (df['Year'] <= 2024)]

    # 연도별 집계: 같은 연도가 여러 행이면 합계로 처리(하지만 보통 한 행임)
    df = df.groupby('Year', as_index=False)['Births'].sum()

    # 정렬
    df = df.sort_values('Year').reset_index(drop=True)

    return df


def plot_births(df: pd.DataFrame, out_path: Path = None):
    font_name = find_font()
    if font_name:
        plt.rc('font', family=font_name)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Year'], df['Births'], marker='o', linewidth=2)
    ax.set_title('연도별 출생아수 (1970-2024)')
    ax.set_xlabel('연도')
    ax.set_ylabel('출생아수 (명)')
    ax.grid(True, linestyle='--', alpha=0.6)

    # x축 눈금: 5년 단위 라벨링
    years = df['Year'].tolist()
    ax.set_xticks([y for y in years if (y % 5 == 0)])

    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=150)
        print(f'그래프를 저장했습니다: {out_path}')
    else:
        plt.show()


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) >= 1:
        file_path = Path(argv[0])
    else:
        file_path = Path('출생아수__합계출산율__자연증가_등_20260602141801.xlsx')

    if not file_path.exists():
        print(f'파일을 찾을 수 없습니다: {file_path}\n경로가 현재 작업 디렉터리에 있는지 확인하세요.')
        return

    df = load_and_clean(file_path)
    print('데이터 샘플:')
    print(df.head())

    out_img = Path('births_1970_2024.png')
    plot_births(df, out_img)


if __name__ == '__main__':
    main()
