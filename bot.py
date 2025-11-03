import pandas as pd
from rapidfuzz import process, fuzz  # type: ignore
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔗 Replace with your Google Sheet CSV link:
GOOGLE_SHEET_CSV_URLS = [
   "https://docs.google.com/spreadsheets/d/1OA6b6PcBRAQE98-4C7dVFRB0r4QtbkXEGQoVMEWwwns/export?format=csv&gid=0"
]

def load_data():
    all_data = {}

    for url in GOOGLE_SHEET_CSV_URLS:
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip().str.lower()

            # detect columns automatically
            question_col = None
            answer_col = None
            for col in df.columns:
                if "question" in col or "سؤال" in col:
                    question_col = col
                elif "answer" in col or "اجابة" in col or "إجابة" in col:
                    answer_col = col

            if not question_col or not answer_col:
                print(f"⚠️ Skipping {url} — missing Question/Answer columns.")
                continue

            # build dictionary from this sheet
            for q, a in zip(df[question_col], df[answer_col]):
                if pd.notna(q) and pd.notna(a):
                    all_data[str(q).strip().lower()] = str(a).strip()

            print(f"✅ Loaded {len(df)} rows from {url}")

        except Exception as e:
            print(f"❌ Error loading {url}: {e}")

    return all_data

qa_data = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحبًا! اسألني أي سؤال من الجداول المتاحة!")

async def reply_with_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip().lower()

    # ✅ Exact match first
    if user_question in qa_data:
        await update.message.reply_text(qa_data[user_question])
        return

    # 🧠 Keyword match — collect all matching questions
    matched_answers = []
    for q, a in qa_data.items():
        for word in user_question.split():
            if len(word) > 2 and word in q:
                matched_answers.append((q, a))
                break  # avoid duplicate matches for same question

    if matched_answers:
        # send all matches
        reply_text = "🔎 وجدت أكثر من إجابة محتملة:\n\n"
        for i, (q, a) in enumerate(matched_answers[:5], start=1):  # limit to top 5
            reply_text += f"{i}. 📝 *السؤال:* {q}\n💡 *الإجابة:* {a}\n\n"
        await update.message.reply_text(reply_text, parse_mode="Markdown")
        return

    # 🔍 Fuzzy match (find closest question)
    best_match = process.extractOne(user_question, qa_data.keys(), scorer=fuzz.token_sort_ratio)

    if best_match and best_match[1] > 70:
        answer = qa_data[best_match[0]]
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("عذرًا، لا أجد إجابة لهذا السؤال.")

def main():
    app = ApplicationBuilder().token("8108891216:AAGeiSFEUjwpERuN7cYuGwxE8IRmzAvXXVQ").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_with_answer))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
