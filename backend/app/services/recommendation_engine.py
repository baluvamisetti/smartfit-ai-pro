"""
Fashion Recommendation Engine
-------------------------------
A hybrid rule-based recommendation system that maps body shape + skin
undertone + occasion to clothing style and color guidance. This is
intentionally rule-based (backed by established styling heuristics)
rather than a black-box model, because fashion recommendations need to
be explainable to the end user ("why was this suggested to me").

This is the MVP core; Phase 2 can add a learned re-ranking layer
(collaborative filtering over user feedback) on top of these rules.
"""

BODY_SHAPE_GUIDE = {
    "Hourglass": {
        "goal": "accentuate the defined waist",
        "fits": ["wrap tops", "fitted shirts", "high-waisted bottoms", "belted jackets"],
        "avoid": ["boxy oversized cuts", "shapeless dresses"],
    },
    "Rectangle": {
        "goal": "create the illusion of curves and definition",
        "fits": ["peplum tops", "layered outfits", "belts to define waist", "structured jackets"],
        "avoid": ["straight-cut shift dresses without a belt"],
    },
    "Triangle": {
        "goal": "balance wider hips with volume on top",
        "fits": ["boat-neck tops", "structured shoulders", "A-line bottoms", "statement collars"],
        "avoid": ["skinny bottoms with plain tops", "tapered pants with tight tops"],
    },
    "Inverted Triangle": {
        "goal": "balance broader shoulders with volume on bottom",
        "fits": ["V-neck tops", "wide-leg pants", "A-line skirts", "minimal shoulder detail"],
        "avoid": ["shoulder pads", "boat necks", "puffed sleeves"],
    },
    "Oval": {
        "goal": "elongate the silhouette and create vertical definition",
        "fits": ["V-neck or open-collar tops", "vertical stripes", "structured open jackets", "straight-leg pants"],
        "avoid": ["horizontal stripes", "tight-fitted waistbands", "bulky layering at the middle"],
    },
    "Athletic": {
        "goal": "add soft definition to a straighter frame",
        "fits": ["textured fabrics", "peplum or wrap details", "tailored blazers", "straight or slim pants"],
        "avoid": ["extremely boxy silhouettes"],
    },
    "Undetermined": {
        "goal": "versatile, universally flattering choices",
        "fits": ["well-tailored fits", "medium-rise bottoms", "classic silhouettes"],
        "avoid": ["extremely oversized or extremely tight fits"],
    },
}

UNDERTONE_COLOR_GUIDE = {
    "Warm": {
        "best": ["mustard yellow", "olive green", "terracotta", "warm red", "camel", "coral", "warm brown"],
        "avoid": ["icy pastels", "stark cool blue", "silver-grey"],
        "palette_hex": ["#C9A227", "#6B8E23", "#E2725B", "#A52A2A", "#C19A6B", "#FF7F50"],
    },
    "Cool": {
        "best": ["navy blue", "emerald green", "true red", "lavender", "cool grey", "sapphire blue"],
        "avoid": ["mustard yellow", "orange", "warm brown"],
        "palette_hex": ["#1B2A4A", "#046A38", "#C41E3A", "#B497BD", "#8C92AC", "#0F52BA"],
    },
    "Neutral": {
        "best": ["soft white", "jade green", "medium blue", "rose pink", "charcoal grey"],
        "avoid": ["neon shades", "overly saturated primary colors"],
        "palette_hex": ["#F5F5F0", "#00A86B", "#4169E1", "#E8A0BF", "#36454F"],
    },
}

OCCASION_CATEGORIES = {
    "casual": ["T-shirts", "Jeans", "Sneakers", "Casual jackets"],
    "formal": ["Formal shirts", "Trousers", "Blazers", "Formal shoes"],
    "ethnic": ["Kurta sets", "Nehru jackets", "Ethnic footwear"],
    "party": ["Statement shirts", "Slim-fit pants", "Loafers", "Accessories"],
    "sport": ["Moisture-wicking tees", "Track pants", "Sports shoes"],
}


def generate_recommendation(body_shape: str, undertone: str, skin_shade_group: str,
                             gender: str = "unisex", occasion: str = "casual",
                             age_group: str = "adult") -> dict:

    body_guide = BODY_SHAPE_GUIDE.get(body_shape, BODY_SHAPE_GUIDE["Undetermined"])
    color_guide = UNDERTONE_COLOR_GUIDE.get(undertone, UNDERTONE_COLOR_GUIDE["Neutral"])
    occasion_items = OCCASION_CATEGORIES.get(occasion.lower(), OCCASION_CATEGORIES["casual"])

    color_recommendation = {
        "best_colors": color_guide["best"],
        "colors_to_avoid": color_guide["avoid"],
        "palette_hex": color_guide["palette_hex"],
        "reasoning": (
            f"Your {undertone.lower()} undertone pairs best with these tones because they "
            f"complement your natural {skin_shade_group.lower()} skin shade rather than "
            f"clashing against it."
        ),
    }

    clothing_recommendations = [
        {
            "category": "Top Wear",
            "items": body_guide["fits"][:2] + [occasion_items[0]],
            "reasoning": f"These help {body_guide['goal']} for a {body_shape} body shape.",
        },
        {
            "category": "Bottom Wear",
            "items": [item for item in body_guide["fits"] if "pant" in item or "bottom" in item or "skirt" in item] or [occasion_items[1] if len(occasion_items) > 1 else "Tailored trousers"],
            "reasoning": f"Balances proportions for a {body_shape} silhouette.",
        },
        {
            "category": "Layering / Outerwear",
            "items": [item for item in body_guide["fits"] if "jacket" in item or "blazer" in item] or ["Structured jacket"],
            "reasoning": "Adds definition without overwhelming your frame.",
        },
        {
            "category": f"{occasion.title()} Footwear & Accessories",
            "items": occasion_items[2:] or ["Minimal accessories"],
            "reasoning": f"Matches the {occasion} occasion while staying consistent with your color palette.",
        },
    ]

    # Simple explainable fashion score (0-100): base + bonuses for confident inputs
    fashion_score = 70
    if body_shape != "Undetermined":
        fashion_score += 15
    if undertone != "Neutral":
        fashion_score += 10
    fashion_score = min(fashion_score, 100)

    style_summary = (
        f"For your {body_shape} body shape and {undertone} undertone, the goal is to "
        f"{body_guide['goal']}. Stick to {color_guide['best'][0]} and {color_guide['best'][1]} "
        f"tones for {occasion} wear, and avoid {body_guide['avoid'][0]}."
    )

    return {
        "fashion_score": fashion_score,
        "color_recommendation": color_recommendation,
        "clothing_recommendations": clothing_recommendations,
        "style_summary": style_summary,
    }
