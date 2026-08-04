import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
import io
import base64
import json

# --- 頁面設定 (針對手機優化) ---
st.set_page_config(
    page_title="量詞學習",
    page_icon="🇯🇵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# --- 🎨 字體、行距與顏色設定區塊 (集中管理) ---
# ==========================================
STYLE_CONFIG = {
    "bg_color": "#E0E0D8",          # 整體背景色 (莫蘭迪灰)
    "text_color": "#4A4A4A",        # 主要文字顏色 (深灰)
    
    # 列表文字設定
    "list_font_size": "20px",       # 🌟 單字列表的字體大小
    "list_line_height": "1.0",      # 🌟 單字列表的行距
    
    # 特殊文字顏色
    "note_color": "#6B8E23",        # 提示文字 (※開頭) 的顏色
    "warn_color": "#C07B7B",        # 警告文字 (*注意) 的顏色
    "highlight_color": "#0066CC",   # 🌟 朗讀時的高亮顏色 (藍色)
    "highlight_bg": "#E8F0FE"       # 朗讀時的背景底色 (淺藍，增加辨識度)
}

# 注入 Streamlit 原生介面 CSS 樣式
st.markdown(f"""
    <style>
    /* 🔥 移除 Streamlit 預設的頂部大留白，讓畫面元素貼近最上方 */
    .block-container {{
        padding-top: 1rem !important;
    }}
    
    /* 🔥 針對 st.title() 產生的標題(h1)，將字體縮小50% (原約 2.5rem 改為 1.25rem) */
    h1 {{
        font-size: 1.25rem !important;
        padding-top: 0 !important;
        margin-bottom: 1 !important;
    }}

    /* 整體背景與字體顏色 */
    .stApp {{
        background-color: {STYLE_CONFIG["bg_color"]};
    }}
    
    /* 下拉選單標題設定 */
    div[data-testid="stSelectbox"] label {{
        color: {STYLE_CONFIG["text_color"]};
        font-weight: bold;
        font-size: 1.8rem;
    }}
    
    /* 🔥 將下拉選單本身的選取框與文字放大約 80% (預設為 1rem，改為 1.8rem) */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
        font-size: 2.8rem !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
        font-size: 2.8rem !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{
        width: 2.8rem !important;
        height: 2.8rem !important;
    }}
    /* 🔥 同步放大展開後的選單清單文字 (加大80%) */
    ul[role="listbox"] li {{
        font-size: 2.8rem !important;
    }}
    
    /* 🔥 縮小 Streamlit 預設的區塊間距 */
    div[data-testid="stVerticalBlock"] {{
        gap: 0rem !important; 
    }}
    /* 🔥 將下拉選單底部的空間進一步壓縮 */
    div[data-testid="stSelectbox"] {{
        margin-bottom: -10px !important;
    }}
    </style>
""", unsafe_allow_html=True)
# ==========================================


# --- 資料設定 (增加數字 1-10、100-900、1000-9000、1萬-9萬) ---
DATA = {
    "數字 (1-10)": ["1 (いち)", "2 (に)", "3 (さん)", "4 (よん) *注意", "5 (ご)", "6 (ろく)", "7 (なな) *注意", "8 (はち)", "9 (きゅう) *注意", "10 (じゅう)"],
    "數字 (100-900)": ["100 (ひゃく)", "200 (にひゃく)", "300 (さんびゃく) *注意", "400 (よんひゃく)", "500 (ごひゃく)", "600 (ろっぴゃく) *注意", "700 (ななひゃく)", "800 (はっぴゃく) *注意", "900 (きゅうひゃく)"],
    "數字 (1000-9000)": ["1000 (せん)", "2000 (にせん)", "3000 (さんぜん) *注意", "4000 (よんせん)", "5000 (ごせん)", "6000 (ろくせん)", "7000 (ななせん)", "8000 (はっせん) *注意", "9000 (きゅうせん)"],
    "數字 (1萬-9萬)": ["1万 (いちまん)", "2万 (にまん)", "3万 (さんまん)", "4万 (よんまん)", "5万 (ごまん)", "6万 (ろくまん)", "7万 (ななまん)", "8万 (はちまん)", "9万 (きゅうまん)"],
    
    # 以下為原本保留的資料
    "日付 (日期)": ["1日 (ついたち)", "2日 (ふつか)", "3日 (みっか)", "4日 (よっか)", "5日 (いつか)", "6日 (むいか)", "7日 (なのか)", "8日 (ようか)", "9日 (ここのか)", "10日 (とおか)", "11日 (じゅういちにち)", "12日 (じゅうににち)", "14日 (じゅうよっか)", "20日 (はつか)", "24日 (にじゅうよっか)"],
    "月 (月份)": ["1月 (いちがつ)", "2月 (にがつ)", "3月 (さんがつ)", "4月 (しがつ) *注意", "5月 (ごがつ)", "6月 (ろくがつ)", "7月 (しちがつ)", "8月 (はちがつ)", "9月 (くがつ) *注意", "10月 (じゅうがつ)", "11月 (じゅういちがつ)", "12月 (じゅうにがつ)"],
    "曜日 (星期)": ["月曜日 (げつようび)", "火曜日 (かようび)", "水曜日 (すいようび)", "木曜日 (もくようび)", "金曜日 (きんようび)", "土曜日 (どようび)", "日曜日 (にちようび)"],
    "時間 (點鐘)": ["1時 (いちじ)", "2時 (にじ)", "3時 (さんじ)", "4時 (よじ) *注意", "5時 (ごじ)", "6時 (ろくじ)", "7時 (しちじ) *注意", "8時 (はちじ)", "9時 (くじ) *注意", "10時 (じゅうじ)", "11時 (じゅういちじ)", "12時 (じゅうにじ)"],
    "時間 (分鐘)": ["1分 (いっぷん)", "2分 (にふん)", "3分 (さんぷん)", "4分 (よんぷん)", "5分 (ごふん)", "6分 (ろっぷん)", "7分 (ななふん)", "8分 (はっぷん)", "9分 (きゅうふん)", "10分 (じゅっぷん)", "30分 (はん / さんじゅっぷん)"],
    "人數 (人)": ["1人 (ひとり) *注意", "2人 (ふたり) *注意", "3人 (さんにん)", "4人 (よにん) *注意", "5人 (ごにん)", "6人 (ろくにん)", "7人 (しちにん/ななにん)", "8人 (はちにん)", "9人 (くにん)", "10人 (じゅうにん)"],
    "通用/立體 (つ)": ["1つ (ひとつ)", "2つ (ふたつ)", "3つ (みっつ)", "4つ (よっつ)", "5つ (いつつ)", "6つ (むっつ)", "7つ (ななつ)", "8つ (やっつ)", "9つ (ここのつ)", "10 (とお) *無つ"],
    "立體物/麵包 (個)": ["※圓形麵包、蘋果、橡皮擦等", "1個 (いっこ)", "2個 (にこ)", "3個 (さんこ)", "4個 (よんこ)", "5個 (ごこ)", "6個 (ろっこ)", "7個 (ななこ)", "8個 (はっこ)", "9個 (きゅうこ)", "10個 (じゅっこ)"],
    "杯/碗 (杯)": ["※水、茶、咖啡、湯等", "1杯 (いっぱい)", "2杯 (にはい)", "3杯 (さんばい)", "4杯 (よんはい)", "5杯 (ごはい)", "6杯 (ろっぱい)", "7杯 (ななはい)", "8杯 (はっぱい)", "9杯 (きゅうはい)", "10杯 (じゅっぱい)"],
    "動物 (匹 - 貓狗魚)": ["1匹 (いっぴき)", "2匹 (にひき)", "3匹 (さんびき)", "4匹 (よんひき)", "5匹 (ごひき)", "6匹 (ろっぴき)", "7匹 (ななひき)", "8匹 (はっぴき)", "9匹 (きゅうひき)", "10匹 (じゅっぴき)"],
    "大型動物 (頭 - 牛馬)": ["1頭 (いっとう)", "2頭 (にとう)", "3頭 (さんとう)", "4頭 (よんとう)", "5頭 (ごとう)", "6頭 (ろっとう)", "7頭 (ななとう)", "8頭 (はっとう)", "9頭 (きゅうとう)", "10頭 (じゅっとう)"],
    "細長物 (本 - 瓶/筆/樹)": ["※瓶子、雨傘、筆等細長物", "1本 (いっぽん)", "2本 (にほん)", "3本 (さんぼん)", "4本 (よんほん)", "5本 (ごほん)", "6本 (ろっぽん)", "7本 (ななほん)", "8本 (はっぽん)", "9本 (きゅうほん)", "10本 (じゅっぽん)"],
    "扁平物 (枚 - 紙/吐司)": ["※紙張、衣服、切片吐司等", "1枚 (いちまい)", "2枚 (にまい)", "3枚 (さんまい)", "4枚 (よんまい)", "5枚 (ごまい)", "6枚 (ろくまい)", "7枚 (ななまい)", "8枚 (はちまい)", "9枚 (きゅうまい)", "10枚 (じゅうまい)"],
    "書籍/雜誌 (冊)": ["1冊 (いっさつ)", "2冊 (にさつ)", "3冊 (さんさつ)", "4冊 (よんさつ)", "5冊 (ごさつ)", "6冊 (ろっさつ)", "7冊 (ななさつ)", "8冊 (はっさつ)", "9冊 (きゅうさつ)", "10冊 (じゅっさつ)"],
    "樓層 (階)": ["1階 (いっかい)", "2階 (にかい)", "3階 (さんがい) *注意", "4階 (よんかい)", "5階 (ごかい)", "6階 (ろっかい)", "7階 (ななかい)", "8階 (はっかい)", "9階 (きゅうかい)", "10階 (じゅっかい)"]
}

# --- 輔助函式 ---
def get_readable_text(text):
    """提取括號內的平假名作為朗讀文字"""
    if "(" in text and ")" in text:
        return text.split("(")[1].split(")")[0]
    return text

@st.cache_data
def get_audio_base64(text):
    """生成 TTS 音訊並轉為 Base64 字串傳遞給前端"""
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    return f"data:audio/mp3;base64,{b64}"

# --- UI 介面設計 ---
st.title("量詞學習/Sa i")

# 選擇類別
selected_category = st.selectbox("選 擇 類 別：", list(DATA.keys()))

# 動態產生該類別的 HTML 與 JavaScript 資料
js_items = []
html_list = []

# 建立資料清單時顯示 Loading 狀態
with st.spinner("載入語音中... (產生後立即可播放)"):
    for i, item in enumerate(DATA[selected_category]):
        item_id = f"item-{i}"
        
        if item.startswith("※"):
            # 提示文字 (無語音)
            html_list.append(f"<div id='{item_id}' class='list-item item-note'>{item}</div>")
            js_items.append({"id": item_id, "hasAudio": False})
        else:
            # 處理警告文字
            clean_text = item.replace("*注意", "")
            warn_html = "<span class='item-warn'>(*注意)</span>" if "*注意" in item else ""
            html_list.append(f"<div id='{item_id}' class='list-item'>{clean_text} {warn_html}</div>")
            
            # 生成語音 Base64
            audio_b64 = get_audio_base64(get_readable_text(item))
            js_items.append({"id": item_id, "hasAudio": True, "audio": audio_b64})

# 組合 HTML 原始碼 (結合 CSS 與 JS 控制器)
custom_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            background-color: {STYLE_CONFIG['bg_color']};
            margin: 0; padding: 0;
            font-family: sans-serif;
        }}
        /* 自訂的細版分隔線 */
        .custom-divider {{
            border: 0;
            border-top: 1px solid #C9C9C9;
            margin: 2px 0 10px 0; /* 極小的間距 */
        }}
        /* 播放按鈕設計 */
        .play-btn {{
            background-color: #A3B1C6;
            color: #333;
            font-size: 1.3rem;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px;
            width: 90%;
            margin-bottom: 20px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        /* 單字列表設計 */
        .list-item {{
            font-size: {STYLE_CONFIG['list_font_size']};
            line-height: {STYLE_CONFIG['list_line_height']};
            color: {STYLE_CONFIG['text_color']};
            font-weight: bold;
            padding: 8px 10px;
            border-bottom: 1px dashed #C9C9C9;
            border-radius: 6px;
            transition: all 0.3s ease;
        }}
        .item-note {{
            color: {STYLE_CONFIG['note_color']};
            font-size: 0.9em;
            font-weight: normal;
        }}
        .item-warn {{ color: {STYLE_CONFIG['warn_color']}; }}
        
        /* 🔥 正在朗讀時的高亮 CSS 類別 */
        .highlight {{
            color: {STYLE_CONFIG['highlight_color']} !important;
            background-color: {STYLE_CONFIG['highlight_bg']};
            transform: scale(1.02); /* 微微放大增加視覺焦點 */
        }}
    </style>
</head>
<body>
    <!-- 緊湊的分隔線 -->
    <hr class="custom-divider">
    <button id="playBtn" class="play-btn" onclick="togglePlay()">▶️ 朗讀 {selected_category}</button>
    <div id="list-container">
        {"".join(html_list)}
    </div>
    
    <audio id="audio-player"></audio>

    <script>
        const items = {json.dumps(js_items)};
        let currentIndex = 0;
        let isPlaying = false;
        let timeoutId = null;
        
        const player = document.getElementById('audio-player');
        const btn = document.getElementById('playBtn');

        function togglePlay() {{
            if (isPlaying) {{
                // 停止邏輯
                isPlaying = false;
                player.pause();
                clearTimeout(timeoutId);
                btn.innerHTML = "▶️ 朗讀 {selected_category}";
                btn.style.backgroundColor = "#A3B1C6";
                clearHighlight();
            }} else {{
                // 開始邏輯
                isPlaying = true;
                currentIndex = 0;
                btn.innerHTML = "⏹ 停止朗讀";
                btn.style.backgroundColor = "#D5C6C6";
                playNext();
            }}
        }}

        function clearHighlight() {{
            document.querySelectorAll('.list-item').forEach(el => el.classList.remove('highlight'));
        }}

        function playNext() {{
            if (!isPlaying) return;
            clearHighlight();

            // 若播放完畢
            if (currentIndex >= items.length) {{
                isPlaying = false;
                btn.innerHTML = "▶️ 朗讀 {selected_category}";
                btn.style.backgroundColor = "#A3B1C6";
                return;
            }}

            const item = items[currentIndex];
            const el = document.getElementById(item.id);

            if (item.hasAudio) {{
                // 1. 變更顏色
                if (el) {{
                    el.classList.add('highlight');
                    // 自動將畫面滾動到正在播放的單字
                    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
                
                // 2. 播放語音
                player.src = item.audio;
                player.play();

                // 3. 語音結束後，等待 2 秒再進下一首
                player.onended = () => {{
                    if (!isPlaying) return;
                    if (el) el.classList.remove('highlight'); /* 變回原色 */
                    currentIndex++;
                    
                    // 暫停 2 秒
                    timeoutId = setTimeout(() => {{
                        playNext();
                    }}, 2000);
                }};
            }} else {{
                // 遇到沒有語音的(如※提示)，直接跳下一個
                currentIndex++;
                playNext();
            }}
        }}
    </script>
</body>
</html>
"""

# 渲染自訂 HTML 元件 (設定足夠的高度以避免雙重捲軸)
components.html(custom_html, height=1000, scrolling=True)
