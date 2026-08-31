from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from db.models import VernacularConcept

# Pre-seeded vernacular content for demonstration purposes
DEFAULT_CONCEPTS = [
    # ── Hindi (hi) ──
    {
        "language": "hi",
        "concept_key": "binary_search",
        "concept_name": "बाइनरी सर्च (Binary Search)",
        "translation": "एक सॉर्टेड लिस्ट में किसी वैल्यू को ढूंढने की एक कुशल विधि जो लिस्ट को आधा करती रहती है।",
        "local_analogy": "डिक्शनरी (शब्दकोश) में शब्द ढूंढना: आप हमेशा बीच का पन्ना खोलते हैं, यह देखने के लिए कि आपका शब्द आगे है या पीछे, और फिर आधे हिस्से को छोड़ देते हैं।",
        "explanation": "बाइनरी सर्च का उपयोग केवल सॉर्टेड एरे पर किया जा सकता है। यह हर कदम पर सर्च रेंज को आधा कर देता है, जिससे इसकी समय जटिलता O(log n) हो जाती है।"
    },
    {
        "language": "hi",
        "concept_key": "stack",
        "concept_name": "स्टैक (Stack - LIFO)",
        "translation": "एक डेटा संरचना जहां अंतिम जोड़ी गई वस्तु सबसे पहले निकाली जाती है।",
        "local_analogy": "शादी की पार्टी में प्लेटों का ढेर: जो प्लेट सबसे अंत में ऊपर रखी जाती है, उसे मेहमान सबसे पहले उठाते हैं (Last In, First Out)।",
        "explanation": "स्टैक में मुख्य रूप से दो क्रियाएं होती हैं: push (नया आइटम जोड़ना) और pop (शीर्ष आइटम निकालना)। दोनों क्रियाएं O(1) समय में होती हैं।"
    },
    {
        "language": "hi",
        "concept_key": "queue",
        "concept_name": "कतार / क्यू (Queue - FIFO)",
        "translation": "एक रैखिक डेटा संरचना जो First In, First Out के सिद्धांत पर कार्य करती है।",
        "local_analogy": "रेलवे टिकट काउंटर की लाइन: जो व्यक्ति पहले लाइन में खड़ा हुआ, उसे सबसे पहले टिकट मिलता है और वह पहले बाहर जाता है।",
        "explanation": "कतार में enqueue (पीछे जोड़ना) और dequeue (आगे से हटाना) ऑपरेशन O(1) समय में होते हैं।"
    },
    {
        "language": "hi",
        "concept_key": "dynamic_programming",
        "concept_name": "डायनामिक प्रोग्रामिंग (Dynamic Programming)",
        "translation": "जटिल समस्याओं को छोटी उप-समस्याओं में तोड़कर उनके परिणामों को संचित (memoize) करने की तकनीक।",
        "local_analogy": "पहाड़े (गुणा तालिका) याद रखना: 7 × 8 को बार-बार जोड़ने के बजाय आप सीधे 56 याद रखते हैं क्योंकि आपने पहले इसे हल किया हुआ है।",
        "explanation": "ओवरलैपिंग सब-प्रॉब्लम्स और ऑप्टिमल सबस्ट्रक्चर वाली समस्याओं में बार-बार गणना से बचने के लिए DP का उपयोग किया जाता है।"
    },
    # ── Telugu (te) ──
    {
        "language": "te",
        "concept_key": "binary_search",
        "concept_name": "బైనరీ సెర్చ్ (Binary Search)",
        "translation": "క్రమబద్ధీకరించిన జాబితాలో ఒక విలువను సగం సగం చేసుకుంటూ శోధించే సమర్థవంతమైన పద్ధతి.",
        "local_analogy": "డిక్షనరీలో పదం వెతకడం: ఎల్లప్పుడూ మధ్య పేజీని తెరిచి, పదం ముందుందో వెనుకందో చూసి మిగతా భాగాన్ని విడిచిపెట్టడం.",
        "explanation": "బైనరీ సెర్చ్ కేవలం క్రమబద్ధీకరించిన (Sorted) శ్రేణిపై పనిచేస్తుంది. దీని సమయ సంక్లిష్టత O(log n)."
    },
    {
        "language": "te",
        "concept_key": "stack",
        "concept_name": "స్టాక్ (Stack - LIFO)",
        "translation": "చివరగా చేర్చిన అంశం మొదట బయటకు వచ్చే డేటా నిర్మాణం.",
        "local_analogy": "పెళ్లి భోజనాలలో ప్లేట్ల వరుస: చివరగా పైన ఉంచిన ప్లేటును అతిథి మొదట తీసుకుంటారు.",
        "explanation": "స్టాక్ పుష్ (Push) మరియు పాప్ (Pop) ఆపరేషన్లను O(1) సమయంలో నిర్వహిస్తుంది."
    },
    {
        "language": "te",
        "concept_key": "queue",
        "concept_name": "క్యూ (Queue - FIFO)",
        "translation": "మొదట వచ్చినది మొదట సేవ చేయబడే క్రమబద్ధమైన డేటా నిర్మాణం.",
        "local_analogy": "సినిమా థియేటర్ టికెట్ కౌంటర్ వరుస: మొదట నిలబడిన వ్యక్తికి టికెట్ మొదట అందుతుంది.",
        "explanation": "క్యూ ఎన్‌క్యూ మరియు డిక్యూలను O(1) సమయంతో ఎడ్జస్ట్ చేస్తుంది."
    },
    # ── Tamil (ta) ──
    {
        "language": "ta",
        "concept_key": "binary_search",
        "concept_name": "பைனரி தேடல் (Binary Search)",
        "translation": "வரிசைப்படுத்தப்பட்ட பட்டியலில் ஒரு மதிப்பை பாதியாகப் பிரித்து தேடும் திறமையான முறை.",
        "local_analogy": "அகராதியில் சொல் தேடுவது: எப்போதும் நடுப்பக்கத்தைத் திறந்து சொல் முன்னா அல்லது பின்னா எனப் பார்த்து மீதியை ஒதுக்குவது.",
        "explanation": "வரிசைப்படுத்தப்பட்ட வரிசைகளில் (Sorted Arrays) மட்டுமே பயன்படுத்த முடியும். இதன் கால அளவு O(log n)."
    },
    {
        "language": "ta",
        "concept_key": "stack",
        "concept_name": "ஸ்டேக் (Stack - LIFO)",
        "translation": "கடைசியாகச் சேர்க்கப்பட்ட பொருள் முதலில் வெளியே எடுக்கப்படும் தரவுக் கட்டமைப்பு.",
        "local_analogy": "விருந்து மண்டபத்தில் தட்டுகள் அடுக்கு: கடைசியில் மேலே வைக்கப்படும் தட்டையே விருந்தினர் முதலில் எடுப்பார்.",
        "explanation": "Stack-இல் புஷ் (Push) மற்றும் பாப் (Pop) செயல்பாடுகள் O(1) நேரத்தில் நடைபெறுகின்றன."
    },
    # ── Kannada (kn) ──
    {
        "language": "kn",
        "concept_key": "binary_search",
        "concept_name": "ಬೈನರಿ ಸರ್ಚ್ (Binary Search)",
        "translation": "ವಿಂಗಡಿಸಲಾದ ಪಟ್ಟಿಯಲ್ಲಿ ಮೌಲ್ಯವನ್ನು ಅರ್ಧ ಭಾಗ ಕಡಿತಗೊಳಿಸುತ್ತಾ ಹುಡುಕುವ ವಿಧಾನ.",
        "local_analogy": "ಡಿಕ್ಷನರಿಯಲ್ಲಿ ಪದ ಹುಡುಕುವುದು: ಮಧ್ಯದ ಪುಟ ತೆರೆದು ಪದ ಮುಂದಿದೆಯೇ ಹಿಂದಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸುವುದು.",
        "explanation": "ಸಾರ್ಟ್ ಮಾಡಲಾದ ಅರೇಗಳಲ್ಲಿ ಮಾತ್ರ ಅನ್ವಯಿಸುತ್ತದೆ. ಇದರ ಸಂಕೀರ್ಣತೆ O(log n)."
    },
    {
        "language": "kn",
        "concept_key": "stack",
        "concept_name": "ಸ್ಟ್ಯಾಕ್ (Stack - LIFO)",
        "translation": "ಕೊನೆಯಲ್ಲಿ ಸೇರಿಸಿದ ವಸ್ತುವು ಮೊದಲಿಗೆ ಹೊರಬರುವ ಡಾಟಾ ರಚನೆ.",
        "local_analogy": "ಮದುವೆ ಮನೆಯ ಊಟದ ತಟ್ಟೆಗಳ ಸಾಲು: ಮೇಲೆ ಇಟ್ಟ ತಟ್ಟೆಯನ್ನು ಅತಿಥಿ ಮೊದಲು ಎತ್ತಿಕೊಳ್ಳುತ್ತಾರೆ.",
        "explanation": "ಸ್ಟ್ಯಾಕ್‌ನಲ್ಲಿ ಪುಷ್ ಮತ್ತು ಪಾಪ್ ಕಾರ್ಯಗಳು O(1) ಸಮಯದಲ್ಲಿ ನಡೆಯುತ್ತವೆ."
    }
]

async def seed_default_vernacular_concepts(db: AsyncSession) -> int:
    """Seeds default vernacular concepts if they are not already present."""
    seeded = 0
    for item in DEFAULT_CONCEPTS:
        stmt = select(VernacularConcept).where(
            and_(
                VernacularConcept.language == item["language"],
                VernacularConcept.concept_key == item["concept_key"]
            )
        )
        existing = (await db.execute(stmt)).scalars().first()
        if not existing:
            concept = VernacularConcept(
                language=item["language"],
                concept_key=item["concept_key"],
                concept_name=item["concept_name"],
                translation=item["translation"],
                local_analogy=item["local_analogy"],
                explanation=item["explanation"]
            )
            db.add(concept)
            seeded += 1
    if seeded > 0:
        await db.commit()
    return seeded

async def get_concepts_by_language(language: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """Retrieves all pre-defined concept listings in a given local language."""
    # Ensure seeded if empty
    await seed_default_vernacular_concepts(db)
    
    stmt = select(VernacularConcept).where(VernacularConcept.language == language)
    concepts = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "id": str(c.id),
            "concept_key": c.concept_key,
            "concept_name": c.concept_name,
            "translation": c.translation,
            "local_analogy": c.local_analogy,
            "explanation": c.explanation
        }
        for c in concepts
    ]

async def get_concept_details(language: str, concept_key: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieves a single concept in a given language by its key."""
    stmt = select(VernacularConcept).where(
        and_(
            VernacularConcept.language == language,
            VernacularConcept.concept_key == concept_key
        )
    )
    c = (await db.execute(stmt)).scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Concept not found in the selected language.")
        
    return {
        "id": str(c.id),
        "concept_key": c.concept_key,
        "concept_name": c.concept_name,
        "translation": c.translation,
        "local_analogy": c.local_analogy,
        "explanation": c.explanation
    }
