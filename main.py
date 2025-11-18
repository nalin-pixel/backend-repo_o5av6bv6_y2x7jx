import os
import random
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import create_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Domain Data ----------
# Tags and representative card images for the 7-round picker
TAG_CARDS: Dict[str, Dict[str, str]] = {
    # vibe / landscape
    "beach": {"label": "Beach", "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&auto=format&fit=crop"},
    "mountains": {"label": "Mountains", "img": "https://images.unsplash.com/photo-1509644851169-2acc08aa25b8?q=80&w=1200&auto=format&fit=crop"},
    "city": {"label": "City", "img": "https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=1200&auto=format&fit=crop"},
    "countryside": {"label": "Countryside", "img": "https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?q=80&w=1200&auto=format&fit=crop"},
    "desert": {"label": "Desert", "img": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop"},
    "tropical": {"label": "Tropical", "img": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1200&auto=format&fit=crop"},
    "arctic": {"label": "Arctic", "img": "https://images.unsplash.com/photo-1476610182048-b716b8518aae?q=80&w=1200&auto=format&fit=crop"},
    # trip styles
    "adventure": {"label": "Adventure", "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1200&auto=format&fit=crop"},
    "relaxation": {"label": "Relaxation", "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&auto=format&fit=crop"},
    "culture": {"label": "Culture", "img": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1200&auto=format&fit=crop"},
    "nightlife": {"label": "Nightlife", "img": "https://images.unsplash.com/photo-1533236897111-3e94666b2edf?q=80&w=1200&auto=format&fit=crop"},
    "food": {"label": "Food", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200&auto=format&fit=crop"},
    # budget / comfort
    "luxury": {"label": "Luxury", "img": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1200&auto=format&fit=crop"},
    "budget": {"label": "Budget", "img": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=1200&auto=format&fit=crop"},
    # climate
    "warm": {"label": "Warm", "img": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?q=80&w=1200&auto=format&fit=crop"},
    "mild": {"label": "Mild", "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1200&auto=format&fit=crop"},
    "cold": {"label": "Cold", "img": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop"},
}

# Destination catalog with tags and helper to build outgoing links
DESTINATIONS = [
    {
        "name": "Bali",
        "country": "Indonesia",
        "tags": ["beach", "tropical", "relaxation", "warm", "food"],
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1400&auto=format&fit=crop",
        "airport": "DPS",
        "city": "Bali"
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "tags": ["culture", "food", "mild", "city"],
        "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1400&auto=format&fit=crop",
        "airport": "KIX",
        "city": "Kyoto"
    },
    {
        "name": "Reykjavík",
        "country": "Iceland",
        "tags": ["arctic", "adventure", "cold", "mountains"],
        "image": "https://images.unsplash.com/photo-1500043357865-c6b8827edfbe?q=80&w=1400&auto=format&fit=crop",
        "airport": "KEF",
        "city": "Reykjavik"
    },
    {
        "name": "Paris",
        "country": "France",
        "tags": ["city", "culture", "food", "nightlife", "mild"],
        "image": "https://images.unsplash.com/photo-1508057198894-247b23fe5ade?q=80&w=1400&auto=format&fit=crop",
        "airport": "CDG",
        "city": "Paris"
    },
    {
        "name": "Marrakech",
        "country": "Morocco",
        "tags": ["desert", "warm", "culture", "food"],
        "image": "https://images.unsplash.com/photo-1544989164-31dc3c645987?q=80&w=1400&auto=format&fit=crop",
        "airport": "RAK",
        "city": "Marrakech"
    },
    {
        "name": "Queenstown",
        "country": "New Zealand",
        "tags": ["mountains", "adventure", "mild"],
        "image": "https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?q=80&w=1400&auto=format&fit=crop",
        "airport": "ZQN",
        "city": "Queenstown"
    },
    {
        "name": "Bangkok",
        "country": "Thailand",
        "tags": ["city", "food", "nightlife", "warm", "budget"],
        "image": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?q=80&w=1400&auto=format&fit=crop",
        "airport": "BKK",
        "city": "Bangkok"
    },
    {
        "name": "Amalfi Coast",
        "country": "Italy",
        "tags": ["beach", "relaxation", "mild", "food"],
        "image": "https://images.unsplash.com/photo-1504730653930-b9a2f0f4b3c8?q=80&w=1400&auto=format&fit=crop",
        "airport": "NAP",
        "city": "Amalfi"
    },
    {
        "name": "Cusco",
        "country": "Peru",
        "tags": ["adventure", "mountains", "culture"],
        "image": "https://images.unsplash.com/photo-1508261303786-0e3b4e42a4ea?q=80&w=1400&auto=format&fit=crop",
        "airport": "CUZ",
        "city": "Cusco"
    },
    {
        "name": "New York",
        "country": "USA",
        "tags": ["city", "nightlife", "food", "luxury"],
        "image": "https://images.unsplash.com/photo-1467269204594-9661b134dd2b?q=80&w=1400&auto=format&fit=crop",
        "airport": "JFK",
        "city": "New York"
    },
]


# ---------- Link Builders ----------
def mk_stays_url(city: str) -> str:
    return f"https://www.booking.com/searchresults.html?ss={city}"


def mk_flights_url(airport: str) -> str:
    return f"https://www.skyscanner.com/transport/flights-to/{airport.lower()}/"


def mk_guide_url(city: str) -> str:
    return f"https://www.google.com/search?q={city}+travel+guide"


# ---------- Models ----------
class SurveyAnswers(BaseModel):
    budget: str = Field(..., description="Budget range: budget|mid|luxury")
    trip_length: str = Field(..., description="Length: weekend|1-2 weeks|long")
    flexibility: str = Field(..., description="Flexibility: low|medium|high")
    stay_type: str = Field(..., description="hotel|apartment|hostel|resort|villa")
    climate: Optional[str] = Field(None, description="warm|mild|cold")
    pace: Optional[str] = Field(None, description="chill|balanced|packed")
    month: Optional[str] = Field(None, description="Travel month keyword")
    companions: Optional[str] = Field(None, description="solo|couple|family|friends")


class ChoiceRequest(BaseModel):
    history: List[str] = Field(default_factory=list, description="Previously chosen tag ids")


class ChoiceCard(BaseModel):
    id: str
    label: str
    image: str


class ChoiceResponse(BaseModel):
    round: int
    total_rounds: int
    options: List[ChoiceCard]


class RecommendRequest(BaseModel):
    answers: SurveyAnswers
    history: List[str]


class Destination(BaseModel):
    name: str
    country: str
    image: str
    score: float
    tags: List[str]
    stays_url: str
    flights_url: str
    guide_url: str


class RecommendResponse(BaseModel):
    recommendations: List[Destination]
    saved_id: Optional[str] = None


TOTAL_ROUNDS = 7


# ---------- Helper Logic ----------
def next_choices(history: List[str]) -> List[ChoiceCard]:
    # diversify: start with broader categories, then mix with style/budget/climate
    available_keys = list(TAG_CARDS.keys())

    # reduce showing duplicates already chosen in last 2 rounds
    recent = set(history[-2:])

    # Bias selection towards complementary tags if user already picked some
    bias_pool: List[str] = []
    for tag in history:
        if tag in ("beach", "mountains", "city", "countryside", "desert", "tropical", "arctic"):
            bias_pool += ["adventure", "relaxation", "food", "culture", "nightlife"]
        if tag in ("adventure", "relaxation", "culture", "nightlife", "food"):
            bias_pool += ["beach", "mountains", "city", "tropical", "countryside"]
        if tag in ("budget", "luxury"):
            bias_pool += ["city", "beach", "food", "relaxation"]
        if tag in ("warm", "mild", "cold"):
            bias_pool += ["beach", "mountains", "arctic", "desert"]

    # Candidate set: avoid most recent duplicates
    candidates = [k for k in available_keys if k not in recent]

    # Inject bias_pool to the front
    random.shuffle(candidates)
    if bias_pool:
        random.shuffle(bias_pool)
        # Add some biased candidates on top
        bias_added = [b for b in bias_pool if b in TAG_CARDS and b not in recent]
        candidates = bias_added + candidates

    # Keep first 4 unique keys
    seen = set()
    selected_keys: List[str] = []
    for key in candidates:
        if key not in seen:
            seen.add(key)
            selected_keys.append(key)
        if len(selected_keys) == 4:
            break

    # Fallback if not enough
    if len(selected_keys) < 4:
        remaining = [k for k in available_keys if k not in seen]
        selected_keys += remaining[: 4 - len(selected_keys)]

    return [
        ChoiceCard(id=k, label=TAG_CARDS[k]["label"], image=TAG_CARDS[k]["img"]) for k in selected_keys
    ]


def score_destination(dest: Dict[str, Any], answers: SurveyAnswers, history: List[str]) -> float:
    score = 0.0
    # Tag overlap weight
    hist_set = set(history)
    score += 3.0 * len(hist_set.intersection(set(dest["tags"])))

    # Budget alignment
    if answers.budget == "budget" and "budget" in dest["tags"]:
        score += 1.5
    if answers.budget == "luxury" and "luxury" in dest["tags"]:
        score += 1.5

    # Climate
    if answers.climate and answers.climate in dest["tags"]:
        score += 1.0

    # Pace/style influence
    if answers.pace == "chill" and "relaxation" in dest["tags"]:
        score += 0.8
    if answers.pace == "packed" and ("city" in dest["tags"] or "adventure" in dest["tags"]):
        score += 0.8

    # Companions
    if answers.companions == "family" and ("beach" in dest["tags"] or "relaxation" in dest["tags"]):
        score += 0.5
    if answers.companions == "friends" and "nightlife" in dest["tags"]:
        score += 0.5
    if answers.companions == "couple" and ("culture" in dest["tags"] or "relaxation" in dest["tags"]):
        score += 0.5

    # Slight bonus for food lovers
    if "food" in hist_set:
        if "food" in dest["tags"]:
            score += 0.7

    return score


# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"message": "Travel Recommender API ready"}


@app.post("/api/choices", response_model=ChoiceResponse)
def get_next_choices(req: ChoiceRequest):
    round_idx = len(req.history)
    if round_idx >= TOTAL_ROUNDS:
        raise HTTPException(status_code=400, detail="All rounds completed")
    options = next_choices(req.history)
    return ChoiceResponse(round=round_idx + 1, total_rounds=TOTAL_ROUNDS, options=options)


@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if len(req.history) < TOTAL_ROUNDS:
        raise HTTPException(status_code=400, detail="Please complete all rounds before requesting recommendations")

    # Score destinations
    scored: List[Dict[str, Any]] = []
    for d in DESTINATIONS:
        s = score_destination(d, req.answers, req.history)
        scored.append({**d, "score": s})

    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]

    # Save to DB as a recommendation record
    try:
        rec_doc = {
            "answers": req.answers.model_dump(),
            "history": req.history,
            "results": [{"name": t["name"], "country": t["country"], "score": t["score"]} for t in top],
        }
        saved_id = create_document("recommendation", rec_doc)
    except Exception:
        saved_id = None

    results: List[Destination] = []
    for t in top:
        results.append(
            Destination(
                name=t["name"],
                country=t["country"],
                image=t["image"],
                score=round(float(t["score"]), 2),
                tags=t["tags"],
                stays_url=mk_stays_url(t["city"]),
                flights_url=mk_flights_url(t["airport"]),
                guide_url=mk_guide_url(t["city"]),
            )
        )

    return RecommendResponse(recommendations=results, saved_id=saved_id)


@app.get("/test")
def test_database():
    """Minimal health with env status"""
    response = {
        "backend": "✅ Running",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
    }
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
