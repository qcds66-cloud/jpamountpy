import streamlit as st
from gtts import gTTS
import io

# --- 頁面設定 (針對手機優化) ---
st.set_page_config(
    page_title="日語量詞學習",
    page_icon="🇯🇵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 莫蘭迪色系 CSS 注入 (優化網頁視覺) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #E0E0D8;
    }
    div[data-testid="stSelectbox"] label {
        color: #4A4A4A;
        font-weight: bold;
        font-size: 1.1rem;
    }
    div[data-testid="stMarkdownContainer"] p {
        color: #4A4A4A;
    }
    /* 備註提示框樣式 */
    .stAlert {
        background-color: #F5F5F0;
        color: #4A4A4A;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)


# --- 資料設定 (完整保留原本的資料) ---
DATA = {
    "日付 (日期)": ["1日 (ついたち)", "2日 (ふつか)", "3日 (みっか)", "4日 (よっか)", "5日 (いつか)", "6日 (むいか)", "7日 (なのか)", "8日 (ようか)", "9日 (ここのか)", "10日 (とおか)", "11日 (じゅういちにち)", "12日 (じゅうににち)", "14日 (じゅうよっか)", "20日 (はつか)", "24日 (にじゅうよっか)"],
    "月 (月份)": ["1月 (いちがつ)", "2月 (にがつ)", "3月 (さんがつ)", "4月 (しがつ) *注意", "5月 (ごがつ)", "6月 (ろくがつ)", "7月 (しちがつ)", "8月 (hachigatsu)", "9月 (くがつ) *注意", "10月 (じゅうがつ)", "11月 (じゅういちがつ)", "12月 (じゅうにがつ)"],
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
    "扁平物 (枚 - 紙/吐司)": ["※紙張、衣服、切片吐司等", "1枚 (いちまい)", "2枚 (にまい)", "3枚 (さんまい)", "4枚 (よんまい)", "5枚 (ごまい)", "6枚 (ろくまい)", "7枚 (ななまい)", "8枚 (はちまい)", "9枚 (きゅうまい)", "10枚 (じゅまい)"],
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
def get_audio_bytes(text):
    """生成 TTS 音訊並轉為位元組 (加入快取以提升手機載入速度)"""
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# --- UI 介面設計 ---
st.title("🇯🇵 日語量詞學習")

# 手機友善的下拉式選單
selected_category = st.selectbox("請選擇學習類別：", list(DATA.keys()))

st.divider()

# 音訊播放區塊 (固定在頂部，避免點擊播放時畫面跳動)
audio_placeholder = st.empty()

# 控制按鈕區 (連續朗讀)
col1, col2 = st.columns([1, 1])
with col1:
    play_all = st.button("▶️ 連續朗讀", use_container_width=True)
with col2:
    st.write("*(欲停止可直接在播放器按暫停)*")

if play_all:
    # 組合該類別的所有單字，使用句號分隔以產生自然的停頓
    items_to_read = [get_readable_text(item) for item in DATA[selected_category] if not item.startswith("※")]
    combined_text = "。 ".join(items_to_read)
    
    with st.spinner("產生連續語音中..."):
        audio_bytes = get_audio_bytes(combined_text)
        # 在頂部顯示播放器並自動播放
        audio_placeholder.audio(audio_bytes, format='audio/mp3', autoplay=True)

# 列表展示區
st.subheader(selected_category)

# 將清單顯示為手機適合的卡片式版面
for idx, item in enumerate(DATA[selected_category]):
    if item.startswith("※"):
        # 提示文字
        st.info(item)
    else:
        # 使用欄位來並排「文字」與「獨立播放按鈕」
        col_text, col_btn = st.columns([4, 1])
        
        with col_text:
            # 判斷是否為有 *注意 的特殊變化，用紅色標記
            if "*注意" in item:
                display_text = item.replace("*注意", "<span style='color:#D5C6C6; font-weight:bold;'>(注意)</span>")
                st.markdown(f"**{display_text}**", unsafe_allow_html=True)
            else:
                st.markdown(f"**{item}**")
                
        with col_btn:
            # 每列的獨立播放按鈕
            if st.button("🔊", key=f"btn_{selected_category}_{idx}", use_container_width=True):
                with st.spinner(""):
                    audio_bytes = get_audio_bytes(get_readable_text(item))
                    # 將產生的音檔放到頂部的播放器並自動播放
                    audio_placeholder.audio(audio_bytes, format='audio/mp3', autoplay=True)
