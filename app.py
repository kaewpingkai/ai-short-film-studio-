import io
import json
import re

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
# CONSTANTS AND HELPERS
# =========================================================

TEXT_MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-3.1-flash-image"

GENRES = [
    # แนวพื้นฐาน
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

    # ระทึกขวัญและอาชญากรรม
    "สืบสวน",
    "นักสืบ",
    "อาชญากรรม",
    "ฆาตกรรมปริศนา",
    "ระทึกขวัญ",
    "จิตวิทยาระทึกขวัญ",
    "อาชญากรรมจิตวิทยา",
    "แก้แค้น",
    "ปล้น",
    "สายลับ",
    "ตำรวจ",
    "มาเฟีย",
    "แก๊งอาชญากรรม",
    "ศาลและกฎหมาย",
    "การเมือง",
    "สมคบคิด",
    "เอาชีวิตรอด",
    "เกมมรณะ",
    "หนีตาย",

    # สยองขวัญและสิ่งลี้ลับ
    "สยองขวัญ",
    "ผีไทย",
    "ผีญี่ปุ่น",
    "ผีเกาหลี",
    "ผีจีน",
    "บ้านผีสิง",
    "ไสยศาสตร์",
    "คุณไสย",
    "คำสาป",
    "ปีศาจ",
    "สัตว์ประหลาด",
    "ซอมบี้",
    "แวมไพร์",
    "มนุษย์หมาป่า",
    "สยองขวัญเชิงจิตวิทยา",
    "สยองขวัญเอาชีวิตรอด",
    "สยองขวัญคอเมดี้",
    "ตำนานเมือง",
    "เรื่องลี้ลับ",
    "สยองขวัญในโรงเรียน",

    # แฟนตาซีและเหนือธรรมชาติ
    "แฟนตาซี",
    "ดาร์กแฟนตาซี",
    "แฟนตาซีมหากาพย์",
    "เวทมนตร์",
    "แม่มดและพ่อมด",
    "โลกเวทมนตร์",
    "เทพปกรณัม",
    "เทพเจ้า",
    "ตำนานพื้นบ้าน",
    "เทพเซียน",
    "เซียน侠",
    "กำลังภายใน",
    "จอมยุทธ์",
    "พลังเหนือธรรมชาติ",
    "พลังพิเศษ",
    "ผู้วิเศษ",
    "โลกคู่ขนาน",
    "ต่างโลก",
    "ทะลุมิติ",
    "เกิดใหม่",
    "ย้อนอดีต",
    "ข้ามภพ",
    "กลับชาติมาเกิด",
    "สลับร่าง",
    "สลับเพศ",
    "ระบบเกม",
    "เลเวลอัป",
    "ตัวเอกไร้เทียมทาน",

    # วิทยาศาสตร์และอนาคต
    "ไซไฟ",
    "ไซไฟระทึกขวัญ",
    "ไซไฟแอ็กชัน",
    "โลกอนาคต",
    "โลกดิสโทเปีย",
    "โลกยูโทเปีย",
    "ไซเบอร์พังก์",
    "สตีมพังก์",
    "หุ่นยนต์",
    "ปัญญาประดิษฐ์",
    "โลกเสมือนจริง",
    "เกมเสมือนจริง",
    "เทคโนโลยีล้ำยุค",
    "การทดลองทางวิทยาศาสตร์",
    "การเดินทางข้ามเวลา",
    "การเดินทางในอวกาศ",
    "มนุษย์ต่างดาว",
    "การรุกรานจากต่างดาว",
    "โลกหลังหายนะ",
    "วันสิ้นโลก",
    "ภัยพิบัติ",
    "การกลายพันธุ์",
    "วิวัฒนาการมนุษย์",

    # โรแมนติกและความสัมพันธ์
    "รักแรก",
    "รักวัยเรียน",
    "รักวัยทำงาน",
    "รักต่างชนชั้น",
    "รักต้องห้าม",
    "รักสามเส้า",
    "รักข้างเดียว",
    "เพื่อนรักกลายเป็นแฟน",
    "คู่กัดกลายเป็นคู่รัก",
    "แต่งงานก่อนรัก",
    "แต่งงานตามสัญญา",
    "แต่งงานปลอม",
    "รักต่างภพ",
    "รักเหนือกาลเวลา",
    "รักแฟนตาซี",
    "รักย้อนยุค",
    "รักดราม่า",
    "รักคอมเมดี้",
    "รักเศร้าเรียกน้ำตา",
    "ความสัมพันธ์ซับซ้อน",

    # ย้อนยุคและประวัติศาสตร์
    "ย้อนยุค",
    "พีเรียดไทย",
    "พีเรียดจีน",
    "พีเรียดเกาหลี",
    "พีเรียดญี่ปุ่น",
    "พีเรียดยุโรป",
    "ประวัติศาสตร์",
    "สงคราม",
    "มหากาพย์สงคราม",
    "ซามูไร",
    "นินจา",
    "ราชวงศ์",
    "วังหลวง",
    "ชิงอำนาจ",
    "การแย่งชิงบัลลังก์",
    "การเมืองในราชสำนัก",
    "ชีวิตในยุคโบราณ",

    # อนิเมะและการ์ตูน
    "อนิเมะแอ็กชัน",
    "อนิเมะแฟนตาซี",
    "อนิเมะโรแมนติก",
    "อนิเมะสยองขวัญ",
    "อนิเมะไซไฟ",
    "โชเน็น",
    "โชโจ",
    "เซเน็น",
    "อิเซไก",
    "เมชา",
    "สาวน้อยเวทมนตร์",
    "โรงเรียนพลังพิเศษ",
    "การแข่งขัน",
    "กีฬา",
    "ดนตรี",
    "ไอดอล",
    "วงการบันเทิง",
    "ชีวิตนักเรียน",
    "การเติบโตของตัวละคร",

    # แนวเฉพาะและแนวผสม
    "สารคดี",
    "สารคดีอาชญากรรม",
    "ชีวประวัติ",
    "กีฬาและการแข่งขัน",
    "ธุรกิจ",
    "การเงิน",
    "การทำอาหาร",
    "การเดินทาง",
    "ธรรมชาติและสัตว์",
    "ผจญภัยในป่า",
    "โจรสลัด",
    "ตะวันตกคาวบอย",
    "มิวสิคัล",
    "เสียดสีสังคม",
    "เสียดสีการเมือง",
    "เหนือจริง",
    "ทดลองทางภาพยนตร์",
    "หนังสั้นหักมุม",
    "ปริศนาเหนือธรรมชาติ",
    "แฟนตาซีโรแมนติก",
    "แอ็กชันคอมเมดี้",
    "สยองขวัญคอมเมดี้",
    "ไซไฟโรแมนติก",
    "ดราม่าแก้แค้น",
    "แฟนตาซีดาร์กโรแมนซ์",
    "การทรยศและหักหลัง",
    "การล้างแค้นของตัวเอก",
    "ตัวร้ายเป็นตัวเอก",
    "ตัวเอกสีเทา",
    "พลิกบทบาทตัวละคร",
    "หักมุมหลายชั้น",
]

VISUAL_MOODS = [
    "ภาพยนตร์สมจริง",
    "อบอุ่นและสบายใจ",
    "โรแมนติกและชวนฝัน",
    "เศร้าซึ้งกินใจ",
    "ลึกลับน่าค้นหา",
    "ตึงเครียดและกดดัน",
    "โทนสีอบอุ่น",
    "โทนสีเย็น",
    "โทนขาวดำ",
    "แสงนีออน",
    "ดาร์กแฟนตาซี",
    "Cyberpunk Neon",
    "ภาพยนตร์ฟิล์ม 35mm",
    "ภาพยนตร์สไตล์ IMAX",
    "อนิเมะญี่ปุ่น",
    "ภาพวาดสีน้ำ",
    "ภาพถ่ายสมจริง",
    "ภาพยนตร์จีนย้อนยุค",
    "ภาพยนตร์เกาหลีย้อนยุค",
    "สยองขวัญแบบมืดทึบ",
    "โรแมนติกแบบภาพยนตร์",
    "ภาพแบบ Surreal Cinematic",
]

MOODS = [
    # Cinematic
    "Cinematic, dramatic lighting",
    "Hollywood blockbuster",
    "Epic and majestic",
    "Dark and gritty realism",
    "Photorealistic cinematic style",
    "Vintage 35mm film",
    "Film noir, black and white",

    # อารมณ์และบรรยากาศ
    "Warm and nostalgic",
    "Romantic and dreamy",
    "Melancholic and emotional",
    "Dark and suspenseful",
    "Dreamlike and surreal",
    "Bright and whimsical",
    "Mysterious and atmospheric",
    "Peaceful and relaxing",
    "Hopeful and inspiring",
    "Lonely and melancholic",
    "Tense and claustrophobic",
    "Playful and comedic",
    "Tragic and heartbreaking",

    # แสงและสี
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
    "Deep red and black palette",
    "Dreamy soft-focus lighting",

    # แฟนตาซีและเหนือธรรมชาติ
    "Epic fantasy concept art",
    "Dark fantasy",
    "Magical glowing atmosphere",
    "Mythical and ethereal",
    "Chinese cultivation fantasy",
    "Wuxia martial arts cinema",
    "Fairytale atmosphere",
    "Supernatural mystery",

    # ไซไฟและโลกอนาคต
    "Cyberpunk neon",
    "Futuristic sci-fi",
    "Dystopian future",
    "Post-apocalyptic atmosphere",
    "Futuristic holographic lighting",
    "Space opera cinematic style",

    # สยองขวัญและระทึกขวัญ
    "Psychological horror",
    "Gothic horror",
    "Eerie haunted atmosphere",
    "Analog horror",
    "Foggy abandoned location",
    "Survival thriller",

    # โรแมนติกและย้อนยุค
    "Korean drama cinematic style",
    "Japanese romance film style",
    "Chinese historical drama style",
    "Vintage romantic film",
    "Soft romantic pastel tones",
    "Historical period film",

    # อนิเมะและงานศิลป์
    "Japanese anime cinematic style",
    "Anime fantasy",
    "Anime action",
    "Anime romance",
    "Hand-painted watercolor",
    "Painterly concept art",
    "3D animated film style",
    "Stop-motion animation",

    # สไตล์เฉพาะ
    "Minimalist cinematic style",
    "Surreal cinematic aesthetic",
    "Dark academia",
    "Gothic aesthetic",
    "Dreamcore aesthetic",
    "Music video cinematic style",
]


def get_saved_api_key():
    """อ่าน API key จาก Streamlit Secrets หากมี"""
    try:
        return str(
            st.secrets.get("GEMINI_API_KEY", "")
        ).strip()
    except Exception:
        return ""


def distribute_duration(total_seconds, count):
    """กระจายเวลาให้ทุกฉากรวมกันตรงกับเวลาที่กำหนด"""
    if count <= 0:
        return []

    base, remainder = divmod(total_seconds, count)

    return [
        base + (1 if i < remainder else 0)
        for i in range(count)
    ]


def normalize_plan(plan, target_count, target_duration):
    """ตรวจสอบและปรับโครงสร้างแผนจาก AI ให้ใช้งานได้"""

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

    scenes = raw_scenes[:target_count]

    durations = distribute_duration(
        target_duration,
        target_count,
    )

    normalized_scenes = []

    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            scene = {}

        normalized_scenes.append(
            {
                "scene_number": index + 1,
                "scene_title": str(
                    scene.get("scene_title")
                    or f"ฉากที่ {index + 1}"
                ),
                "purpose": str(
                    scene.get("purpose") or ""
                ),
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

    plan["title"] = str(
        plan.get("title") or "เรื่องของฉัน"
    )
    plan["genre"] = str(
        plan.get("genre") or "ดราม่า"
    )
    plan["logline"] = str(
        plan.get("logline") or ""
    )
    plan["duration_seconds"] = target_duration
    plan["visual_style"] = str(
        plan.get("visual_style") or ""
    )
    plan["notes"] = str(
        plan.get("notes") or ""
    )
    plan["scenes"] = normalized_scenes

    return plan


# =========================================================
# TEMPLATE STORY GENERATOR (NO API REQUIRED)
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
):
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

    beats = beats_th if language == "ไทย" else beats_en

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
                    f"{genre} short film. "
                    f"Story idea: {idea}. "
                    f"Scene {index + 1}: {beat}. "
                    f"Visual style: {mood}. "
                    f"{style_notes}. "
                    "Consistent character design, "
                    "cinematic composition, "
                    "detailed environment, no text or logos."
                ),
                "video_prompt": (
                    f"Create a {durations[index]}-second "
                    f"cinematic shot. "
                    f"Story: {idea}. "
                    f"Action: {beat}. "
                    f"Visual mood: {mood}. "
                    "Use intentional camera movement, "
                    "natural motion, "
                    "consistent character appearance, "
                    "no subtitles or logos."
                ),
                "voiceover": (
                    "บรรยายสั้น ๆ เพื่อเชื่อมอารมณ์ของฉาก"
                    if language == "ไทย"
                    else (
                        "A short voiceover to connect "
                        "the scene emotionally."
                    )
                ),
                "duration_seconds": durations[index],
            }
        )

    return {
        "title": title,
        "genre": genre,
        "logline": (
            f"{idea.strip()} — เรื่องแนว{genre} "
            f"ที่เล่าด้วยโทน {mood}"
        ),
        "duration_seconds": duration,
        "visual_style": mood,
        "notes": style_notes,
        "scenes": scenes,
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
):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

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
You are a professional short-film pre-production assistant.

Write the entire film plan in {language}.
Return exactly {scene_count} scenes.
The target total runtime is {duration} seconds.

Every scene must have:
scene_number, scene_title, purpose, visual_prompt,
video_prompt, voiceover, duration_seconds.

Divide the runtime across all scenes as evenly as possible.
Keep character appearance, setting, and visual continuity consistent.
Create a coherent beginning, middle, turning point, and ending.
Make every scene distinct and suitable for general audiences.

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
        raise ValueError(
            "Gemini ไม่ได้ส่งข้อความกลับมา"
        )

    result = json.loads(response.text)

    return normalize_plan(
        result,
        scene_count,
        duration,
    )


# =========================================================
# GEMINI API ERROR HANDLING
# =========================================================

def explain_api_error(error):
    message = str(error)
    lower_message = message.lower()

    if (
        "429" in message
        or "resource_exhausted" in lower_message
    ):
        return (
            "Gemini API ไม่มีโควตาสำหรับสร้างภาพในขณะนี้ "
            "กรุณาตรวจสอบโควตาและ Billing ที่ "
            "https://ai.dev/rate-limit"
        )

    if (
        "403" in message
        or "permission_denied" in lower_message
    ):
        return (
            "API key ไม่มีสิทธิ์เรียกใช้โมเดลนี้ "
            "กรุณาตรวจสอบสิทธิ์การใช้งาน"
        )

    if (
        "404" in message
        or "not_found" in lower_message
    ):
        return (
            "ไม่พบโมเดลที่เรียกใช้ "
            "กรุณาตรวจสอบชื่อโมเดล"
        )

    return (
        f"เกิดข้อผิดพลาดจาก Gemini API: {message}"
    )


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

Film title: {plan.get("title", "")}
Genre: {plan.get("genre", "")}
Overall visual style: {plan.get("visual_style", "")}
Selected visual mood: {mood or plan.get("visual_style", "")}
Story summary: {plan.get("logline", "")}
Scene number: {scene.get("scene_number", "")}
Scene title: {scene.get("scene_title", "")}
Scene purpose: {scene.get("purpose", "")}
Image prompt: {scene.get("visual_prompt", "")}

Requirements:
- Widescreen cinematic composition, aspect ratio 16:9.
- High-quality film still with coherent lighting and color grading.
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
        "กรุณาตรวจสอบโมเดล API key โควตา "
        "และสิทธิ์การใช้งาน"
    )


# =========================================================
# PROJECT SETTINGS
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
        3,
        10,
        5,
    )

    language = st.selectbox(
        "ภาษา",
        ["ไทย", "English"],
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
        "การสร้างภาพและข้อความผ่าน API อาจมีค่าใช้จ่าย "
        "ขึ้นอยู่กับโมเดลและโควตาของบัญชี"
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
        st.error(
            "กรุณาใส่ไอเดียเรื่องก่อน"
        )

    elif use_ai and not api_key.strip():
        st.error(
            "กรุณากรอก Gemini API key "
            "หรือปิดตัวเลือก Gemini API "
            "เพื่อใช้โหมดเทมเพลต"
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
                    )

                    source = "Template mode"

                st.session_state["film_plan"] = plan
                st.session_state["scene_images"] = {}
                st.session_state["plan_source"] = source

        except Exception as exc:
            st.error(
                f"สร้างแผนไม่สำเร็จ: {exc}"
            )

            st.info(
                "ตรวจสอบ API key การเชื่อมต่ออินเทอร์เน็ต "
                "ชื่อโมเดล และโควตา API หรือปิด Gemini API "
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

   
