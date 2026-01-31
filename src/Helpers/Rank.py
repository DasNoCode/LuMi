from typing import Dict, Union, Optional

RANKS: Dict[str, Dict[str, Union[int, str]]] = {
    "Recruit": {"exp": 0, "emoji": "🔨"},
    "Apprentice": {"exp": 1000, "emoji": "🛠️"},
    "Disciple": {"exp": 5000, "emoji": "⚒️"},
    "Adept": {"exp": 10000, "emoji": "🍀"},
    "Master": {"exp": 20000, "emoji": "〽️"},
    "Grandmaster": {"exp": 50000, "emoji": "🔮"},
    "Legendary": {"exp": 100000, "emoji": "👑"},
    "Legendary II": {"exp": 135000, "emoji": "👑"},
    "Legendary III": {"exp": 175000, "emoji": "👑"},
    "Mythical": {"exp": 200000, "emoji": "🌟"},
    "Mythical II": {"exp": 350000, "emoji": "🌟"},
    "Mythical III": {"exp": 425000, "emoji": "🌟"},
    "Immortal": {"exp": 500000, "emoji": "💀"},
    "Immortal II": {"exp": 650000, "emoji": "💀"},
    "Immortal III": {"exp": 850000, "emoji": "💀"},
    "Radiant": {"exp": 1000000, "emoji": "💫"},
    "Divine": {"exp": 2000000, "emoji": "🔥"},
}


def get_rank(total_xp: int) -> Dict[str, Union[int, str, None]]:
    level = 1
    while total_xp >= (5 * (level**2) + 50):
        level += 1
    next_level_xp = 5 * (level**2) + 50

    sorted_ranks = sorted(RANKS.items(), key=lambda x: x[1]["exp"])

    current_rank_name = "Recruit"
    current_rank_data = RANKS["Recruit"]
    next_rank_name: Optional[str] = None
    next_rank_emoji: Optional[str] = None
    next_rank_xp: Optional[int] = None

    for i, (rank_name, rank_data) in enumerate(sorted_ranks):
        if total_xp >= rank_data["exp"]:
            current_rank_name = rank_name
            current_rank_data = rank_data
            # Only assign next rank if it's not the last in the list
            if (
                i + 1 < len(sorted_ranks)
                and total_xp < sorted_ranks[i + 1][1]["exp"]
            ):
                next_rank_name = sorted_ranks[i + 1][0]
                next_rank_emoji = sorted_ranks[i + 1][1]["emoji"]
                next_rank_xp = sorted_ranks[i + 1][1]["exp"]
        else:
            break

    return {
        "level": level,
        "xp": total_xp,
        "level_xp_target": next_level_xp,
        "rank_name": current_rank_name,
        "rank_emoji": current_rank_data["emoji"],
        "next_rank_name": next_rank_name,
        "next_rank_emoji": next_rank_emoji,
        "next_rank_xp": next_rank_xp,
    }
