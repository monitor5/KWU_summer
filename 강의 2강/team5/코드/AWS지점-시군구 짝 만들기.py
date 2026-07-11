import csv
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set, Tuple

DATA_DIR = Path("../data")

def load_town() -> Set[str]:
    """KOSIS 파일 → (코드, 행정구역명) 집합"""
    town = set()
    with open(DATA_DIR / "KOSIS/시군구 인구 통계.csv", encoding="utf8") as f:
        rdr = csv.reader(f)
        next(rdr); next(rdr)
        for name, *_ in rdr:
            town.add(name.strip())
    return town


def load_spot() -> Tuple[Set[str], dict[str, int]]:
    """AWS 파일 → (코드, 지점명) 집합"""
    spot, spot_code_dict = set(), dict()
    with open(DATA_DIR / "AWS/20211215_20220615.csv", encoding="utf8") as f:
        rdr = csv.reader(f)
        next(rdr)      # header skip
        for code, name, *_ in rdr:   # ← 파일 구조에 맞게 index 조정
            spot.add(name.strip())
            spot_code_dict[name.strip()] = int(code.strip())
    return spot, spot_code_dict


def fetch_admin(code: int) -> list[str] | None:
    """기상청 팝업에서 새주소 → '○○시/군/구' 한 개 추출"""
    print(f"fetch Start, {code}")
    url = "https://data.kma.go.kr/cmmn/stnDetailPopup.do"
    try:
        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "text/html, */*; q=0.01",
            },
            data={"stnId": code},
            timeout=120,
        )
    except:
        print('time out!')
        return None
    print(f"fetch Done, {code}")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    th = soup.find("th", string="새주소")
    if not th:
        return None
    addr = th.find_next_sibling("td").get_text(strip=True)
    match = re.findall(r"[가-힣]+[시군구]", addr)
    return match if match else None


def main() -> None:
    town = load_town()
    spot, spot_code_dict = load_spot()

    matched = [(spot_code_dict[i], i) for i in spot & town]
    print(f"일치: {len(matched)}개")

    # 불일치 집합
    spot_only = spot - town
    spot_only_with_code= [(spot_code_dict[i], i) for i in spot_only]
    #town_only = town - spot

    not_matched: set[Tuple[int, str]] = set()

    # 관측소 기준으로만 순회 (town_only는 코드 — 지점명이 없을 수 있으므로 제외)
    for code, wrong_name in spot_only_with_code:
        admins = fetch_admin(code)
        if not admins:
            not_matched.add((code, wrong_name))
            continue

        saved = None                   # 실제로 저장할 행정구역명

        for admin in admins:
            candidate = admin

            # 1️⃣ '00구'만 나올 때 ⇒ '상위00시-00구' 만들기
            if admin.endswith("구"):
                parent = next(
                    (a for a in admins if a.endswith("시")), None
                )
                if parent:
                    candidate = f"{parent}-{admin}"

            # 2️⃣ town 세트에 있으면 매칭 성공
            if admin in town:
                matched.append((code, candidate))
                saved = candidate
                break

        # 3️⃣ 끝까지 못 찾으면 불일치로 기록
        if not saved:
            # (원래 이름)→(마지막 시도한 candidate) 형태로 저장
            not_matched.add((code, f"{wrong_name}→{candidate}"))

    # 결과
    print(f"추가 매칭 후 총 일치: {len(matched)}개")
    print(f"여전히 불일치: {len(not_matched)}개")
    with open('../data/aws/matched.txt', 'w', encoding='utf8') as f:
        f.write("{\n")
        for i, j in matched:
            f.write(f"{i}: '{j}',")
        f.write("}")
    with open('../data/aws/not_matched.txt', 'w', encoding='utf8') as f:
        f.write("{\n")
        for i, j in not_matched:
            f.write(f"{i}: '{j}',")
        f.write("}")

if __name__ == "__main__":
    main()