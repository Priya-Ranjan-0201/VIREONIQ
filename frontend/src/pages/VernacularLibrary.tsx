import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Sparkles, Languages, MessageSquare, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

interface VernacularConcept {
  id: string;
  language: string;
  concept_key: string;
  concept_name: string;
  translation: string;
  local_analogy: string | null;
  explanation: string;
}

const FALLBACK_CONCEPTS_MAP: Record<string, VernacularConcept[]> = {
  hi: [
    {
      id: 'fb-hi-1',
      language: 'hi',
      concept_key: 'binary_search',
      concept_name: 'बाइनरी सर्च (Binary Search)',
      translation: 'एक सॉर्टेड लिस्ट में किसी वैल्यू को ढूंढने की एक कुशल विधि जो लिस्ट को आधा करती रहती है।',
      local_analogy: 'डिक्शनरी (शब्दकोश) में शब्द ढूंढना: आप हमेशा बीच का पन्ना खोलते हैं, यह देखने के लिए कि आपका शब्द आगे है या पीछे, और फिर आधे हिस्से को छोड़ देते हैं।',
      explanation: 'बाइनरी सर्च का उपयोग केवल सॉर्टेड एरे पर किया जा सकता है। यह हर कदम पर सर्च रेंज को आधा कर देता है, जिससे इसकी समय जटिलता O(log n) हो जाती है।'
    },
    {
      id: 'fb-hi-2',
      language: 'hi',
      concept_key: 'stack',
      concept_name: 'स्टैक (Stack - LIFO)',
      translation: 'एक डेटा संरचना जहां अंतिम जोड़ी गई वस्तु सबसे पहले निकाली जाती है।',
      local_analogy: 'शादी की दावत में प्लेटों का ढेर: जो प्लेट सबसे अंत में ऊपर रखी जाती है, उसे मेहमान सबसे पहले उठाते हैं (Last In, First Out)।',
      explanation: 'स्टैक में मुख्य रूप से दो क्रियाएं होती हैं: push (नया आइटम जोड़ना) और pop (शीर्ष आइटम निकालना)। दोनों क्रियाएं O(1) समय में होती हैं।'
    },
    {
      id: 'fb-hi-3',
      language: 'hi',
      concept_key: 'queue',
      concept_name: 'कतार / क्यू (Queue - FIFO)',
      translation: 'एक रैखिक डेटा संरचना जो First In, First Out के सिद्धांत पर कार्य करती है।',
      local_analogy: 'रेलवे टिकट काउंटर की लाइन: जो व्यक्ति पहले लाइन में खड़ा हुआ, उसे सबसे पहले टिकट मिलता है और वह पहले बाहर जाता है।',
      explanation: 'कतार में enqueue (पीछे जोड़ना) और dequeue (आगे से हटाना) ऑपरेशन O(1) समय में होते हैं।'
    },
    {
      id: 'fb-hi-4',
      language: 'hi',
      concept_key: 'dynamic_programming',
      concept_name: 'डायनामिक प्रोग्रामिंग (Dynamic Programming)',
      translation: 'जटिल समस्याओं को छोटी उप-समस्याओं में तोड़कर उनके परिणामों को संचित (memoize) करने की तकनीक।',
      local_analogy: 'पहाड़े (गुणा तालिका) याद रखना: 7 × 8 को बार-बार जोड़ने के बजाय आप सीधे 56 याद रखते हैं क्योंकि आपने पहले इसे हल किया हुआ है।',
      explanation: 'ओवरलैपिंग सब-प्रॉब्लम्स और ऑप्टिमल सबस्ट्रक्चर वाली समस्याओं में बार-बार गणना से बचने के लिए DP का उपयोग किया जाता है।'
    }
  ],
  te: [
    {
      id: 'fb-te-1',
      language: 'te',
      concept_key: 'binary_search',
      concept_name: 'బైనరీ సెర్చ్ (Binary Search)',
      translation: 'క్రమబద్ధీకరించిన జాబితాలో ఒక విలువను సగం సగం చేసుకుంటూ శోధించే సమర్థవంతమైన పద్ధతి.',
      local_analogy: 'డిక్షనరీలో పదం వెతకడం: ఎల్లప్పుడూ మధ్య పేజీని తెరిచి, పదం ముందుందో వెనుకందో చూసి మిగతా భాగాన్ని విడిచిపెట్టడం.',
      explanation: 'బైనరీ సెర్చ్ కేవలం క్రమబద్ధీకరించిన శ్రేణిపై పనిచేస్తుంది. దీని సమయ సంక్లిష్టత O(log n).'
    },
    {
      id: 'fb-te-2',
      language: 'te',
      concept_key: 'stack',
      concept_name: 'స్టాక్ (Stack - LIFO)',
      translation: 'చివరగా చేర్చిన అంశం మొదట బయటకు వచ్చే డేటా నిర్మాణం.',
      local_analogy: 'పెళ్లి భోజనాలలో ప్లేట్ల వరుస: చివరగా పైన ఉంచిన ప్లేటును అతిథి మొదట తీసుకుంటారు.',
      explanation: 'స్టాక్ పుష్ (Push) మరియు పాప్ (Pop) ఆపరేషన్లను O(1) సమయంలో నిర్వహిస్తుంది.'
    },
    {
      id: 'fb-te-3',
      language: 'te',
      concept_key: 'queue',
      concept_name: 'క్యూ (Queue - FIFO)',
      translation: 'మొదట వచ్చినది మొదట సేవ చేయబడే క్రమబద్ధమైన డేటా నిర్మాణం.',
      local_analogy: 'సినిమా థియేటర్ టికెట్ కౌంటర్ వరుస: మొదట నిలబడిన వ్యక్తికి టికెట్ మొదట అందుతుంది.',
      explanation: 'క్యూ ఎన్‌క్యూ మరియు డిక్యూలను O(1) సమయంతో నిర్వహిస్తుంది.'
    }
  ],
  ta: [
    {
      id: 'fb-ta-1',
      language: 'ta',
      concept_key: 'binary_search',
      concept_name: 'பைனரி தேடல் (Binary Search)',
      translation: 'வரிசைப்படுத்தப்பட்ட பட்டியலில் ஒரு மதிப்பை பாதியாகப் பிரித்து தேடும் திறமையான முறை.',
      local_analogy: 'அகராதியில் சொல் தேடுவது: எப்போதும் நடுப்பக்கத்தைத் திறந்து சொல் முன்னா அல்லது பின்னா எனப் பார்த்து மீதியை ஒதுக்குவது.',
      explanation: 'வரிசைப்படுத்தப்பட்ட வரிசைகளில் மட்டுமே பயன்படுத்த முடியும். இதன் கால அளவு O(log n).'
    },
    {
      id: 'fb-ta-2',
      language: 'ta',
      concept_key: 'stack',
      concept_name: 'ஸ்டேக் (Stack - LIFO)',
      translation: 'கடைசியாகச் சேர்க்கப்பட்ட பொருள் முதலில் வெளியே எடுக்கப்படும் தரவுக் கட்டமைப்பு.',
      local_analogy: 'விருந்து மண்டபத்தில் தட்டுகள் அடுக்கு: கடைசியில் மேலே வைக்கப்படும் தட்டையே விருந்தினர் முதலில் எடுப்பார்.',
      explanation: 'Stack-இல் புஷ் மற்றும் பாப் செயல்பாடுகள் O(1) நேரத்தில் நடைபெறுகின்றன.'
    }
  ],
  kn: [
    {
      id: 'fb-kn-1',
      language: 'kn',
      concept_key: 'binary_search',
      concept_name: 'ಬೈನರಿ ಸರ್ಚ್ (Binary Search)',
      translation: 'ವಿಂಗಡಿಸಲಾದ ಪಟ್ಟಿಯಲ್ಲಿ ಮೌಲ್ಯವನ್ನು ಅರ್ಧ ಭಾಗ ಕಡಿತಗೊಳಿಸುತ್ತಾ ಹುಡುಕುವ ವಿಧಾನ.',
      local_analogy: 'ಡಿಕ್ಷನರಿಯಲ್ಲಿ ಪದ ಹುಡುಕುವುದು: ಮಧ್ಯದ ಪುಟ ತೆರೆದು ಪದ ಮುಂದಿದೆಯೇ ಹಿಂದಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸುವುದು.',
      explanation: 'ಸಾರ್ಟ್ ಮಾಡಲಾದ ಅರೇಗಳಲ್ಲಿ ಮಾತ್ರ ಅನ್ವಯಿಸುತ್ತದೆ. ಇದರ ಸಂಕೀರ್ಣತೆ O(log n).'
    },
    {
      id: 'fb-kn-2',
      language: 'kn',
      concept_key: 'stack',
      concept_name: 'ಸ್ಟ್ಯಾಕ್ (Stack - LIFO)',
      translation: 'ಕೊನೆಯಲ್ಲಿ ಸೇರಿಸಿದ ವಸ್ತುವು ಮೊದಲಿಗೆ ಹೊರಬರುವ ಡಾಟಾ ರಚನೆ.',
      local_analogy: 'ಮದುವೆ ಮನೆಯ ಊಟದ ತಟ್ಟೆಗಳ ಸಾಲು: ಮೇಲೆ ಇಟ್ಟ ತಟ್ಟೆಯನ್ನು ಅತಿಥಿ ಮೊದಲು ಎತ್ತಿಕೊಳ್ಳುತ್ತಾರೆ.',
      explanation: 'ಸ್ಟ್ಯಾಕ್‌ನಲ್ಲಿ ಪುಷ್ ಮತ್ತು ಪಾಪ್ ಕಾರ್ಯಗಳು O(1) ಸಮಯದಲ್ಲಿ ನಡೆಯುತ್ತವೆ.'
    }
  ]
};

export const VernacularLibrary = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('hi'); // Default: Hindi
  const [concepts, setConcepts] = useState<VernacularConcept[]>(FALLBACK_CONCEPTS_MAP.hi);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchConcepts();
  }, [selectedLanguage]);

  const fetchConcepts = async () => {
    setIsLoading(true);
    const fallbacks = FALLBACK_CONCEPTS_MAP[selectedLanguage] || FALLBACK_CONCEPTS_MAP.hi;
    try {
      const res = await api.get('/vernacular/concepts', {
        params: { language: selectedLanguage }
      });
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        setConcepts(res.data);
      } else {
        setConcepts(fallbacks);
      }
    } catch (e) {
      setConcepts(fallbacks);
    } finally {
      setIsLoading(false);
    }
  };

  const languages = [
    { code: 'hi', name: 'Hindi / हिन्दी' },
    { code: 'te', name: 'Telugu / తెలుగు' },
    { code: 'ta', name: 'Tamil / தமிழ்' },
    { code: 'kn', name: 'Kannada / ಕನ್ನಡ' }
  ];

  const filteredConcepts = concepts.filter(c =>
    c.concept_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.explanation.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
            Vernacular Concept Library
          </h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
            Learn core computer science concepts translated into local regional analogies & stories
          </p>
        </div>

        {/* Language Selector */}
        <div className="flex gap-2">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setSelectedLanguage(lang.code)}
              className={`px-3 py-2 rounded-2xl border text-xs font-bold transition ${
                selectedLanguage === lang.code
                  ? 'bg-primary text-slate-950 border-primary'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <Languages className="w-3.5 h-3.5 mr-1 inline-block" />
              {lang.name}
            </button>
          ))}
        </div>
      </header>

      {/* Search Panel */}
      <div className="glass-panel p-4 rounded-3xl">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search concepts or analogies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-950 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none text-sm"
          />
        </div>
      </div>

      {/* Main Concepts Display */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : filteredConcepts.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-xs border border-dashed border-slate-850 rounded-3xl">
          No concepts indexed for this language filter yet. Earn premium days by contributing!
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {filteredConcepts.map((concept) => (
            <div key={concept.id} className="glass-panel p-6 rounded-3xl space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex justify-between items-start border-b border-slate-850 pb-3">
                  <div>
                    <h3 className="text-base font-bold text-white">{concept.concept_name}</h3>
                    <span className="text-[10px] text-primary uppercase font-bold tracking-wider mt-1 block">
                      Translated: {concept.translation}
                    </span>
                  </div>
                  <Sparkles className="w-5 h-5 text-amber-400" />
                </div>

                <div className="space-y-2">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Local Analogy / Story</span>
                  <p className="text-xs text-slate-300 leading-relaxed italic bg-slate-905 p-3.5 border border-slate-850 rounded-2xl">
                    {concept.local_analogy || 'No analogy logged yet.'}
                  </p>
                </div>

                <div className="space-y-1.5">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Technical Explanation</span>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {concept.explanation}
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-850 flex justify-between items-center text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                <span>Concept Index: {concept.concept_key}</span>
                <span>Ready for interview</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default VernacularLibrary;
