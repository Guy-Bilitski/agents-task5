"""Data generation for RAG experiment (Hebrew)."""

import random
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Document:
    id: int
    domain: str
    text: str
    has_needle: bool
    needle_fact: str = ""

# Simple Hebrew filler templates
TEMPLATES = {
    "medicine": [
        "המחקר הרפואי מתקדם בצעדי ענק בשנים האחרונות.",
        "רופאים ממליצים על תזונה מאוזנת ופעילות גופנית סדירה.",
        "בתי החולים עמוסים במטופלים הזקוקים לטיפול דחוף.",
        "תרופות חדשות נכנסות לסל הבריאות מדי שנה.",
        "מערכת החיסון היא קו ההגנה הראשון של הגוף.",
        "בדיקות דם שגרתיות יכולות למנוע מחלות רבות.",
        "התפתחות הטכנולוגיה הרפואית מאפשרת ניתוחים מורכבים.",
        "בריאות הנפש היא חלק בלתי נפרד מהבריאות הכללית.",
        "ויטמינים ומינרלים חיוניים לתפקוד התקין של הגוף.",
        "הצוות הרפואי עובד מסביב לשעון להצלת חיים."
    ],
    "law": [
        "בית המשפט פסק לטובת התובע לאחר דיון ארוך.",
        "חוק החוזים מחייב תום לב במשא ומתן לקראת כריתת חוזה.",
        "עורכי דין מייצגים את לקוחותיהם בערכאות השונות.",
        "החקיקה החדשה נועדה להגן על זכויות הצרכן.",
        "דיני קניין רוחני עוסקים בהגנה על יצירות ומותגים.",
        "רשלנות רפואית היא עילה לתביעה נזיקית.",
        "בית המשפט העליון קבע תקדים משפטי מחייב.",
        "הסכמים בינלאומיים מחייבים את המדינות החתומות עליהם.",
        "זכויות אדם הן נר לרגליה של הדמוקרטיה.",
        "הליך הגישור מאפשר פתרון סכסוכים מחוץ לכותלי בית המשפט."
    ],
    "technology": [
        "בינה מלאכותית משנה את הדרך בה אנו עובדים ולומדים.",
        "אבטחת מידע היא אתגר מרכזי בארגונים גדולים.",
        "מחשוב ענן מאפשר גמישות ויעילות בעבודה מרחוק.",
        "רשתות חברתיות מחברות בין אנשים מכל רחבי העולם.",
        "האינטרנט של הדברים מחבר מכשירים יומיומיים לרשת.",
        "פיתוח תוכנה דורש חשיבה לוגית ויצירתיות.",
        "אלגוריתמים מתקדמים מפעילים את מנועי החיפוש.",
        "טכנולוגיית הבלוקצ'יין מבטיחה שקיפות ואמינות.",
        "רובוטיקה מתקדמת משתלבת בתעשייה ובחיי היומיום.",
        "מציאות מדומה פותחת אפשרויות חדשות במשחקים ובהדרכה."
    ]
}

def generate_filler_text(domain: str, min_words: int) -> str:
    """Generate random filler text for a specific domain."""
    templates = TEMPLATES.get(domain, TEMPLATES["technology"])
    text_parts = []
    current_words = 0
    
    while current_words < min_words:
        sentence = random.choice(templates)
        text_parts.append(sentence)
        current_words += len(sentence.split())
        
    return " ".join(text_parts)

def generate_dataset(config) -> List[Document]:
    """
    Generate a dataset of documents.
    
    Args:
        config: DatasetConfig object
        
    Returns:
        List of Document objects
    """
    documents = []
    
    # Create list of domains for all docs
    # 1 Target (Medicine), Rest Distractors
    domains = [config.target_domain] 
    
    # Fill the rest with distractors
    num_distractors = config.total_docs - 1
    for _ in range(num_distractors):
        domains.append(random.choice(config.distractor_domains))
        
    # Shuffle to randomize where the target domain appears (optional, but we force needle index)
    # However, the config says `needle.doc_index` is fixed. So let's respect that.
    # We will force the document at `doc_index` to be the target domain.
    
    # Re-build domains list to guarantee target at index
    final_domains = [random.choice(config.distractor_domains) for _ in range(config.total_docs)]
    final_domains[config.needle.doc_index] = config.target_domain
    
    for i in range(config.total_docs):
        domain = final_domains[i]
        is_needle_doc = (i == config.needle.doc_index)
        
        # Generate base text
        text = generate_filler_text(domain, config.doc_length_words)
        
        # Insert needle if it's the target doc
        needle_fact = ""
        if is_needle_doc:
            needle_fact = config.needle.fact
            # Insert somewhere in the middle to make it "searchable"
            words = text.split()
            insert_pos = len(words) // 2
            words.insert(insert_pos, needle_fact)
            text = " ".join(words)
            
        documents.append(Document(
            id=i,
            domain=domain,
            text=text,
            has_needle=is_needle_doc,
            needle_fact=needle_fact
        ))
        
    return documents
