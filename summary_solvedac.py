import math
from sys import argv

import requests

# fmt: off
USERNAME = argv[1]
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


request = requests.get(USER_API_URL, {"handle": USERNAME})
user = request.json()

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

get_rating = lambda x: round(175 * (1 - 0.995**x))
count = 0
while (
    get_rating(solved_count + count) == get_rating(solved_count)
    and rating_by_solved_count != 175
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

request = requests.get(TOP_100_API_URL, {"handle": USERNAME})
top_100 = request.json()
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
    f"[^1]: `{min(rating_by_solved_count + 1, 175)} = round(175 * (1 - 0.995 ** {solved_count + count}))`"
)
