from google import genai
import os
import json
from app.models import User, Profile

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
MODEL  = "gemini-2.0-flash"

LANG_MAP = {"uz": "O'zbek", "ru": "Rus", "en": "Ingliz"}

def _lang(profile) -> str:
    return LANG_MAP.get(profile.language if profile else "uz", "O'zbek")

def generate_schedule(user: User, date: str, notes: str = "") -> dict:
    profile = user.profile
    goals   = [g.title for g in user.goals if not g.is_done][:5]
    lang    = _lang(profile)

    profile_info = ""
    if profile:
        profile_info = f"""
- Uyg'onish: {profile.wake_time}, Uxlash: {profile.sleep_time}
- Ish vaqti: {profile.work_start} - {profile.work_end}
- Kasb: {profile.occupation or "ko'rsatilmagan"}
- Asosiy maqsadlar: {", ".join(goals) or "yo'q"}
"""

    prompt = f"""Sen vaqt menejment ekspertisan. Foydalanuvchi uchun {date} kuniga kun tartibi tuz.

Foydalanuvchi ma'lumotlari:{profile_info}
Qo'shimcha eslatma: {notes or "yo'q"}

{lang} tilida javob ber. Faqat JSON formatda qaytaruvchi (boshqa matn yo'q):
{{
  "schedule": [
    {{"time": "07:00", "task": "...", "duration": 30, "category": "salomatlik"}}
  ],
  "advice": "kun uchun qisqa maslahat (2-3 jumla)"
}}

Kategoriyalar: salomatlik | ish | dam | oila | organish"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass

    # Mock fallback
    return {
        "schedule": [
            {"time": "07:00", "task": "Uyg'onish va cho'milish", "duration": 30, "category": "salomatlik"},
            {"time": "07:30", "task": "Nonushta", "duration": 20, "category": "salomatlik"},
            {"time": "08:00", "task": "Ish bloki #1", "duration": 90, "category": "ish"},
            {"time": "09:30", "task": "Qisqa dam", "duration": 10, "category": "dam"},
            {"time": "09:40", "task": "Ish bloki #2", "duration": 90, "category": "ish"},
            {"time": "11:10", "task": "Tushlik", "duration": 40, "category": "salomatlik"},
            {"time": "12:00", "task": "Ish bloki #3", "duration": 90, "category": "ish"},
            {"time": "13:30", "task": "Dam olish / Yurish", "duration": 30, "category": "dam"},
            {"time": "14:00", "task": "Ish bloki #4", "duration": 90, "category": "ish"},
            {"time": "15:30", "task": "Sport", "duration": 45, "category": "salomatlik"},
            {"time": "16:30", "task": "Kechki ovqat", "duration": 30, "category": "salomatlik"},
            {"time": "17:00", "task": "O'rganish / Kitob", "duration": 60, "category": "organish"},
            {"time": "18:00", "task": "Oila vaqti", "duration": 90, "category": "oila"},
            {"time": "20:00", "task": "Ertangi reja", "duration": 15, "category": "ish"},
            {"time": "22:30", "task": "Uxlash", "duration": 0, "category": "salomatlik"},
        ],
        "advice": "Har bir ish blokidan keyin 10 daqiqa dam olin. Telefon bildirginomalarini ish vaqtida o'chiring. Kechqurun ertangi 3 asosiy vazifani yozing."
    }


def get_advice(user: User, message: str) -> str:
    profile = user.profile
    lang    = _lang(profile)
    goals   = [g.title for g in user.goals if not g.is_done][:3]

    occ = (profile.occupation or "yoq") if profile else "yoq"
    gls = ", ".join(goals) or "yoq"

    prompt = f"""Sen vaqt menejment va produktivlik ekspertisan. {lang} tilida qisqa, amaliy maslahat ber (2-4 jumla).

Foydalanuvchi: kasbi={occ}, maqsadlari={gls}
Savol: {message}"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception:
        return _smart_mock(message)


def _smart_mock(message: str) -> str:
    m = message.lower()

    if any(w in m for w in ["erta", "uyg'on", "sabah", "tong"]):
        return "Erta turish uchun kechqurun bir xil vaqtda yotishni odat qiling. Uyg'onganingizda darhol yorug'lik yoqing va 5 daqiqa cho'zilish qiling. Telefonga qaramay, avval suv iching."

    if any(w in m for w in ["telefon", "ijtimoiy", "instagram", "tiktok", "social"]):
        return "Telefon vaqtini cheklash uchun 'Screen Time' yoki 'Digital Wellbeing' ilovasini o'rnating. Ish vaqtida bildirishnomalarni o'chiring. Ovqat paytida ham telefonsiz o'tiring — bu odat qilib olish 21 kun davom etadi."

    if any(w in m for w in ["stres", "stress", "charchad", "toliqd", "band"]):
        return "Stress ko'p bo'lsa, 'to'xtatish vaqti' belgilang — har 2 soatda 15 daqiqa dam. Hafta oxirida hech qanday ish qilmasdan to'liq dam oling. Bugungi eng muhim 3 vazifani aniqlang, qolganini ertaga qoldiring."

    if any(w in m for w in ["maqsad", "goal", "rejа", "plan", "nima qils"]):
        return "Maqsadlarni SMART usulida yozing: aniq, o'lchanadigan, erishish mumkin, real, muddatli. Katta maqsadni kichik haftalik vazifaga bo'ling. Har kuni kechqurun ertangi 1 ta asosiy vazifani belgilang."

    if any(w in m for w in ["uxla", "yot", "tun", "kech", "uyqu"]):
        return "Sifatli uyqu uchun har kuni bir xil vaqtda yoting. Uxlashdan 1 soat oldin ekrandan uzoqlashing. Xona haroratini 18-20 darajada ushlab turing. 7-8 soat uyqu — produktivlikni 40% oshiradi."

    if any(w in m for w in ["sport", "jismon", "harakat", "yugur", "gym"]):
        return "Sport vaqtini kalendaringizga yozing — xuddi muhim uchrashuv kabi. Kunda 30 daqiqa yurish ham yetarli. Ertalab sport qilish kun bo'yi energiya beradi. Kechqurun intensiv mashq uyquni buzishi mumkin."

    if any(w in m for w in ["kons", "focus", "diqqat", "fikr", "chalg'i"]):
        return "Pomodoro usulini sinab ko'ring: 25 daqiqa ish, 5 daqiqa dam. Ish paytida faqat bitta vazifaga e'tibor bering, bir vaqtda ko'p ish qilmang. Ish joyingizni tartibli saqlang — tartibsizlik diqqatni kamaytiradi."

    if any(w in m for w in ["vaqt", "behuda", "sarflad", "isrof", "yo'qot"]):
        return "Bir hafta davomida vaqtingizni kuzating — qayerga ko'p ketayotganini aniqlang. Har kuni 'vaqt o'g'rilari'ni ro'yxat qiling. Muhim vazifalarni tong paytida bajaring — bu vaqt eng samarali."

    if any(w in m for w in ["motivat", "ilhom", "istak", "hohish", "tashabbos"]):
        return "Motivatsiya his-tuyg'u, intizom esa ko'nikma. Hamma kuni ilhom kutib o'tirmang — intizomli bo'ling. Kichik g'alabalarni nishonlang. Nima uchun bu maqsadga erishmoqchi ekanligingizni yozib qo'ying."

    if any(w in m for w in ["ish", "work", "vazifa", "loyiha", "project"]):
        return "Ish samaradorligi uchun avval eng qiyin vazifani bajaring (Eat the Frog usuli). Har kuni ish boshida 10 daqiqa rejalang. Ish vaqtida email va chatlarni 2 soatda bir marta tekshiring."

    return "Vaqt menejmentda asosiy qoida: muhim ammo shoshilinch bo'lmagan vazifalarni ustuvor qiling. Har kuni 3 ta asosiy vazifa aniqlang va shu 3 tani albatta bajaring. Qolgan hamma narsa ikkinchi darajali."
