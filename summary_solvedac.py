import math
import sys
import time

import requests

# fmt: off
USERNAME = sys.argv[1]
SOLVED_URL = f"https://solved.ac/{USERNAME}"
BADGE_URL = f"http://mazassumnida.wtf/api/generate_badge?boj={USERNAME}"
USER_API_URL = "https://solved.ac/api/v3/user/show"
TOP_100_API_URL = "https://solved.ac/api/v3/user/top_100"

PROBLEM_TOP_TIER = 30
TIER_RATING = [
    0,                              # Unrated
    30, 60, 90, 120, 150,           # Bronze
    200, 300, 400, 500, 650,        # Silver
    800, 950, 1100, 1250, 1400,     # Gold
    1600, 1750, 1900, 2000, 2100,   # Platinum
    2200, 2300, 2400, 2500, 2600,   # Diamond
    2700, 2800, 2850, 2900, 2950,   # Ruby
    3000                            # Master
]
# fmt: on

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BACKOFF_BASE = 2


def api_get(url, params):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                print(f"Error: request to {url} failed after {MAX_RETRIES} attempts: {exc}", file=sys.stderr)
                sys.exit(1)
            time.sleep(BACKOFF_BASE ** attempt)
            continue

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                if attempt == MAX_RETRIES:
                    print(f"Error: {url} returned HTTP 200 but body is not valid JSON.", file=sys.stderr)
                    sys.exit(1)
                time.sleep(BACKOFF_BASE ** attempt)
                continue

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt == MAX_RETRIES:
                print(f"Error: {url} returned HTTP {response.status_code} after {MAX_RETRIES} attempts.", file=sys.stderr)
                sys.exit(1)
            time.sleep(BACKOFF_BASE ** attempt)
            continue

        print(f"Error: {url} returned HTTP {response.status_code}: {response.text[:200]}", file=sys.stderr)
        sys.exit(1)


def get_tier_title(x):
    titles = ["Unrated", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Master"] # fmt: skip
    levels = ["V", "IV", "III", "II", "I"]
    if x == 0 or x == 31:
        return titles[math.ceil(x / 5)]
    else:
        return f"{titles[(x - 1) // 5 + 1]} {levels[(x - 1) % 5]}"


def get_tier_color(x):
    colors = ["#2d2d2d", "#ad5600", "#435f7a", "#ec9a00", "#27e2a4", "#00b4fc", "#ff0062", "#B491FF"] # fmt: skip
    return colors[math.ceil(x / 5)]


user = api_get(USER_API_URL, {"handle": USERNAME})

tier = user["tier"]
rating = user["rating"]
rating_by_problems_sum = user["ratingByProblemsSum"]
rating_by_class = user["ratingByClass"]
rating_by_solved_count = user["ratingBySolvedCount"]
solved_count = user["solvedCount"]

print(f"[![solved.ac Profile]({BADGE_URL})]({SOLVED_URL})")
print()
print(
    f"$\\huge{{\\rm{{\\color{{{get_tier_color(tier + 1)}}}{get_tier_title(tier + 1)}}}}}$까지 **+{TIER_RATING[tier + 1] - rating:,d}** 남음"
)
print()

print("## 레이팅 종합")
print()

get_rating = lambda x: round(200 * (1 - 0.997**x))
count = 0
while (
    get_rating(solved_count + count) == get_rating(solved_count)
    and rating_by_solved_count != 200
):
    count += 1

print(f"| {get_tier_title(tier)} | +{rating:,d}")
print("| --- | --: |")
print(f"| 상위 100문제의 난이도 합 | **+{rating_by_problems_sum:,d}** |")
print(f"| CLASS {user['class']} | **+{rating_by_class:,d}** |")
print(
    f"| 문제수에 따른 보너스 점수 _(다음 점수까지 **{count}**문제[^1])_ | **+{rating_by_solved_count:,d}** |"
)

print()
print("## 난이도 별 얻게 될 점수")
print()

top_100 = api_get(TOP_100_API_URL, {"handle": USERNAME})
lowest_point = top_100["items"][-1]["level"]

print("| Level | Earning Points |")
print("| :---: | -------------: |")
for n in range(min(lowest_point + 10, PROBLEM_TOP_TIER), lowest_point, -1):
    if n == tier:
        print(f"| **{get_tier_title(n)}** | **+{n - lowest_point}** |")
    else:
        print(f"| {get_tier_title(n)} | +{n - lowest_point} |")
print()

print(
    f"[^1]: `{min(rating_by_solved_count + 1, 200)} = round(200 * (1 - 0.997 ** {solved_count + count}))`"
)
