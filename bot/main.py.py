import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# 1. إعدادات البوت
TOKEN = 'حط_التوكن_حقك_هنا'
TOTAL_PAGES = 604
DATA_FILE = 'quran_data.json'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. وظائف حفظ وتحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 3. أحداث البوت
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ البوت شغال باسم: {bot.user.name}')
    print('--- جاهز لختمة رمضان ---')

# 4. دالة شريط الإنجاز (الرسم)
def get_progress_bar(current):
    percentage = min((current / TOTAL_PAGES) * 100, 100)
    length = 15
    filled = int(length * current // TOTAL_PAGES)
    bar = '🟩' * filled + '⬜' * (length - filled)
    return bar, int(percentage)

# 5. أمر تسجيل القراءة
@bot.tree.command(name="قراءة", description="سجل عدد الصفحات اللي قريتها")
@app_commands.describe(pages="كم صفحة قريت الحين؟")
async def read(interaction: discord.Interaction, pages: int):
    data = load_data()
    user_id = str(interaction.user.id)
    
    if user_id not in data:
        data[user_id] = 0
    
    data[user_id] += pages
    save_data(data)
    
    current_pages = data[user_id]
    bar, percent = get_progress_bar(current_pages)
    
    embed = discord.Embed(
        title="🌙 إنجاز قرآني جديد!",
        description=f"تقبل الله منك يا **{interaction.user.display_name}**",
        color=discord.Color.gold()
    )
    embed.add_field(name="📥 أضفت اليوم", value=f"{pages} صفحات", inline=True)
    embed.add_field(name="📖 مجموعك الكلي", value=f"{current_pages} / {TOTAL_PAGES}", inline=True)
    embed.add_field(name="📊 التقدم", value=f"{bar} {percent}%", inline=False)
    
    if current_pages >= TOTAL_PAGES:
        embed.set_footer(text="🎉 مبارك! ختمت المصحف، جعلها الله في ميزان حسناتك")
    else:
        embed.set_footer(text=f"باقي لك {TOTAL_PAGES - current_pages} صفحة على الختمة")
        
    await interaction.response.send_message(embed=embed)

# 6. أمر لوحة الصدارة (المنافسة)
@bot.tree.command(name="الترتيب", description="شوف مين أكثر واحد قرأ في السيرفر")
async def leaderboard(interaction: discord.Interaction):
    data = load_data()
    if not data:
        await interaction.response.send_message("لسه ما أحد بدأ يقرأ، كن أولهم!")
        return

    # ترتيب المستخدمين حسب عدد الصفحات
    sorted_users = sorted(data.items(), key=lambda item: item[1], reverse=True)
    
    leaderboard_text = ""
    for i, (u_id, p_count) in enumerate(sorted_users[:10], 1):
        member = interaction.guild.get_member(int(u_id))
        name = member.display_name if member else "عضو غادر"
        leaderboard_text += f"{i}. **{name}** - {p_count} صفحة\n"

    embed = discord.Embed(
        title="🏆 لوحة صدارة الختمة الرمضانية",
        description=leaderboard_text,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

bot.run('MTQ3MDgwNjU0NjUxNzcyMTExOA.GW2ljl.-FX0DpQZkajE5caMyOy68wPi1Y6IUNFsz4L1_I')