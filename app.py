import streamlit as st

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Hotel Booking DFA",
    page_icon="🏨",
    layout="wide"
)

HARGA_KAMAR = {
    "standard": 300000,
    "deluxe": 500000,
    "suite": 800000
}

STATE_LABELS = {
    "q0": "q0 - Start",
    "q1": "q1 - Nama",
    "q2": "q2 - Lama Menginap",
    "q3": "q3 - Pilih Kamar",
    "q4": "q4 - Konfirmasi",
    "q5": "q5 - Selesai (Sukses)",
    "q6": "q6 - Selesai (Batal)",
}

STATE_ORDER = ["q0", "q1", "q2", "q3", "q4", "q5", "q6"]


# ============================================================
# INISIALISASI SESSION STATE
# (setiap user/browser punya session_state sendiri-sendiri,
#  jadi tidak akan tercampur seperti versi Flask sebelumnya)
# ============================================================
def reset_booking():
    st.session_state.dfa_state = "q0"
    st.session_state.nama = ""
    st.session_state.malam = 0
    st.session_state.kamar = ""


if "dfa_state" not in st.session_state:
    reset_booking()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "bot",
            "text": (
                "👋 Selamat datang di Hotel Paradise!\n\n"
                "🏨 Kami siap membantu reservasi kamar Anda.\n\n"
                "👉 Ketik **Ya** untuk memulai booking."
            ),
        }
    ]


# ============================================================
# LOGIKA DFA
# ============================================================
def process(user_input: str) -> str:
    user_input = user_input.strip().lower()
    state = st.session_state.dfa_state

    # q0 - start
    if state == "q0":
        if user_input in ["ya", "iya", "oke", "ok"]:
            st.session_state.dfa_state = "q1"
            return "🏨 Booking baru dimulai.\n\n📝 Silakan masukkan nama Anda."
        elif user_input in ["tidak", "nggak", "tidak jadi"]:
            return "❌ Booking dibatalkan.\n\n🔄 Untuk memulai booking, ketik **Ya**."
        return "🤔 Jawab dengan ✅ Ya atau ❌ Tidak."

    # q1 - input nama
    elif state == "q1":
        st.session_state.nama = user_input.title()
        st.session_state.dfa_state = "q2"
        return f"👋 Halo {st.session_state.nama}!\n\n🌙 Berapa malam Anda akan menginap?"

    # q2 - lama menginap
    elif state == "q2":
        if not user_input.isdigit():
            return "⚠️ Masukkan jumlah malam dalam angka."
        st.session_state.malam = int(user_input)
        st.session_state.dfa_state = "q3"
        return (
            "🛏️ Pilih tipe kamar:\n\n"
            "1️⃣ Standard - Rp300.000/malam\n\n"
            "2️⃣ Deluxe - Rp500.000/malam\n\n"
            "3️⃣ Suite - Rp800.000/malam"
        )

    # q3 - pilih kamar
    elif state == "q3":
        pilihan = {"1": "standard", "2": "deluxe", "3": "suite"}
        if user_input not in pilihan:
            return "⚠️ Pilih 1️⃣, 2️⃣, atau 3️⃣."

        st.session_state.kamar = pilihan[user_input]
        total = HARGA_KAMAR[st.session_state.kamar] * st.session_state.malam
        st.session_state.dfa_state = "q4"

        return (
            f"📋 **Detail Booking**\n\n"
            f"👤 Nama : {st.session_state.nama}\n\n"
            f"🛏️ Kamar : {st.session_state.kamar.title()}\n\n"
            f"🌙 Lama Menginap : {st.session_state.malam} malam\n\n"
            f"💰 Total : Rp {total:,}\n\n"
            f"❓ Konfirmasi booking?\n\n"
            f"✅ Ya / ❌ Tidak"
        )

    # q4 - konfirmasi
    elif state == "q4":
        if user_input in ["ya", "iya", "oke", "ok"]:
            total = HARGA_KAMAR[st.session_state.kamar] * st.session_state.malam
            st.session_state.dfa_state = "q5"
            return (
                "🎉 **Booking Berhasil!**\n\n"
                f"👤 Nama : {st.session_state.nama}\n\n"
                f"🛏️ Kamar : {st.session_state.kamar.title()}\n\n"
                f"🌙 Lama Menginap : {st.session_state.malam} malam\n\n"
                f"💰 Total : Rp {total:,}\n\n"
                "✅ Terima kasih telah melakukan reservasi.\n\n"
                "🔄 Untuk booking baru, ketik **Ya**."
            )
        elif user_input in ["tidak", "nggak", "tidak jadi"]:
            st.session_state.dfa_state = "q6"
            return "❌ Booking dibatalkan.\n\n🔄 Untuk memulai booking baru, ketik **Ya**."
        return "🤔 Jawab dengan ✅ Ya atau ❌ Tidak."

    # q5 - selesai sukses
    elif state == "q5":
        if user_input in ["ya", "iya", "oke", "ok"]:
            nama_lama = st.session_state.nama
            reset_booking()
            st.session_state.dfa_state = "q1"
            return "🏨 Booking baru dimulai.\n\n📝 Silakan masukkan nama Anda."
        return "🔄 Jika ingin booking ulang, ketik **Ya**."

    # q6 - selesai batal
    elif state == "q6":
        if user_input in ["ya", "iya", "oke", "ok"]:
            reset_booking()
            st.session_state.dfa_state = "q1"
            return "🏨 Booking baru dimulai.\n\n📝 Silakan masukkan nama Anda."
        return "🔄 Jika ingin booking ulang, ketik **Ya**."


# ============================================================
# UI - LAYOUT DUA KOLOM (chat | panel DFA)
# ============================================================
st.title("🏨 Hotel Booking Chatbot")

col_chat, col_panel = st.columns([3, 1])

with col_chat:
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            avatar = "🤖" if msg["role"] == "bot" else "🧑"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["text"])

    user_input = st.chat_input("Ketik pesan...")

    if user_input:
        st.session_state.messages.append({"role": "user", "text": user_input})
        reply = process(user_input)
        st.session_state.messages.append({"role": "bot", "text": reply})
        st.rerun()

with col_panel:
    st.subheader("DFA State")
    current = st.session_state.dfa_state
    for s in STATE_ORDER:
        label = STATE_LABELS[s]
        if s == current:
            st.markdown(
                f"<div style='background:#28a745;color:white;padding:10px;"
                f"border-radius:5px;margin-bottom:8px;'>{label}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background:#eee;padding:10px;"
                f"border-radius:5px;margin-bottom:8px;'>{label}</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    if st.button("🔄 Reset Percakapan"):
        reset_booking()
        st.session_state.messages = [
            {
                "role": "bot",
                "text": (
                    "👋 Selamat datang di Hotel Paradise!\n\n"
                    "🏨 Kami siap membantu reservasi kamar Anda.\n\n"
                    "👉 Ketik **Ya** untuk memulai booking."
                ),
            }
        ]
        st.rerun()