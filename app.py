import io
import json

import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Short Film Studio",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            160deg, #100c20 0%, #171326 55%, #0c1020 100%
        );
    }

    .block-container {
        max-width: 1100px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label, .stMarkdown {
        color: #f4efff;
    }

    div[data-testid="stMetric"] {
        background: #241d37;
        padding: 12px;
        border-radius: 12px;
    }

    div[data-testid="stTabs"] button {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎬 AI Short Film Studio")

st.caption(
    "วางพล็อต แบ่งฉาก สร้าง Prompt และสร้างภาพประกอบ "
    "สำหรับการผลิตหนังสั้นด้วย AI"
)

# =========================================================
# CONSTANTS
# =========================================================

TEXT_MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-3.1-flash-image"

GENRES = [
    "แอ็กชัน",
    "ผจญภัย",
    "ดราม่า",
    "ตลก",
    "โรแมนติก",
    "โรแมนติกคอมเมดี้",
    "เมโลดราม่า",
    "ชีวิตประจำวัน",
    "ครอบครัว",
    "มิตรภาพ",
    "วัยรุ่น",
    "Coming of Age",
    "ฟีลกู๊ด",
    "สร้างแรงบันดาลใจ",
    "โศกนาฏกรรม",
    "สืบสวน",
    "นักสืบ",
    "อาชญากรรม",
    "ฆาตกรรมปริศนา",
    "ระทึกขวัญ",
    "จิตวิทยาระทึกขวัญ",
    "แก้แค้น",
    "ปล้น",
    "สายลับ",
    "ตำรวจ",
    "มาเฟีย",
    "ศาลและกฎหมาย",
    "การเมือง",
    "สมคบคิด",
    "เอาชีวิตรอด",
    "เกมมรณะ",
    "สยองขวัญ",
    "ผีไทย",
    "ผีญี่ปุ่น",
    "ผีเกาหลี",
    "บ้านผีสิง",
    "ไสยศาสตร์",
    "คำสาป",
    "ปีศาจ",
    "ซอมบี้",
    "แวมไพร์",
    "แฟนตาซี",
    "ดาร์กแฟนตาซี",
    "เวทมนตร์",
    "เทพปกรณัม",
    "ตำนานพื้นบ้าน",
    "กำลังภายใน",
    "จอมยุทธ์",
    "โลกคู่ขนาน",
    "ต่างโลก",
    "ทะลุมิติ",
    "เกิดใหม่",
    "ย้อนอดีต",
    "ไซไฟ",
    "โลกอนาคต",
    "โลกดิสโทเปีย",
    "ไซเบอร์พังก์",
    "หุ่นยนต์",
    "ปัญญาประดิษฐ์",
    "การเดินทางข้ามเวลา",
    "มนุษย์ต่างดาว",
    "โลกหลังหายนะ",
    "ภัยพิบัติ",
    "รักแรก",
    "รักวัยเรียน",
    "รักต้องห้าม",
    "รักสามเส้า",
    "คู่กัดกลายเป็นคู่รัก",
    "รักเหนือกาลเวลา",
    "ย้อนยุค",
    "พีเรียดไทย",
    "พีเรียดจีน",
    "พีเรียดเกาหลี",
    "พีเรียดญี่ปุ่น",
    "ประวัติศาสตร์",
    "สงคราม",
    "ซามูไร",
    "ราชวงศ์",
    "วังหลวง",
    "อนิเมะแอ็กชัน",
    "อนิเมะแฟนตาซี",
    "อนิเมะโรแมนติก",
    "อนิเมะสยองขวัญ",
    "กีฬา",
    "ดนตรี",
    "สารคดี",
    "ชีวประวัติ",
    "การทำอาหาร",
    "การเดินทาง",
    "ธรรมชาติและสัตว์",
    "โจรสลัด",
    "มิวสิคัล",
    "เสียดสีสังคม",
    "เหนือจริง",
    "หนังสั้นหักมุม",
    "แฟนตาซีโรแมนติก",
    "แอ็กชันคอมเมดี้",
    "การทรยศและหักหลัง",
    "ตัวร้ายเป็นตัวเอก",
    "หักมุมหลายชั้น",
]

MOODS = [
    "Cinematic, dramatic lighting",
    "Hollywood blockbuster",
    "Epic and majestic",
    "Dark and gritty realism",
    "Photorealistic cinematic style",
    "Vintage 35mm film",
    "Film noir, black and white",
    "Warm and nostalgic",
    "Romantic and dreamy",
    "Melancholic and emotional",
    "Dark and suspenseful",
    "Dreamlike and surreal",
    "Bright and whimsical",
    "Mysterious and atmospheric",
    "Peaceful and relaxing",
    "Hopeful and inspiring",
    "Tense and claustrophobic",
    "Golden hour lighting",
    "Soft natural lighting",
    "Dramatic shadows and high contrast",
    "Cool blue cinematic tones",
    "Warm golden color grading",
    "Pastel color palette",
    "Neon lighting",
    "Volumetric fog and light rays",
    "Rainy night atmosphere",
    "Moonlight and silver tones",
    "Epic fantasy concept art",
    "Dark fantasy",
    "Magical glowing atmosphere",
    "Chinese cultivation fantasy",
    "Wuxia martial arts cinema",
    "Cyberpunk neon",
    "Futuristic sci-fi",
    "Dystopian future",
    "Psychological horror",
    "Gothic horror",
    "Eerie haunted atmosphere",
    "Survival thriller",
    "Korean drama cinematic style",
    "Japanese romance film style",
    "Chinese historical drama style",
    "Historical period film",
    "Japanese anime cinematic style",
    "Anime fantasy",
    "Hand-painted watercolor",
    "Painterly concept art",
    "3D animated film style",
    "Stop-motion animation",
    "Minimalist cinematic style",
    "Surreal cinematic aesthetic",
    "Dark academia",
    "Music video cinematic style",
]

# =========================================================
# LANGUAGE SYSTEM
# =========================================================

LANGUAGES = {
    "ไทยมาตรฐาน": {
        "instruction": "Natural contemporary Standard Thai",
        "regions": [
            "ไทยมาตรฐาน",
            "ภาษาพูดธรรมชาติ",
            "สุภาพ",
            "กันเอง",
        ],
    },
    "ไทยเหนือ / คำเมือง": {
        "instruction": (
            "Northern Thai Kham Mueang dialect. "
            "Use natural regional expressions."
        ),
        "regions": [
            "เชียงใหม่",
            "เชียงราย",
            "ลำพูน",
            "ลำปาง",
            "พะเยา",
            "แพร่",
            "น่าน",
            "แม่ฮ่องสอน",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยอีสาน": {
        "instruction": (
            "Natural spoken Isan Thai dialect. "
            "Use regionally appropriate expressions."
        ),
        "regions": [
            "ขอนแก่น",
            "อุดรธานี",
            "อุบลราชธานี",
            "ร้อยเอ็ด",
            "สกลนคร",
            "นครพนม",
            "มหาสารคาม",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยอีสานใต้": {
        "instruction": (
            "Southern Isan Thai speech. "
            "Use plausible local expressions."
        ),
        "regions": [
            "บุรีรัมย์",
            "สุรินทร์",
            "ศรีสะเกษ",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยโคราช": {
        "instruction": (
            "Khorat Thai dialect, naturally blended "
            "with Central Thai where appropriate."
        ),
        "regions": [
            "นครราชสีมา",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยใต้": {
        "instruction": (
            "Natural colloquial Southern Thai dialect."
        ),
        "regions": [
            "สงขลา",
            "นครศรีธรรมราช",
            "พัทลุง",
            "ตรัง",
            "ภูเก็ต",
            "กระบี่",
            "สุราษฎร์ธานี",
            "ปัตตานี",
            "ยะลา",
            "นราธิวาส",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยใต้ตอนบน": {
        "instruction": "Upper Southern Thai dialect",
        "regions": [
            "สุราษฎร์ธานี",
            "ชุมพร",
            "ระนอง",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยใต้ตอนล่าง": {
        "instruction": "Lower Southern Thai dialect",
        "regions": [
            "สงขลา",
            "พัทลุง",
            "ตรัง",
            "สตูล",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยตะวันออก": {
        "instruction": "Eastern Thai regional speech",
        "regions": [
            "ชลบุรี",
            "ระยอง",
            "จันทบุรี",
            "ตราด",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยตะวันตก": {
        "instruction": "Western Thai regional speech",
        "regions": [
            "กาญจนบุรี",
            "ราชบุรี",
            "เพชรบุรี",
            "ประจวบคีรีขันธ์",
            "ไม่ระบุพื้นที่",
        ],
    },
    "มลายูถิ่นปาตานี": {
        "instruction": (
            "Patani Malay. Do not substitute standard Thai."
        ),
        "regions": [
            "ปัตตานี",
            "ยะลา",
            "นราธิวาส",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ภาษาเจ๊ะเห": {
        "instruction": (
            "Jehe local language variety. Avoid inventing "
            "obscure vocabulary when uncertain."
        ),
        "regions": [
            "ตากใบ",
            "นราธิวาส",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ไทยผสมอังกฤษ": {
        "instruction": (
            "Natural Thai-English code-switching."
        ),
        "regions": [
            "กรุงเทพฯ / เมืองใหญ่",
            "วัยรุ่น",
            "ที่ทำงาน",
            "ไม่ระบุบริบท",
        ],
    },
    "เหนือผสมไทยกลาง": {
        "instruction": (
            "Blend Northern Thai and Central Thai naturally."
        ),
        "regions": [
            "เชียงใหม่",
            "เชียงราย",
            "ไม่ระบุพื้นที่",
        ],
    },
    "อีสานผสมไทยกลาง": {
        "instruction": (
            "Blend Isan Thai and Central Thai naturally."
        ),
        "regions": [
            "ภาคอีสาน",
            "คนย้ายถิ่น",
            "ไม่ระบุพื้นที่",
        ],
    },
    "ใต้ผสมไทยกลาง": {
        "instruction": (
            "Blend Southern Thai and Central Thai naturally."
        ),
        "regions": [
            "ภาคใต้",
            "คนย้ายถิ่น",
            "ไม่ระบุพื้นที่",
        ],
    },
    "中文（普通话）": {
        "instruction": (
            "Natural Mandarin Chinese using Simplified Chinese."
        ),
        "regions": [
            "普通话",
            "北京口音",
            "台湾普通话",
            "新加坡华语",
        ],
    },
    "简体中文": {
        "instruction": (
            "Natural modern Mandarin written in Simplified Chinese."
        ),
        "regions": [
            "中国大陆",
            "新加坡",
            "不指定地区",
        ],
    },
    "繁體中文": {
        "instruction": (
            "Natural Traditional Chinese wording."
        ),
        "regions": [
            "台灣",
            "香港書面語",
            "澳門",
            "不指定地區",
        ],
    },
    "廣東話 / Cantonese": {
        "instruction": (
            "Natural spoken Cantonese using Traditional Chinese "
            "characters and colloquial Cantonese wording."
        ),
        "regions": [
            "香港",
            "廣州",
            "澳門",
            "不指定地區",
        ],
    },
    "ฮกเกี้ยน": {
        "instruction": (
            "Hokkien language. Avoid inventing uncertain vocabulary."
        ),
        "regions": [
            "ไต้หวัน",
            "สิงคโปร์ / มาเลเซีย",
            "ไม่ระบุพื้นที่",
        ],
    },
    "แต้จิ๋ว": {
        "instruction": (
            "Teochew language. Avoid inventing uncertain vocabulary."
        ),
        "regions": [
            "จีนแต้จิ๋ว",
            "ไทยเชื้อสายแต้จิ๋ว",
            "ไม่ระบุพื้นที่",
        ],
    },
    "English": {
        "instruction": "Natural contemporary English",
        "regions": [
            "International English",
            "Casual",
            "Formal",
        ],
    },
    "English (US)": {
        "instruction": "Natural American English",
        "regions": [
            "General American",
            "Southern US",
            "New York",
        ],
    },
    "English (UK)": {
        "instruction": "Natural British English",
        "regions": [
            "Received Pronunciation",
            "London",
            "Northern England",
            "Scottish English",
            "Welsh English",
        ],
    },
    "English (Australia)": {
        "instruction": "Natural Australian English",
        "regions": [
            "General Australian",
            "Casual Australian",
        ],
    },
    "English (India)": {
        "instruction": "Natural Indian English",
        "regions": [
            "General Indian English",
            "Urban conversational",
        ],
    },
    "日本語": {
        "instruction": (
            "Natural Japanese with appropriate politeness and register."
        ),
        "regions": [
            "標準語",
            "関西弁",
            "丁寧語",
            "カジュアル",
        ],
    },
    "한국어": {
        "instruction": (
            "Natural Korean with appropriate speech levels and honorifics."
        ),
        "regions": [
            "표준어",
            "서울말",
            "경상도 사투리",
            "존댓말",
            "반말",
        ],
    },
    "Français": {
        "instruction": "Natural contemporary French",
        "regions": [
            "France",
            "Québec",
            "Belgium",
            "Casual",
            "Formal",
        ],
    },
    "Deutsch": {
        "instruction": "Natural contemporary German",
        "regions": [
            "Germany",
            "Austria",
            "Switzerland",
            "Casual",
            "Formal",
        ],
    },
    "Español": {
        "instruction": "Natural Spanish",
        "regions": [
            "España",
            "México",
            "Argentina",
            "Colombia",
            "Neutral Latin American Spanish",
        ],
    },
    "Português": {
        "instruction": "Natural Portuguese",
        "regions": [
            "Brasil",
            "Portugal",
            "Neutral",
        ],
    },
    "Italiano": {
        "instruction": "Natural contemporary Italian",
        "regions": [
            "Standard Italian",
            "Casual",
            "Formal",
        ],
    },
    "Русский": {
        "instruction": "Natural contemporary Russian",
        "regions": [
            "Standard Russian",
            "Casual",
            "Formal",
        ],
    },
    "العربية": {
        "instruction": (
            "Natural Arabic following the selected dialect or register."
        ),
        "regions": [
            "Modern Standard Arabic",
            "Egyptian Arabic",
            "Levantine Arabic",
            "Gulf Arabic",
            "Moroccan Arabic",
        ],
    },
    "हिन्दी": {
        "instruction": "Natural Hindi using Devanagari script",
        "regions": [
            "Standard Hindi",
            "Conversational",
            "Mumbai Hindi",
        ],
    },
    "Bahasa Indonesia": {
        "instruction": "Natural contemporary Indonesian",
        "regions": [
            "Bahasa Indonesia baku",
            "Percakapan sehari-hari",
        ],
    },
    "Bahasa Melayu": {
        "instruction": "Natural contemporary Malay",
        "regions": [
            "Malaysia",
            "Brunei",
            "Formal",
            "Colloquial",
        ],
    },
    "Tiếng Việt": {
        "instruction": "Natural Vietnamese",
        "regions": [
            "Northern",
            "Central",
            "Southern",
            "Standard",
        ],
    },
    "ພາສາລາວ": {
        "instruction": "Natural Lao language",
        "regions": [
            "เวียงจันทน์",
            "หลวงพระบาง",
            "ภาษาพูดทั่วไป",
        ],
    },
    "ភាសាខ្មែរ": {
        "instruction": "Natural Khmer language",
        "regions": [
            "Standard Khmer",
            "Conversational",
        ],
    },
    "မြန်မာဘာသာ": {
        "instruction": "Natural Burmese language",
        "regions": [
            "Standard Burmese",
            "Conversational",
        ],
    },
    "Filipino": {
        "instruction": "Natural Filipino / Tagalog",
        "regions": [
            "Standard Filipino",
            "Manila colloquial",
            "Taglish",
        ],
    },
    "Türkçe": {
        "instruction": "Natural contemporary Turkish",
        "regions": [
            "Standard Turkish",
            "Casual",
            "Formal",
        ],
    },
    "Nederlands": {
        "instruction": "Natural Dutch",
        "regions": [
            "Netherlands",
            "Belgium / Flemish",
            "Casual",
            "Formal",
        ],
    },
    "Polski": {
        "instruction": "Natural contemporary Polish",
        "regions": [
            "Standard Polish",
            "Casual",
            "Formal",
        ],
    },
    "Українська": {
        "instruction": "Natural contemporary Ukrainian",
        "regions": [
            "Standard Ukrainian",
            "Conversational",
        ],
    },
    "বাংলা": {
        "instruction": "Natural Bengali using Bengali script",
        "regions": [
            "Bangladesh",
            "West Bengal",
            "Standard",
        ],
    },
    "اردو": {
        "instruction": "Natural Urdu using Urdu script",
        "regions": [
            "Standard Urdu",
            "Conversational",
        ],
    },
    "فارسی": {
        "instruction": "Natural Persian / Farsi",
        "regions": [
            "Iranian Persian",
            "Conversational",
        ],
    },
    "Ελληνικά": {
        "instruction": "Natural contemporary Greek",
        "regions": [
            "Standard Greek",
            "Conversational",
        ],
    },
    "Svenska": {
        "instruction": "Natural Swedish",
        "regions": [
            "Standard Swedish",
            "Conversational",
        ],
    },
    "Norsk": {
        "instruction": "Natural Norwegian",
        "regions": [
            "Bokmål",
            "Nynorsk",
            "Conversational",
        ],
    },
    "Dansk": {
        "instruction": "Natural Danish",
        "regions": [
            "Standard Danish",
            "Conversational",
        ],
    },
    "Suomi": {
        "instruction": "Natural Finnish",
        "regions": [
            "Standard Finnish",
            "Conversational",
        ],
    },
}

# =========================================================
# HELPERS
# =========================================================


def get_saved_api_key():
    """อ่าน API key จาก Streamlit Secrets หากมี"""
    try:
        return str(
            st.secrets.get("GEMINI_API_KEY", "")
        ).strip()
    except Exception:
        return ""


def distribute_duration(total_seconds, count):
    """แบ่งระยะเวลาให้ทุกฉากรวมกันเท่ากับเวลาที่กำหนด"""
    if count <= 0:
        return []

    base, remainder = divmod(total_seconds, count)

    return [
        base + (1 if index < remainder else 0)
        for index in range(count)
    ]


def normalize_plan(plan, target_count, target_duration):
    """ตรวจสอบและจัดรูปแบบข้อมูลที่ AI ส่งกลับมา"""

    if not isinstance(plan, dict):
        raise ValueError("ข้อมูลแผนจาก AI ไม่ใช่ JSON object")

    raw_scenes = plan.get("scenes")

    if not isinstance(raw_scenes, list) or not raw_scenes:
        raise ValueError("AI ไม่ได้ส่งรายการฉากกลับมา")

    if len(raw_scenes) < target_count:
        raise ValueError(
            f"AI ส่งมาเพียง {len(raw_scenes)} ฉาก "
            f"แต่ต้องการ {target_count} ฉาก กรุณาลองใหม่"
        )

    durations = distribute_duration(
        target_duration,
        target_count,
    )

    normalized_scenes = []

    for index, scene in enumerate(raw_scenes[:target_count]):
        if not isinstance(scene, dict):
            scene = {}

        normalized_scenes.append(
            {
                "scene_number": index + 1,
                "scene_title": str(
                    scene.get("scene_title")
                    or f"ฉากที่ {index + 1}"
                ),
                "purpose": str(scene.get("purpose") or ""),
                "visual_prompt": str(
                    scene.get("visual_prompt") or ""
                ),
                "video_prompt": str(
                    scene.get("video_prompt") or ""
                ),
                "voiceover": str(
                    scene.get("voiceover") or ""
                ),
                "duration_seconds": durations[index],
            }
        )

    plan.update(
        {
            "title": str(
                plan.get("title") or "เรื่องของฉัน"
            ),
            "genre": str(
                plan.get("genre") or "ดราม่า"
            ),
            "logline": str(plan.get("logline") or ""),
            "duration_seconds": target_duration,
            "visual_style": str(
                plan.get("visual_style") or ""
            ),
            "notes": str(plan.get("notes") or ""),
            "scenes": normalized_scenes,
        }
    )

    return plan


# =========================================================
# TEMPLATE STORY GENERATOR
# ไม่ต้องใช้ API สำหรับสร้างโครงเรื่องพื้นฐาน
# =========================================================


def fallback_story(
    title,
    genre,
    idea,
    scene_count,
    duration,
    mood,
    language,
    style_notes,
    region="",
    multilingual=False,
    character_languages="",
):
    is_thai = language in LANGUAGES and language.startswith(
        (
            "ไทย",
            "เหนือ",
            "อีสาน",
            "ใต้",
            "มลายู",
            "ภาษาเจ๊ะ",
        )
    )

    beats_th = [
        (
            "เปิดเรื่อง",
            "แนะนำตัวละครและสถานที่ พร้อมภาพกว้างสร้างบรรยากาศ",
        ),
        (
            "สัญญาณแรก",
            "ตัวละครพบสิ่งผิดปกติที่เกี่ยวข้องกับไอเดียหลัก",
        ),
        (
            "ความขัดแย้ง",
            "เบาะแสใหม่ทำให้ตัวละครต้องตัดสินใจ",
        ),
        (
            "จุดพลิกผัน",
            "ความจริงเปลี่ยนความเข้าใจของตัวละคร",
        ),
        (
            "บทสรุป",
            "ปิดเรื่องด้วยภาพจำและอารมณ์ที่ชัดเจน",
        ),
        (
            "ผลสะเทือน",
            "แสดงผลลัพธ์จากการตัดสินใจ",
        ),
        (
            "เงื่อนงำใหม่",
            "ทิ้งคำถามให้ผู้ชมตีความ",
        ),
        (
            "เผชิญหน้า",
            "ตัวละครเผชิญหน้ากับอุปสรรคสำคัญ",
        ),
        (
            "ช่วงเงียบ",
            "ใช้ภาพและเสียงแทนบทพูด",
        ),
        (
            "ตอนจบ",
            "จบด้วยภาพที่สอดคล้องกับธีมเรื่อง",
        ),
    ]

    beats_en = [
        (
            "Opening",
            "Introduce the protagonist and establish the setting",
        ),
        (
            "First Signal",
            "Reveal an unusual clue related to the main idea",
        ),
        (
            "Conflict",
            "A new discovery forces the protagonist to decide",
        ),
        (
            "Turning Point",
            "A revelation changes the protagonist's understanding",
        ),
        (
            "Resolution",
            "Close with a memorable image and emotional impact",
        ),
        (
            "Consequences",
            "Show the result of the protagonist's decision",
        ),
        (
            "New Clue",
            "Leave a question for the audience to interpret",
        ),
        (
            "Confrontation",
            "Face the central obstacle",
        ),
        (
            "Silent Moment",
            "Use visuals and sound instead of dialogue",
        ),
        (
            "Ending",
            "Finish with an image that reinforces the theme",
        ),
    ]

    beats = beats_th if is_thai else beats_en

    durations = distribute_duration(
        duration,
        scene_count,
    )

    scenes = []

    for index in range(scene_count):
        name, beat = beats[index % len(beats)]

        scenes.append(
            {
                "scene_number": index + 1,
                "scene_title": name,
                "purpose": beat,
                "visual_prompt": (
                    f"Cinematic film still, {genre}. "
                    f"Story concept: {idea}. "
                    f"Scene {index + 1}: {beat}. "
                    f"Visual style: {mood}. "
                    f"{style_notes}. "
                    "Consistent character design, coherent setting, "
                    "cinematic composition, detailed environment, "
                    "realistic lighting, no text or logos."
                ),
                "video_prompt": (
                    f"Create a {durations[index]}-second cinematic shot. "
                    f"Story: {idea}. "
                    f"Action: {beat}. "
                    f"Visual mood: {mood}. "
                    "Use intentional camera movement, natural motion, "
                    "consistent character appearance, "
                    "no subtitles or logos."
                ),
                "voiceover": (
                    "บรรยายสั้น ๆ เพื่อเชื่อมอารมณ์ของฉาก"
                    if is_thai
                    else "A short voiceover to connect the scene emotionally."
                ),
                "duration_seconds": durations[index],
            }
        )

    if is_thai:
        logline = (
            f"{idea.strip()} — เรื่องแนว{genre} "
            f"ที่เล่าด้วยโทน {mood}"
        )
    else:
        logline = (
            f"{idea.strip()} — a {genre} short film "
            f"with a {mood} mood."
        )

    return {
        "title": title,
        "genre": genre,
        "logline": logline,
        "duration_seconds": duration,
        "visual_style": mood,
        "notes": style_notes,
        "scenes": scenes,
        "language": language,
        "dialect_region": region,
        "multilingual": multilingual,
        "character_languages": character_languages,
        "template_notice": (
            "โหมดเทมเพลตสร้างโครงฉากพื้นฐาน "
            "หากต้องการบทพูดภาษาถิ่นหรือภาษาต่างประเทศ "
            "ที่เป็นธรรมชาติ แนะนำให้เปิด Gemini API"
        ),
    }


# =========================================================
# GEMINI TEXT GENERATION
# =========================================================


def gemini_story(
    api_key,
    title,
    genre,
    idea,
    scene_count,
    duration,
    mood,
    language,
    style_notes,
    region="",
    multilingual=False,
    character_languages="",
):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    language_info = LANGUAGES.get(
        language,
        {
            "instruction": language,
            "regions": [],
        },
    )

    region_text = region or "ไม่ระบุพื้นที่หรือสำเนียงเพิ่มเติม"

    if multilingual:
        language_rule = (
            f"Main narration and story metadata should be written in "
            f"{language}. The story may use multiple languages. "
            "Use each character's specified language/dialect in their "
            "spoken dialogue. Keep each line in its intended language. "
            "Do not translate every line unless requested. "
            "Add a brief parenthetical translation only when useful."
        )
    else:
        language_rule = (
            f"Write all story text, scene titles, purpose, voiceover, "
            f"and dialogue in {language}. "
            f"Follow this language guidance: "
            f"{language_info['instruction']}."
        )

    schema = {
        "type": "OBJECT",
        "properties": {
            "title": {
                "type": "STRING",
            },
            "genre": {
                "type": "STRING",
            },
            "logline": {
                "type": "STRING",
            },
            "duration_seconds": {
                "type": "INTEGER",
            },
            "visual_style": {
                "type": "STRING",
            },
            "notes": {
                "type": "STRING",
            },
            "scenes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "scene_number": {
                            "type": "INTEGER",
                        },
                        "scene_title": {
                            "type": "STRING",
                        },
                        "purpose": {
                            "type": "STRING",
                        },
                        "visual_prompt": {
                            "type": "STRING",
                        },
                        "video_prompt": {
                            "type": "STRING",
                        },
                        "voiceover": {
                            "type": "STRING",
                        },
                        "duration_seconds": {
                            "type": "INTEGER",
                        },
                    },
                    "required": [
                        "scene_number",
                        "scene_title",
                        "purpose",
                        "visual_prompt",
                        "video_prompt",
                        "voiceover",
                        "duration_seconds",
                    ],
                },
            },
        },
        "required": [
            "title",
            "genre",
            "logline",
            "duration_seconds",
            "visual_style",
            "notes",
            "scenes",
        ],
    }

    prompt = f"""
You are an expert short-film writer and pre-production assistant.

LANGUAGE RULE:
{language_rule}

Selected language/dialect:
{language}

Language-specific guidance:
{language_info['instruction']}

Dialect/region variant:
{region_text}

Multilingual dialogue enabled:
{multilingual}

Character language assignments:
{character_languages or 'No character-specific assignments. Use the main language.'}

Return exactly {scene_count} scenes.
The target total runtime is {duration} seconds.

Every scene must contain:
scene_number, scene_title, purpose, visual_prompt,
video_prompt, voiceover, duration_seconds.

Divide the runtime evenly.
Create a coherent beginning, middle, turning point, and ending.
Make every scene distinct and suitable for general audiences.

IMPORTANT PROMPT LANGUAGE SEPARATION:
- Scene titles, purpose, voiceover, and dialogue follow the requested language and dialect rules.
- visual_prompt and video_prompt must be written in clear, detailed ENGLISH.
- Keep dialogue in the requested language, even though visual prompts are English.
- Do not put dialect spellings or dialogue into visual_prompt unless visually necessary.
- Keep character appearance, clothing, setting, and lighting consistent.
- Include concise dialogue in voiceover only when useful.
- Identify speakers by name where appropriate.
- Do not invent obscure dialect words if uncertain.
- Use natural, regionally plausible speech.

Film title: {title}
Genre: {genre}
Story idea: {idea}
Visual mood: {mood}
Additional notes: {style_notes}
"""

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=schema,
            temperature=0.8,
        ),
    )

    if not response.text:
        raise ValueError("Gemini ไม่ได้ส่งข้อความกลับมา")

    plan = normalize_plan(
        json.loads(response.text),
        scene_count,
        duration,
    )

    plan["language"] = language
    plan["dialect_region"] = region
    plan["multilingual"] = multilingual
    plan["character_languages"] = character_languages

    return plan


# =========================================================
# GEMINI API ERROR HANDLING
# =========================================================


def explain_api_error(error):
    message = str(error)
    lower = message.lower()

    if "429" in message or "resource_exhausted" in lower:
        return (
            "Gemini API ใช้โควตาหมดหรือไม่มีโควตาสำหรับโมเดลนี้ "
            "กรุณาตรวจสอบโควตาและ Billing ที่ "
            "https://ai.google.dev/gemini-api/docs/rate-limits"
        )

    if "403" in message or "permission_denied" in lower:
        return (
            "API key ไม่มีสิทธิ์เรียกใช้โมเดลนี้ "
            "กรุณาตรวจสอบสิทธิ์การใช้งานและ Billing"
        )

    if "404" in message or "not_found" in lower:
        return (
            "ไม่พบโมเดลที่เรียกใช้ "
            "กรุณาตรวจสอบชื่อโมเดลใน TEXT_MODEL หรือ IMAGE_MODEL"
        )

    return f"เกิดข้อผิดพลาดจาก Gemini API: {message}"


# =========================================================
# GEMINI IMAGE GENERATION
# =========================================================


def gemini_generate_image(
    api_key,
    plan,
    scene,
    mood=None,
):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create one cinematic film still for a short film.

Film title: {plan.get('title', '')}
Genre: {plan.get('genre', '')}
Overall visual style: {plan.get('visual_style', '')}
Selected visual mood: {mood or plan.get('visual_style', '')}
Story summary: {plan.get('logline', '')}

Scene number: {scene.get('scene_number', '')}
Scene title: {scene.get('scene_title', '')}
Scene purpose: {scene.get('purpose', '')}

Image prompt (English):
{scene.get('visual_prompt', '')}

Requirements:
- Widescreen cinematic composition, aspect ratio 16:9.
- High-quality cinematic film still.
- Coherent lighting and color grading.
- Maintain consistent character appearance and setting.
- One image only, not a collage or storyboard.
- No captions, subtitles, logos, watermarks, or written text.
"""

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        ),
    )

    for part in response.parts or []:
        if getattr(part, "inline_data", None) is not None:
            image = part.as_image()

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            return buffer.getvalue()

    raise RuntimeError(
        "โมเดลไม่ได้ส่งภาพกลับมา "
        "กรุณาตรวจสอบโมเดล API key โควตา และสิทธิ์การใช้งาน"
    )


# =========================================================
# SIDEBAR SETTINGS
# =========================================================

with st.sidebar:
    st.header("⚙️ ตั้งค่าโปรเจกต์")

    title = st.text_input(
        "ชื่อเรื่อง",
        "คืนสุดท้ายที่สถานี",
    )

    genre = st.selectbox(
        "แนวหนัง",
        GENRES,
    )

    mood = st.selectbox(
        "อารมณ์ภาพ",
        MOODS,
    )

    duration = st.select_slider(
        "ความยาวโดยประมาณ",
        options=[30, 60, 90, 120, 180],
        value=60,
        format_func=lambda value: f"{value} วินาที",
    )

    scene_count = st.slider(
        "จำนวนฉาก",
        min_value=3,
        max_value=10,
        value=5,
    )

    st.divider()

    language = st.selectbox(
        "ภาษาหลักของเรื่อง",
        list(LANGUAGES.keys()),
        index=0,
    )

    language_info = LANGUAGES[language]

    region = st.selectbox(
        "พื้นที่ / สำเนียง / รูปแบบภาษา",
        language_info["regions"],
        index=0,
    )

    multilingual = st.checkbox(
        "รองรับบทสนทนาหลายภาษา",
        value=False,
        help=(
            "ให้ตัวละครพูดคนละภาษาได้ "
            "โดยกำหนดภาษาของแต่ละตัวละครด้านล่าง"
        ),
    )

    st.caption(
        "ตัวอย่าง: มิน | ไทยอีสาน | ขอนแก่น"
    )

    character_languages = st.text_area(
        "ภาษาของตัวละคร (ไม่บังคับ)",
        "มิน | ไทยอีสาน | ขอนแก่น\n"
        "เรย์ | English (US) | General American",
        height=90,
        help=(
            "หนึ่งตัวละครต่อหนึ่งบรรทัด: "
            "ชื่อตัวละคร | ภาษา/สำเนียง | พื้นที่ (ถ้ามี)"
        ),
    )

    st.divider()

    use_ai = st.checkbox(
        "ใช้ Gemini API สำหรับสร้างพล็อต",
        value=False,
    )

    saved_key = get_saved_api_key()

    api_key = st.text_input(
        "Gemini API key (ไม่บังคับ)",
        value=saved_key,
        type="password",
        help=(
            "ใส่คีย์จาก Google AI Studio "
            "หรือกำหนด GEMINI_API_KEY "
            "ใน Streamlit Secrets"
        ),
    )

    st.caption(
        "การสร้างข้อความและภาพผ่าน API "
        "อาจมีค่าใช้จ่ายตามโมเดลและโควตาบัญชี"
    )


# =========================================================
# STORY IDEA AND STYLE NOTES
# =========================================================

idea = st.text_area(
    "💡 ไอเดียเรื่อง",
    (
        "หญิงสาวคนหนึ่งได้รับข้อความจากตัวเองในอนาคต "
        "เตือนว่าอย่าขึ้นรถไฟเที่ยวสุดท้าย"
    ),
    height=110,
)

style_notes = st.text_input(
    "รายละเอียดเพิ่มเติม",
    "ตัวละครหลักคนเดียว ฉากกลางคืน มีจุดหักมุม",
)


# =========================================================
# CREATE FILM PLAN
# =========================================================

if st.button(
    "✨ สร้างพล็อตและแบ่งฉาก",
    type="primary",
    use_container_width=True,
):
    if not idea.strip():
        st.error("กรุณาใส่ไอเดียเรื่องก่อน")

    elif use_ai and not api_key.strip():
        st.error(
            "กรุณากรอก Gemini API key "
            "หรือปิดตัวเลือก Gemini API เพื่อใช้โหมดเทมเพลต"
        )

    else:
        try:
            with st.spinner("กำลังวางโครงเรื่อง..."):

                if use_ai:
                    plan = gemini_story(
                        api_key.strip(),
                        title,
                        genre,
                        idea,
                        scene_count,
                        duration,
                        mood,
                        language,
                        style_notes,
                        region,
                        multilingual,
                        character_languages,
                    )

                    source = "Gemini API"

                else:
                    plan = fallback_story(
                        title,
                        genre,
                        idea,
                        scene_count,
                        duration,
                        mood,
                        language,
                        style_notes,
                        region,
                        multilingual,
                        character_languages,
                    )

                    source = "Template mode"

                st.session_state["film_plan"] = plan
                st.session_state["scene_images"] = {}
                st.session_state["plan_source"] = source

        except Exception as exc:
            error_message = (
                explain_api_error(exc)
                if use_ai
                else str(exc)
            )

            st.error(
                f"สร้างแผนไม่สำเร็จ: {error_message}"
            )

            st.info(
                "ตรวจสอบ API key การเชื่อมต่อ ชื่อโมเดล "
                "และโควตา หรือปิด Gemini API "
                "เพื่อใช้โหมดเทมเพลต"
            )


# =========================================================
# DISPLAY FILM PLAN
# =========================================================

if "film_plan" in st.session_state:

    plan = st.session_state["film_plan"]

    scenes = plan.get("scenes", [])

    scene_images = st.session_state.setdefault(
        "scene_images",
        {},
    )

    st.success(
        "สร้างแผนแล้ว • แหล่งสร้าง: "
        + st.session_state.get(
            "plan_source",
            "ไม่ทราบ",
        )
    )

    if (
        plan.get("template_notice")
        and st.session_state.get("plan_source") == "Template mode"
    ):
        st.info(plan["template_notice"])

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "จำนวนฉาก",
        len(scenes),
    )

    m2.metric(
        "ความยาวเป้าหมาย",
        f"{plan.get('duration_seconds', 0)} วินาที",
    )

    m3.metric(
        "แนวหนัง",
        plan.get("genre", "-"),
    )

    st.header(plan.get("title", "เรื่องของฉัน"))

    st.write(
        "**เรื่องย่อ:**",
        plan.get("logline", ""),
    )

    st.write(
        "**สไตล์ภาพ:**",
        plan.get("visual_style", ""),
    )

    st.write(
        "**ภาษา:**",
        plan.get("language", language),
        "•",
        plan.get("dialect_region", region),
    )

    if plan.get("character_languages"):
        with st.expander("การกำหนดภาษาของตัวละคร"):
            st.code(plan["character_languages"])

    # -----------------------------------------------------
    # IMAGE GENERATION
    # -----------------------------------------------------

    st.subheader("🎨 สร้างภาพประกอบฉาก")

    if not api_key.strip():
        st.warning(
            "ต้องมี Gemini API key เพื่อสร้างภาพ "
            "กรุณาใส่คีย์ในแถบด้านข้าง"
        )

    if st.button(
        "🎨 สร้างภาพทุกฉากที่ยังไม่มี",
        use_container_width=True,
        disabled=not bool(api_key.strip()),
    ):
        failures = []

        progress = st.progress(0)

        for index, scene in enumerate(scenes):
            image_key = str(scene["scene_number"])

            if image_key not in scene_images:
                try:
                    with st.spinner(
                        f"กำลังสร้างภาพฉากที่ {image_key}..."
                    ):
                        scene_images[image_key] = (
                            gemini_generate_image(
                                api_key.strip(),
                                plan,
                                scene,
                                mood,
                            )
                        )

                except Exception as exc:
                    failures.append(
                        f"ฉาก {image_key}: "
                        f"{explain_api_error(exc)}"
                    )

            progress.progress(
                (index + 1) / max(1, len(scenes))
            )

        st.session_state["scene_images"] = scene_images

        if failures:
            st.error(
                "บางฉากสร้างภาพไม่สำเร็จ:\n\n"
                + "\n".join(failures)
            )
        else:
            st.success("สร้างภาพครบทุกฉากแล้ว")

        st.rerun()

    # -----------------------------------------------------
    # SCENE TABS
    # -----------------------------------------------------

    tabs = st.tabs(
        [
            f"ฉาก {scene['scene_number']}"
            for scene in scenes
        ]
    )

    for tab, scene in zip(tabs, scenes):

        with tab:
            scene_number = str(scene["scene_number"])

            st.subheader(
                f"ฉาก {scene_number}: {scene['scene_title']}"
            )

            st.caption(
                f"ความยาว: "
                f"{scene.get('duration_seconds', 0)} วินาที"
            )

            st.write("**เป้าหมายของฉาก**")
            st.write(scene.get("purpose", ""))

            st.write("**Prompt สำหรับภาพ (ภาษาอังกฤษ)**")

            st.text_area(
                f"visual_prompt_{scene_number}",
                scene.get("visual_prompt", ""),
                height=130,
                key=f"visual_{scene_number}",
            )

            st.write("**Prompt สำหรับวิดีโอ (ภาษาอังกฤษ)**")

            st.text_area(
                f"video_prompt_{scene_number}",
                scene.get("video_prompt", ""),
                height=100,
                key=f"video_{scene_number}",
            )

            st.write("**บทบรรยาย / บทพูด**")

            st.text_area(
                f"voiceover_{scene_number}",
                scene.get("voiceover", ""),
                height=100,
                key=f"voice_{scene_number}",
            )

            if scene_number in scene_images:
                st.image(
                    scene_images[scene_number],
                    caption=f"ภาพฉากที่ {scene_number}",
                    use_container_width=True,
                )

                st.download_button(
                    "⬇️ ดาวน์โหลดภาพ PNG",
                    data=scene_images[scene_number],
                    file_name=f"scene_{scene_number}.png",
                    mime="image/png",
                    key=f"download_img_{scene_number}",
                )

    # -----------------------------------------------------
    # DOWNLOAD PROJECT
    # -----------------------------------------------------

    json_data = json.dumps(
        plan,
        ensure_ascii=False,
        indent=2,
    )

    txt_lines = [
        f"ชื่อเรื่อง: {plan.get('title', '')}",
        f"แนว: {plan.get('genre', '')}",
        f"เรื่องย่อ: {plan.get('logline', '')}",
        (
            f"ความยาว: "
            f"{plan.get('duration_seconds', 0)} วินาที"
        ),
        (
            f"ภาษา: {plan.get('language', language)} / "
            f"{plan.get('dialect_region', region)}"
        ),
        f"สไตล์ภาพ: {plan.get('visual_style', '')}",
        f"หมายเหตุ: {plan.get('notes', '')}",
        "",
    ]

    for scene in scenes:
        txt_lines.extend(
            [
                (
                    f"ฉาก {scene.get('scene_number')}: "
                    f"{scene.get('scene_title', '')}"
                ),
                (
                    f"เวลา: "
                    f"{scene.get('duration_seconds', 0)} วินาที"
                ),
                f"เป้าหมาย: {scene.get('purpose', '')}",
                (
                    f"Visual Prompt: "
                    f"{scene.get('visual_prompt', '')}"
                ),
                (
                    f"Video Prompt: "
                    f"{scene.get('video_prompt', '')}"
                ),
                (
                    f"บทบรรยาย/บทพูด: "
                    f"{scene.get('voiceover', '')}"
                ),
                "-" * 40,
            ]
        )

    st.subheader("📦 ดาวน์โหลดโปรเจกต์")

    d1, d2 = st.columns(2)

    d1.download_button(
        "⬇️ ดาวน์โหลดแผน JSON",
        data=json_data.encode("utf-8"),
        file_name="film_plan.json",
        mime="application/json",
        use_container_width=True,
    )

    d2.download_button(
        "⬇️ ดาวน์โหลดบทหนัง TXT",
        data="\n".join(txt_lines).encode("utf-8"),
        file_name="film_script.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.caption(
        "หมายเหตุ: แอปนี้สร้างภาพนิ่งประกอบฉากได้ผ่านโมเดลภาพ "
        "ที่กำหนดไว้ ส่วนการสร้างวิดีโอจริงยังไม่ได้เปิดใช้งาน"
    )
