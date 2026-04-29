from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

RAINFOREST_API_KEY = "6926EF1C425F40AE9DC3A23FE10D3B63"
AFFILIATE_TAG = "crydalch7-20"

KEYWORD_MAP = {
    ("Mom", "Christmas"): "gifts for mom christmas",
    ("Mom", "Birthday"): "birthday gifts for mom",
    ("Mom", "Anniversary"): "anniversary gifts for her",
    ("Mom", "Graduation"): "graduation gifts for women",
    ("Mom", "Easter"): "easter gifts for mom",
    ("Mom", "Just Because"): "thoughtful gifts for mom",
    ("Mom", "Valentine's Day"): "valentines gifts for mom",
    ("Mom", "Mother's Day"): "mothers day gifts for mom",
    ("Mom", "New Baby"): "new mom gifts",

    ("Dad", "Christmas"): "gifts for dad christmas",
    ("Dad", "Birthday"): "birthday gifts for dad",
    ("Dad", "Anniversary"): "anniversary gifts for him",
    ("Dad", "Graduation"): "graduation gifts for men",
    ("Dad", "Easter"): "easter gifts for dad",
    ("Dad", "Just Because"): "cool gifts for dad",
    ("Dad", "Valentine's Day"): "valentines gifts for husband",
    ("Dad", "Father's Day"): "fathers day gifts for dad",
    ("Dad", "New Baby"): "new dad gifts",

    ("Partner", "Christmas"): "romantic christmas gifts",
    ("Partner", "Birthday"): "romantic birthday gifts",
    ("Partner", "Anniversary"): "anniversary gifts for couple",
    ("Partner", "Graduation"): "graduation gifts for boyfriend girlfriend",
    ("Partner", "Easter"): "easter gifts for partner",
    ("Partner", "Just Because"): "romantic gifts for partner",
    ("Partner", "Valentine's Day"): "valentines day gifts for her him",
    ("Partner", "New Baby"): "new baby couple gifts",
    ("Partner", "Housewarming"): "housewarming gifts for couple",

    ("Sibling", "Christmas"): "gifts for sibling christmas",
    ("Sibling", "Birthday"): "birthday gifts for brother sister",
    ("Sibling", "Graduation"): "graduation gifts for sibling",
    ("Sibling", "Easter"): "easter basket gifts",
    ("Sibling", "Just Because"): "fun gifts for sibling",
    ("Sibling", "Valentine's Day"): "galentines gifts for sister",
    ("Sibling", "New Baby"): "new baby sibling gift",
    ("Sibling", "Housewarming"): "housewarming gifts for sibling",

    ("Best Friend", "Christmas"): "best friend christmas gifts",
    ("Best Friend", "Birthday"): "best friend birthday gifts",
    ("Best Friend", "Graduation"): "graduation gifts for best friend",
    ("Best Friend", "Easter"): "easter gifts for friend",
    ("Best Friend", "Just Because"): "thoughtful gifts for best friend",
    ("Best Friend", "Valentine's Day"): "galentines day gifts best friend",
    ("Best Friend", "New Baby"): "new baby gifts for best friend",
    ("Best Friend", "Housewarming"): "housewarming gifts for friend",

    ("Coworker", "Christmas"): "coworker christmas gifts office",
    ("Coworker", "Birthday"): "birthday gifts for coworker",
    ("Coworker", "Graduation"): "graduation gifts coworker",
    ("Coworker", "Easter"): "easter office gifts",
    ("Coworker", "Just Because"): "appreciation gifts for coworker",
    ("Coworker", "Housewarming"): "housewarming office gift",
    ("Coworker", "Valentine's Day"): "office valentines gifts",

    ("Grandma", "Christmas"): "christmas gifts for grandma",
    ("Grandma", "Birthday"): "birthday gifts for grandma",
    ("Grandma", "Mother's Day"): "mothers day gifts for grandma",
    ("Grandma", "Easter"): "easter gifts for grandma",
    ("Grandma", "Just Because"): "thoughtful gifts for grandma",
    ("Grandma", "Anniversary"): "anniversary gifts for grandma",
    ("Grandma", "Valentine's Day"): "valentines gifts for grandma",

    ("Grandpa", "Christmas"): "christmas gifts for grandpa",
    ("Grandpa", "Birthday"): "birthday gifts for grandpa",
    ("Grandpa", "Father's Day"): "fathers day gifts for grandpa",
    ("Grandpa", "Easter"): "easter gifts for grandpa",
    ("Grandpa", "Just Because"): "cool gifts for grandpa",
    ("Grandpa", "Anniversary"): "anniversary gifts for grandpa",

    ("Teacher", "Christmas"): "christmas gifts for teacher",
    ("Teacher", "Birthday"): "birthday gifts for teacher",
    ("Teacher", "Graduation"): "end of year teacher gifts",
    ("Teacher", "Just Because"): "appreciation gifts for teacher",
    ("Teacher", "Easter"): "easter gifts for teacher",

    ("Kid", "Christmas"): "best christmas toys for kids",
    ("Kid", "Birthday"): "popular birthday gifts for kids",
    ("Kid", "Easter"): "easter basket stuffers for kids",
    ("Kid", "Graduation"): "kindergarten graduation gifts",
    ("Kid", "Just Because"): "fun gifts for kids",
    ("Kid", "New Baby"): "newborn baby gifts",

    ("Teen", "Christmas"): "christmas gifts for teenagers",
    ("Teen", "Birthday"): "birthday gifts for teens",
    ("Teen", "Easter"): "easter basket ideas for teens",
    ("Teen", "Graduation"): "high school graduation gifts",
    ("Teen", "Just Because"): "cool gifts for teenagers",
    ("Teen", "Valentine's Day"): "valentines gifts for teens",
}

BUDGET_MAP = {
    "Under $25": (0, 25),
    "$25-$75": (25, 75),
    "$75-$125": (75, 125),
    "$125+": (125, 9999),
}

BADGES = [
    "Trending this season",
    "Top pick right now",
    "Most gifted this week",
    "Flying off shelves",
    "Crowd favorite",
    "Trending up 200%+",
    "Best seller",
    "Scout's top pick",
]

BLACKLIST = [
    "sexy", "adult", "erotic", "lingerie", "thong", "bra", "panty",
    "vibrat", "dildo", "penis", "vagina", "breast", "nipple", "nude",
    "naked", "porn", "xxx", "fetish", "bondage", "massage oil",
    "edible", "stripper", "bachelor", "bachelorette"
]

def search_rainforest(keyword, min_price, max_price, fallback_keyword=None):
    def fetch(kw, min_p, max_p):
        params = {
            "api_key": RAINFOREST_API_KEY,
            "type": "search",
            "amazon_domain": "amazon.com",
            "search_term": kw,
            "sort_by": "featured",
            "exclude_sponsored": "true",
        }
        if min_p > 0:
            params["min_price"] = str(int(min_p))
        if max_p != 9999:
            params["max_price"] = str(int(max_p))

        try:
            response = requests.get(
                "https://api.rainforestapi.com/request",
                params=params,
                timeout=15
            )
            data = response.json()
            products = []
            items = data.get("search_results", [])

            for item in items:
                # Get title
                title = item.get("title", "").strip()
                if not title:
                    continue

                # Filter inappropriate content
                if any(word.lower() in title.lower() for word in BLACKLIST):
                    continue

                # Get price
                price_data = item.get("price", {})
                price = price_data.get("value", 0) if price_data else 0
                if not price:
                    # Try buybox price
                    buybox = item.get("buybox_winner", {})
                    if buybox:
                        price_data = buybox.get("price", {})
                        price = price_data.get("value", 0) if price_data else 0
                if not price:
                    continue

                # Enforce budget
                if price < min_p:
                    continue
                if max_p != 9999 and price > max_p:
                    continue

                # Get ASIN and build affiliate URL
                asin = item.get("asin", "")
                if not asin:
                    continue
                affiliate_url = f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"

                # Get image
                image = item.get("image", "")

                # Get rating
                rating = item.get("rating", "")
                reviews = item.get("ratings_total", "")

                products.append({
                    "name": title[:65] + ("..." if len(title) > 65 else ""),
                    "price": f"${price:.2f}",
                    "image": image,
                    "url": affiliate_url,
                    "rating": f"{rating} out of 5 stars" if rating else "",
                    "reviews": f"{int(reviews):,}" if reviews else "",
                    "badge": random.choice(BADGES),
                })

                if len(products) >= 8:
                    break

            return products

        except Exception as e:
            print(f"Rainforest API error: {e}")
            return []

    # Try specific keyword first
    results = fetch(keyword, min_price, max_price)

    # If less than 4 results try fallback
    if len(results) < 4 and fallback_keyword:
        results = fetch(fallback_keyword, min_price, max_price)

    # If still less than 4 try broad search
    if len(results) < 4:
        budget_label = f"under {int(max_price)}" if max_price != 9999 else "over 125"
        results = fetch(f"best gifts {budget_label} dollars", min_price, max_price)

    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/results")
def results():
    who = request.args.get("who", "Mom")
    occasion = request.args.get("occasion", "Christmas")
    budget = request.args.get("budget", "$25-$75")
    budget = budget.replace("%2B", "+")
    return render_template("results.html", who=who, occasion=occasion, budget=budget)

@app.route("/api/products")
def api_products():
    who = request.args.get("who", "Mom")
    occasion = request.args.get("occasion", "Christmas")
    budget = request.args.get("budget", "$25-$75")
    budget = budget.replace("%2B", "+")
    min_price, max_price = BUDGET_MAP.get(budget, (25, 75))
    keyword = KEYWORD_MAP.get((who, occasion), f"gifts for {who.lower()} {occasion.lower()}")
    fallback = f"gifts for {who.lower()}"
    products = search_rainforest(keyword, min_price, max_price, fallback_keyword=fallback)
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)
