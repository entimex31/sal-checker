import requests

API_KEY = "4ccc49c1c9cf932dd19428e0d802dbcad1b6731451072e257579884d7b390e88"

URL = "https://astro-api-1qnc.onrender.com/api/v1/chinese/bazi"

# 테스트용 샘플 (QA에서 문제된 케이스 하나)
payload_base = {
    "year": 1989,
    "month": 4,
    "day": 15,
    "hour": 13,
    "minute": 20,
    "lat": 37.5665,
    "lng": 126.9780,
    "city": "Seoul",
    "sex": "M",
    "include_pinyin": True,
    "include_stars": False,
    "include_interactions": False
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "Authorization": f"Bearer {API_KEY}"
}


def call_api(time_standard):
    payload = payload_base.copy()
    payload["time_standard"] = time_standard

    print(f"\n====== {time_standard} ======")

    res = requests.post(URL, json=payload, headers=headers, timeout=20)

    print("status:", res.status_code)

    data = res.json()

    if res.status_code != 200:
        print("error:", data)
        return

    # 핵심 비교 포인트
    pillars = data.get("pillars", [])
    hour_pillar = pillars[3] if len(pillars) > 3 else None

    print("시주:", hour_pillar["gan"] + hour_pillar["zhi"] if hour_pillar else "없음")

    debug = data.get("astro_debug", {})
    print("입력 시간:", debug.get("input_local_time"))
    print("보정 시간(local):", debug.get("effective_solar_time_local"))
    print("보정 시간(absolute):", debug.get("effective_solar_time_absolute"))


# 3가지 방식 호출
call_api("civil")
call_api("true_solar")
call_api("true_solar_absolute")