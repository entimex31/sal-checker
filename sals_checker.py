import requests
from itertools import combinations

# =========================================
# 설정
# =========================================

API_KEY = "4ccc49c1c9cf932dd19428e0d802dbcad1b6731451072e257579884d7b390e88"
API_URL = "https://astro-api-1qnc.onrender.com/api/v1/chinese/bazi"

POLICY = {
    "dohwa_base": "day",   # "day" or "year"
    "yeokma_base": "day",  # "day" or "year"
    "jisal_base": "day",   # "day" or "year"
}

# =========================================
# 한자 -> 한글 매핑
# =========================================

STEM_MAP = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
    "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계"
}

BRANCH_MAP = {
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
    "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해"
}

STEM_WITH_ELEMENT = {
    "갑": "갑목", "을": "을목", "병": "병화", "정": "정화", "무": "무토",
    "기": "기토", "경": "경금", "신": "신금", "임": "임수", "계": "계수"
}

BRANCH_WITH_ELEMENT = {
    "자": "자수", "축": "축토", "인": "인목", "묘": "묘목", "진": "진토",
    "사": "사화", "오": "오화", "미": "미토", "신": "신금", "유": "유금",
    "술": "술토", "해": "해수"
}

BRANCH_ANIMAL = {
    "자": "쥐", "축": "소", "인": "호랑이", "묘": "토끼", "진": "용", "사": "뱀",
    "오": "말", "미": "양", "신": "원숭이", "유": "닭", "술": "개", "해": "돼지"
}

POSITION_NAMES = ["년지", "월지", "일지", "시지"]
PILLAR_POSITION_NAMES = ["연주", "월주", "일주", "시주"]
STEM_POSITION_NAMES = ["년간", "월간", "일간", "시간"]


# =========================================
# API 호출
# =========================================

def get_saju(year, month, day, hour, minute):
    payload = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "lat": 37.5665,
        "lng": 126.9780,
        "city": "Seoul",
        "sex": "M",
        "time_standard": "civil",
        "include_pinyin": True,
        "include_stars": True,
        "include_interactions": True
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY.strip()
    }

    res = requests.post(API_URL, json=payload, headers=headers, timeout=20)

    try:
        data = res.json()
    except Exception:
        print("\nJSON 파싱 실패")
        print(res.text)
        raise

    if "pillars" not in data:
        print("\nAPI 응답에 'pillars'가 없습니다.")
        raise SystemExit

    return data


# =========================================
# 공통 유틸
# =========================================

def normalize_pillars(api_data):
    pillars = api_data["pillars"]

    year_stem = STEM_MAP[pillars[0]["gan"]]
    month_stem = STEM_MAP[pillars[1]["gan"]]
    day_stem = STEM_MAP[pillars[2]["gan"]]
    hour_stem = STEM_MAP[pillars[3]["gan"]]

    year_branch = BRANCH_MAP[pillars[0]["zhi"]]
    month_branch = BRANCH_MAP[pillars[1]["zhi"]]
    day_branch = BRANCH_MAP[pillars[2]["zhi"]]
    hour_branch = BRANCH_MAP[pillars[3]["zhi"]]

    stems = [year_stem, month_stem, day_stem, hour_stem]
    branches = [year_branch, month_branch, day_branch, hour_branch]
    ganji_pillars = [
        year_stem + year_branch,
        month_stem + month_branch,
        day_stem + day_branch,
        hour_stem + hour_branch
    ]

    return {
        "stems": stems,
        "branches": branches,
        "pillars": ganji_pillars,
        "day_stem": day_stem,
        "day_branch": day_branch,
        "year_stem": year_stem,
        "year_branch": year_branch,
    }


def get_base_branch(saju, policy_key):
    base = POLICY[policy_key]
    if base == "day":
        return saju["day_branch"]
    elif base == "year":
        return saju["year_branch"]
    else:
        raise ValueError(f"잘못된 기준축 설정: {policy_key}={base}")


def calc_pair_grade(i, j):
    includes_day = (i == 2 or j == 2)
    adjacent = (j == i + 1)

    grade = 1
    if includes_day:
        grade = 2
    if includes_day and adjacent:
        grade = 3

    return {
        "is_adjacent": adjacent,
        "includes_day": includes_day,
        "grade": grade
    }


# =========================================
# 1) 원진살
# =========================================

def check_wonjin(branches):
    wonjin_pairs = {
        tuple(sorted(("자", "미"))),
        tuple(sorted(("축", "오"))),
        tuple(sorted(("인", "유"))),
        tuple(sorted(("묘", "신"))),
        tuple(sorted(("진", "해"))),
        tuple(sorted(("사", "술"))),
    }

    items = []

    for i, j in combinations(range(4), 2):
        pair = tuple(sorted((branches[i], branches[j])))
        if pair in wonjin_pairs:
            extra = calc_pair_grade(i, j)
            items.append({
                "positions": [POSITION_NAMES[i], POSITION_NAMES[j]],
                "chars": [branches[i], branches[j]],
                **extra
            })

    return {
        "name": "원진살",
        "total_count": len(items),
        "items": items
    }


# =========================================
# 2) 귀문살
# =========================================

def check_gwimun(branches):
    gwimun_pairs = {
        tuple(sorted(("자", "유"))),
        tuple(sorted(("축", "오"))),
        tuple(sorted(("인", "미"))),
        tuple(sorted(("묘", "신"))),
        tuple(sorted(("진", "해"))),
        tuple(sorted(("사", "술"))),
    }

    items = []

    for i, j in combinations(range(4), 2):
        pair = tuple(sorted((branches[i], branches[j])))
        if pair in gwimun_pairs:
            extra = calc_pair_grade(i, j)
            items.append({
                "positions": [POSITION_NAMES[i], POSITION_NAMES[j]],
                "chars": [branches[i], branches[j]],
                **extra
            })

    return {
        "name": "귀문살",
        "total_count": len(items),
        "items": items
    }


# =========================================
# 3) 백호살
# =========================================

def check_baekho(pillars):
    baekho_set = {"갑진", "을미", "병술", "정축", "무진", "임술", "계축"}

    items = []

    for i, pillar in enumerate(pillars):
        if pillar in baekho_set:
            grade = 2 if i == 2 else 1
            items.append({
                "position": PILLAR_POSITION_NAMES[i],
                "pillar": pillar,
                "grade": grade
            })

    return {
        "name": "백호살",
        "total_count": len(items),
        "items": items
    }


# =========================================
# 4) 괴강살
# =========================================

def check_goegang(day_pillar):
    goegang_set = {"임진", "경진", "경술", "무술"}

    items = []
    if day_pillar in goegang_set:
        items.append({
            "position": "일주",
            "pillar": day_pillar,
            "grade": 3
        })

    return {
        "name": "괴강살",
        "total_count": len(items),
        "items": items
    }


# =========================================
# 5) 현침살
# 형상 기반
# 천간: 갑, 신 / 지지: 묘, 오, 미, 신
# =========================================

def check_hyeonchim(stems, branches):
    hyeonchim_stems = {"갑", "신"}
    hyeonchim_branches = {"묘", "오", "미", "신"}

    items = []

    for i, stem in enumerate(stems):
        if stem in hyeonchim_stems:
            items.append({
                "position": STEM_POSITION_NAMES[i],
                "char": stem
            })

    for i, branch in enumerate(branches):
        if branch in hyeonchim_branches:
            items.append({
                "position": POSITION_NAMES[i],
                "char": branch
            })

    return {
        "name": "현침살",
        "total_count": len(items),
        "items": items
    }


# =========================================
# 6) 도화살
# 일지 기준 기본, year 옵션 가능
# 기준지지는 제외하고 년/월/시 또는 월/일/시? -> 자료 기준대로
# 비교는 원국 4지지 전체 중 기준 자리 제외
# =========================================

def check_dohwa(branches, base_branch, base_type="day"):
    dohwa_map = {
        "인": "묘", "오": "묘", "술": "묘",
        "신": "유", "자": "유", "진": "유",
        "해": "자", "묘": "자", "미": "자",
        "사": "오", "유": "오", "축": "오"
    }

    target = dohwa_map.get(base_branch)
    items = []

    if target is None:
        return {"name": "도화살", "base": base_type, "target": None, "total_count": 0, "items": items}

    exclude_idx = 2 if base_type == "day" else 0

    for i in range(4):
        if i == exclude_idx:
            continue
        if branches[i] == target:
            items.append({
                "position": POSITION_NAMES[i],
                "char": branches[i]
            })

    return {
        "name": "도화살",
        "base": base_type,
        "target": target,
        "total_count": len(items),
        "items": items
    }


# =========================================
# 7) 홍염살
# 일간 -> 지지 매핑형
# =========================================

def check_hongyeom(day_stem, branches):
    hongyeom_map = {
        "갑": ["오"],
        "을": ["오"],
        "병": ["인"],
        "정": ["미"],
        "무": ["진"],
        "기": ["진"],
        "경": ["술"],
        "신": ["유"],
        "임": ["신", "자"],
        "계": ["신"],
    }

    targets = hongyeom_map.get(day_stem, [])
    items = []

    for i, branch in enumerate(branches):
        if branch in targets:
            items.append({
                "position": POSITION_NAMES[i],
                "char": branch
            })

    return {
        "name": "홍염살",
        "standard_ilgan": day_stem,
        "targets": targets,
        "total_count": len(items),
        "items": items
    }


# =========================================
# 8) 역마살
# 일지 기준 기본, year 옵션 가능
# 비교는 기준 자리 제외
# =========================================

def check_yeokma(branches, base_branch, base_type="day"):
    yeokma_map = {
        "인": "신", "오": "신", "술": "신",
        "신": "인", "자": "인", "진": "인",
        "해": "사", "묘": "사", "미": "사",
        "사": "해", "유": "해", "축": "해"
    }

    target = yeokma_map.get(base_branch)
    items = []

    if target is None:
        return {"name": "역마살", "base": base_type, "target": None, "total_count": 0, "items": items}

    exclude_idx = 2 if base_type == "day" else 0

    for i in range(4):
        if i == exclude_idx:
            continue
        if branches[i] == target:
            items.append({
                "position": POSITION_NAMES[i],
                "char": branches[i]
            })

    return {
        "name": "역마살",
        "base": base_type,
        "target": target,
        "total_count": len(items),
        "items": items
    }


# =========================================
# 9) 지살
# 일지 기준 기본, year 옵션 가능
# 비교는 기준 자리 제외
# =========================================

def check_jisal(branches, base_branch, base_type="day"):
    jisal_map = {
        "인": "인", "오": "인", "술": "인",
        "신": "신", "자": "신", "진": "신",
        "해": "해", "묘": "해", "미": "해",
        "사": "사", "유": "사", "축": "사"
    }

    target = jisal_map.get(base_branch)
    items = []

    if target is None:
        return {"name": "지살", "base": base_type, "target": None, "total_count": 0, "items": items}

    exclude_idx = 2 if base_type == "day" else 0

    for i in range(4):
        if i == exclude_idx:
            continue
        if branches[i] == target:
            items.append({
                "position": POSITION_NAMES[i],
                "char": branches[i]
            })

    return {
        "name": "지살",
        "base": base_type,
        "target": target,
        "total_count": len(items),
        "items": items
    }


# =========================================
# 실행 함수
# =========================================

def run_all_stars(saju):
    branches = saju["branches"]
    stems = saju["stems"]
    pillars = saju["pillars"]

    dohwa_base = get_base_branch(saju, "dohwa_base")
    yeokma_base = get_base_branch(saju, "yeokma_base")
    jisal_base = get_base_branch(saju, "jisal_base")

    results = [
        check_wonjin(branches),
        check_gwimun(branches),
        check_baekho(pillars),
        check_goegang(saju["pillars"][2]),
        check_hyeonchim(stems, branches),
        check_dohwa(branches, dohwa_base, POLICY["dohwa_base"]),
        check_hongyeom(saju["day_stem"], branches),
        check_yeokma(branches, yeokma_base, POLICY["yeokma_base"]),
        check_jisal(branches, jisal_base, POLICY["jisal_base"]),
    ]

    total_items = sum(item["total_count"] for item in results)

    return {
        "total_star_count": total_items,
        "stars": results
    }


# =========================================
# 출력
# =========================================

def print_result(saju, final_result):
    print("\n========================")
    print("사주 원국")
    print("========================")
    print("연주:", saju["pillars"][0])
    print("월주:", saju["pillars"][1])
    print("일주:", saju["pillars"][2])
    print("시주:", saju["pillars"][3])

    print("\n========================")
    print("일간 / 일지")
    print("========================")
    print("일간:", STEM_WITH_ELEMENT[saju["day_stem"]], "일간")
    print("일주:", saju["pillars"][2], "일주")
    print("일지:", BRANCH_WITH_ELEMENT[saju["day_branch"]], f"(나의 동물: {BRANCH_ANIMAL[saju['day_branch']]})")

    print("\n========================")
    print("신살 결과")
    print("========================")
    print("총 발견 개수:", final_result["total_star_count"])

    for star in final_result["stars"]:
        print(f"\n[{star['name']}] {star['total_count']}개")

        if star["total_count"] == 0:
            print("- 없음")
            continue

        for item in star["items"]:
            print("-", item)


# =========================================
# 메인
# =========================================

def main():
    year = int(input("년도: ").strip())
    month = int(input("월: ").strip())
    day = int(input("일: ").strip())
    hour = int(input("시: ").strip())
    minute = int(input("분: ").strip())

    api_data = get_saju(year, month, day, hour, minute)
    saju = normalize_pillars(api_data)
    final_result = run_all_stars(saju)
    print_result(saju, final_result)


if __name__ == "__main__":
    main()