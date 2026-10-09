import io
import json
import re
import streamlit as st

st.set_page_config(page_title="AI Short Film Studio", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1100px; padding-top: 1.4rem;}
.stApp {background: linear-gradient(160deg, #100c20 0%, #171326 55%, #0c1020 100%);}
h1, h2, h3, p, label {color: #f4efff;}
div[data-testid="stMetric"] {background: #241d37; padding: 12px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🎬 AI Short Film Studio")
st.caption("รุ่นเริ่มต้น • วางพล็อต แบ่งฉาก และสร้าง Prompt สำหรับผลิตหนังสั้น")

with st.sidebar:
    st.header("⚙️ ตั้งค่าโปรเจกต์")
    title = st.text_input("ชื่อเรื่อง", "คืนสุดท้ายที่สถานี")
    genre = st.selectbox("แนวหนัง", ["ไซไฟ", "สยองขวัญ", "โรแมนติก", "แฟนตาซี", "แอ็กชัน", "ดราม่า", "สืบสวน"])
    mood = st.selectbox("อารมณ์ภาพ", ["cinematic, dramatic lighting", "warm and nostalgic", "dark and suspenseful", "dreamlike and surreal", "bright and whimsical"])
    duration = st.select_slider("ความยาวโดยประมาณ", options=[30, 60, 90, 120, 180], value=60, format_func=lambda x: f"{x} วินาที")
    scene_count = st.slider("จำนวนฉาก", 3, 10, 5)
    language = st.selectbox("ภาษา", ["ไทย", "English"])
    st.divider()
    use_ai = st.checkbox("ใช้ Gemini API ถ้ามี API key", value=False)
    api_key = st.text_input("Gemini API key (ไม่บังคับ)", type="password", help="เก็บไว้ในเซสชันนี้เท่านั้น อย่าใส่ API key ในโค้ดหรือส่งให้ผู้อื่น")

idea = st.text_area("💡 ไอเดียเรื่อง", "หญิงสาวคนหนึ่งได้รับข้อความจากตัวเองในอนาคต เตือนว่าอย่าขึ้นรถไฟเที่ยวสุดท้าย", height=110)
style_notes = st.text_input("รายละเอียดเพิ่มเติม", "ตัวละครหลักคนเดียว ฉากกลางคืน มีจุดหักมุม")

def fallback_story(title, genre, idea, scene_count, duration, mood, language, style_notes):
    names = [
        ("เปิดเรื่อง", "แนะนำตัวละครและสถานที่ พร้อมภาพกว้างเพื่อสร้างบรรยากาศ"),
        ("สัญญาณแรก", "ตัวละครพบสิ่งผิดปกติที่เชื่อมโยงกับไอเดียหลัก"),
        ("ความขัดแย้ง", "เบาะแสใหม่ทำให้ตัวละครต้องตัดสินใจ"),
        ("จุดพลิกผัน", "ความจริงเปลี่ยนความเข้าใจของตัวละคร"),
        ("บทสรุป", "ปิดเรื่องด้วยภาพจำและอารมณ์ที่ชัดเจน"),
        ("ผลสะเทือน", "แสดงผลลัพธ์จากการตัดสินใจ"),
        ("เงื่อนงำใหม่", "ทิ้งคำถามเล็กน้อยให้ผู้ชมตีความ"),
        ("เผชิญหน้า", "ตัวละครเผชิญหน้ากับอุปสรรคสำคัญ"),
        ("ช่วงเงียบ", "ใช้ภาพและเสียงแทนบทพูด"),
        ("ตอนจบ", "จบด้วยภาพที่สอดคล้องกับธีมเรื่อง"),
    ]
    story = {
        "title": title,
        "genre": genre,
        "logline": f"{idea.strip()} — เรื่องแนว{genre}ที่เล่าด้วยโทน {mood}",
        "duration_seconds": duration,
        "visual_style": mood,
        "notes": style_notes,
        "scenes": []
    }
    for i in range(scene_count):
        name, beat = names[i % len(names)]
        seconds = max(4, duration // scene_count)
        story["scenes"].append({
            "scene_number": i + 1,
            "scene_title": name,
            "purpose": beat,
            "visual_prompt": f"{genre} short film, {idea}, scene {i+1}: {beat}. {mood}. Consistent character design, cinematic composition, detailed environment, no text, {style_notes}",
            "video_prompt": f"Create a {seconds}-second cinematic shot. {idea}. Action: {beat}. Camera movement is subtle and intentional; {mood}; natural motion, consistent character appearance, no subtitles or logos.",
            "voiceover": "บรรยายสั้น ๆ เพื่อเชื่อมอารมณ์ของฉาก" if language == "ไทย" else "A short voiceover to connect the scene emotionally.",
            "duration_seconds": seconds
        })
    return story


def gemini_story(api_key, title, genre, idea, scene_count, duration, mood, language, style_notes):
    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a short-film pre-production assistant. Return ONLY valid JSON, no markdown.
Create a short film plan in {language}. All fields must be present:
title, genre, logline, duration_seconds, visual_style, notes, scenes.
scenes must contain exactly {scene_count} items. Each item has:
scene_number (integer), scene_title, purpose, visual_prompt, video_prompt, voiceover, duration_seconds (integer).
Title: {title}
Genre: {genre}
Idea: {idea}
Visual mood: {mood}
Additional notes: {style_notes}
Target total duration: {duration} seconds.
Keep prompts suitable for general audiences. Maintain character and setting consistency.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I)
    return json.loads(raw)


def gemini_generate_image(api_key, plan, scene):
    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create one cinematic film still for a short film.

Film title: {plan.get("title", "")}
Genre: {plan.get("genre", "")}
Overall visual style: {plan.get("visual_style", "")}
Story summary: {plan.get("logline", "")}
Scene number: {scene.get("scene_number", "")}
Scene title: {scene.get("scene_title", "")}
Scene purpose: {scene.get("purpose", "")}
Scene image prompt: {scene.get("visual_prompt", "")}

Requirements:
- Widescreen cinematic composition, aspect ratio 16:9.
- High-quality film still, coherent lighting and color grading.
- Keep the scene consistent with the story and visual style.
- No captions, subtitles, logos, watermarks, or written text.
- Create a single image, not a collage or storyboard.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=prompt,
    )

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            image = part.as_image()
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()

    raise RuntimeError(
        "โมเดลไม่ได้ส่งภาพกลับมา กรุณาลองใหม่หรือตรวจสอบโควตา API"
    )

if st.button("✨ สร้างพล็อตและแบ่งฉาก", type="primary", use_container_width=True):
    if not idea.strip():
        st.error("กรุณาใส่ไอเดียเรื่องก่อน")
    else:
        with st.spinner("กำลังวางโครงเรื่อง..."):
            try:
                if use_ai and api_key.strip():
                    plan = gemini_story(api_key.strip(), title, genre, idea, scene_count, duration, mood, language, style_notes)
                    st.session_state["film_plan"] = plan
                    st.session_state["scene_images"] = {}
                    st.session_state["plan_source"] = "Gemini API"
                else:
                    st.session_state["film_plan"] = fallback_story(title, genre, idea, scene_count, duration, mood, language, style_notes)
                    st.session_state["scene_images"] = {}
                    st.session_state["plan_source"] = "Template mode (ไม่ใช้ API)"
            except Exception as e:
                st.error(f"เรียก AI ไม่สำเร็จ: {e}")
                st.info("ลองปิดตัวเลือก Gemini API เพื่อใช้โหมดฟรีแบบเทมเพลต หรือเช็ก API key และโควตา")

if "film_plan" in st.session_state:
    plan = st.session_state["film_plan"]
    st.success(f"สร้างแผนแล้ว • แหล่งสร้าง: {st.session_state.get('plan_source', 'ไม่ทราบ')}")
    m1, m2, m3 = st.columns(3)
    m1.metric("จำนวนฉาก", len(plan.get("scenes", [])))
    m2.metric("ความยาวเป้าหมาย", f"{plan.get('duration_seconds', duration)} วินาที")
    m3.metric("แนวหนัง", plan.get("genre", genre))
    st.subheader(plan.get("title", "เรื่องของฉัน"))
    st.write(plan.get("logline", ""))
    st.caption(f"สไตล์ภาพ: {plan.get('visual_style', '')}")
    st.subheader("🖼️ สร้างภาพ AI ของแต่ละฉาก")
    st.caption(
        "ใช้ Gemini API key ที่กรอกไว้ในแถบด้านข้าง "
        "การสร้างภาพอาจใช้โควตาหรือมีค่าใช้จ่าย"
    )

    if "scene_images" not in st.session_state:
        st.session_state["scene_images"] = {}

    if st.button(
        "🎨 สร้างภาพทุกฉาก",
        type="primary",
        key="generate_all_scene_images",
        use_container_width=True,
    ):
        if not api_key.strip():
            st.error(
                "กรุณากรอก Gemini API key ในแถบด้านข้างก่อนสร้างภาพ"
            )
        else:
            scenes = plan.get("scenes", [])
            progress = st.progress(0)
            status = st.empty()

            for i, scene in enumerate(scenes):
                number = scene.get("scene_number", i + 1)
                status.write(
                    f"กำลังสร้างภาพฉาก {number}/{len(scenes)}..."
                )

                try:
                    image_bytes = gemini_generate_image(
                        api_key.strip(), plan, scene
                    )
                    st.session_state["scene_images"][str(number)] = (
                        image_bytes
                    )
                except Exception as e:
                    st.error(f"ฉาก {number} สร้างภาพไม่สำเร็จ: {e}")

                progress.progress((i + 1) / max(len(scenes), 1))

            status.write("ประมวลผลครบทุกฉากแล้ว")

    for i, scene in enumerate(plan.get("scenes", [])):
        number = scene.get("scene_number", i + 1)
        image_bytes = st.session_state["scene_images"].get(str(number))

        if image_bytes:
            st.markdown(
                f"**ฉาก {number}: {scene.get('scene_title', 'ฉาก')}**"
            )
            st.image(image_bytes, use_container_width=True)
            st.download_button(
                f"⬇️ ดาวน์โหลดภาพฉาก {number}",
                data=image_bytes,
                file_name=f"scene_{number}.png",
                mime="image/png",
                key=f"download_scene_{number}",
            )
    tabs = st.tabs([f"ฉาก {s.get('scene_number', i+1)}" for i, s in enumerate(plan.get("scenes", []))])
    for tab, scene in zip(tabs, plan.get("scenes", [])):
        with tab:
            st.markdown(f"### {scene.get('scene_title', 'ฉาก')}")
            st.write(scene.get("purpose", ""))
            st.markdown("**Prompt สำหรับภาพอ้างอิง**")
            st.code(scene.get("visual_prompt", ""), language=None)
            st.markdown("**Prompt สำหรับวิดีโอ**")
            st.code(scene.get("video_prompt", ""), language=None)
            st.markdown("**เสียงบรรยาย**")
            st.write(scene.get("voiceover", ""))
            st.caption(f"เวลาฉาก: {scene.get('duration_seconds', 0)} วินาที")        
    json_bytes = json.dumps(plan, ensure_ascii=False, indent=2).encode("utf-8")
    prompt_text = "\n\n".join(
        f"SCENE {s.get('scene_number')}: {s.get('scene_title')}\nIMAGE PROMPT: {s.get('visual_prompt')}\nVIDEO PROMPT: {s.get('video_prompt')}\nVOICEOVER: {s.get('voiceover')}"
        for s in plan.get("scenes", [])
    )
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ ดาวน์โหลดแผน JSON", data=json_bytes, file_name="film_plan.json", mime="application/json", use_container_width=True)
    c2.download_button("⬇️ ดาวน์โหลด Prompts TXT", data=prompt_text, file_name="film_prompts.txt", mime="text/plain", use_container_width=True)
    st.caption("หมายเหตุ: ระบบสร้างภาพนิ่งด้วย Gemini API ได้ ส่วนการสร้างวิดีโอยังไม่ได้เปิดใช้งาน")
else:
    st.info("เริ่มได้เลย: ใส่ไอเดียเรื่อง แล้วกด “สร้างพล็อตและแบ่งฉาก”")
    st.markdown("**ความสามารถในรุ่นแรก**")
    st.write("- สร้างโครงเรื่องและแบ่งฉาก")
    st.write("- สร้าง Prompt สำหรับภาพและวิดีโอ")
    st.write("- ดาวน์โหลดผลลัพธ์เป็น JSON และ TXT")
    st.write("- เลือกใช้เทมเพลตฟรี หรือ Gemini API หากมีคีย์")
