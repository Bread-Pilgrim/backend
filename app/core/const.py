# 1시간 | 2주
EXPIRE_IN = {"ACCESS": 60 * 60 * 1, "REFRESH": 60 * 60 * 24 * 14}

ETC_MENU_NAME = "기타메뉴"

REVIEW_THRESHOLDS = [1, 10, 50, 100, 500]
BREAD_THRESHOLDS = [10, 100, 500]

BREAD_TYPE_FIELDS = [
    "pastry_bread_count",
    "meal_bread_count",
    "healthy_bread_count",
    "baked_bread_count",
    "retro_bread_count",
    "dessert_bread_count",
    "sandwich_bread_count",
    "cake_bread_count",
]

BADGE_METRICS = {
    10: "meal_bread_count",
    11: "healthy_bread_count",
    12: "baked_bread_count",
    13: "retro_bread_count",
    14: "dessert_bread_count",
    15: "sandwich_bread_count",
    16: "cake_bread_count",
    41: "pastry_bread_count",
}

BADGE_METRICS_REVERSE = {
    "meal_bread_count": 10,
    "healthy_bread_count": 11,
    "baked_bread_count": 12,
    "retro_bread_count": 13,
    "dessert_bread_count": 14,
    "sandwich_bread_count": 15,
    "cake_bread_count": 16,
    "pastry_bread_count": 41,
}
