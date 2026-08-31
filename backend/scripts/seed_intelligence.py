import asyncio
import uuid
import json
from sqlalchemy import text
from db.session import engine

async def seed_intelligence():
    print("Seeding Recruiter Intelligence & Personas...")
    
    # ─── Recruiter Personas ──────────────────────────────────────────
    personas = [
        {
            "id": uuid.uuid4(),
            "name": "Skeptical Tech Lead",
            "company_context": "High-Growth Startup",
            "personality_traits": json.dumps({"skepticism": 0.9, "speed": 0.8, "empathy": 0.3}),
            "focus_areas": json.dumps(["Scalability", "Edge Cases", "Code Quality", "Ownership"]),
            "communication_style": "Pressure-based"
        },
        {
            "id": uuid.uuid4(),
            "name": "FAANG Senior EM",
            "company_context": "Big Tech",
            "personality_traits": json.dumps({"skepticism": 0.6, "speed": 0.5, "empathy": 0.7}),
            "focus_areas": json.dumps(["System Design", "Cultural Alignment", "Impact", "Leadership"]),
            "communication_style": "Inquisitive"
        },
        {
            "id": uuid.uuid4(),
            "name": "Rapid-Fire CTO",
            "company_context": "Early Stage",
            "personality_traits": json.dumps({"skepticism": 0.5, "speed": 1.0, "empathy": 0.4}),
            "focus_areas": json.dumps(["Fast Implementation", "Pragmatism", "Debugging", "Versatility"]),
            "communication_style": "Direct"
        }
    ]

    async with engine.begin() as conn:
        for p in personas:
            await conn.execute(
                text("""
                INSERT INTO recruiter_personas (id, name, company_context, personality_traits, focus_areas, communication_style)
                VALUES (:id, :name, :company_context, :personality_traits, :focus_areas, :communication_style)
                ON CONFLICT (name) DO UPDATE SET
                    personality_traits = EXCLUDED.personality_traits,
                    focus_areas = EXCLUDED.focus_areas,
                    communication_style = EXCLUDED.communication_style
                """),
                {
                    "id": str(p["id"]),
                    "name": p["name"],
                    "company_context": p["company_context"],
                    "personality_traits": p["personality_traits"],
                    "focus_areas": p["focus_areas"],
                    "communication_style": p["communication_style"]
                }
            )

    print("Intelligence seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_intelligence())
