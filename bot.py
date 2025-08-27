import discord
from discord.ext import commands

# ============ إعدادات IDs ============
TOKEN = "ضع_التوكن_هنا"  # ⚠️ حط توكن البوت هنا
GUILD_ID                = 1409565990387450038   # ID السيرفر
CHANNEL_VERIFY_ID       = 1410306211869491240   # روم "تفعيل"
CHANNEL_APPLICATIONS_ID = 1410306611179815013   # روم "استمارات-التفعيل"
ROLE_UNVERIFIED_ID      = 1410306854432800879   # رول "غير مفعل"
ROLE_VERIFIED_ID        = 1410307090659938324   # رول "مفعل"
ROLE_VERIFY_TEAM_ID     = 1410307338870460529   # رول "GALAXY VERIFICATION TEAM"
ROLE_BLACKLIST_ID       = 1410307196570308608   # رول "BLACK LIST"

# بنر
BANNER_URL = "https://cdn.discordapp.com/attachments/1408466066144890973/1410296250187907142/logo.png"

# ============ إعداد البوت ============
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ============ وظائف مساعدة ============
def has_role(member: discord.Member, role_id: int) -> bool:
    return discord.utils.get(member.roles, id=role_id) is not None

def only_verify_team(interaction: discord.Interaction) -> bool:
    return (interaction.user 
            and isinstance(interaction.user, discord.Member) 
            and has_role(interaction.user, ROLE_VERIFY_TEAM_ID))

# ============ عند دخول عضو ============
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    role = guild.get_role(ROLE_UNVERIFIED_ID)
    if role:
        await member.add_roles(role)

# ============ واجهة الأزرار للاستلام/القبول/الرفض ============
class ApplicationActionView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="📥 استلام", style=discord.ButtonStyle.gray)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not only_verify_team(interaction):
            await interaction.response.send_message("❌ هذا الزر للفريق فقط.", ephemeral=True)
            return
        await interaction.response.send_message("✅ تم الاستلام.", ephemeral=True)

    @discord.ui.button(label="✅ قبول", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not only_verify_team(interaction):
            await interaction.response.send_message("❌ هذا الزر للفريق فقط.", ephemeral=True)
            return
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        if member:
            unverified = guild.get_role(ROLE_UNVERIFIED_ID)
            verified = guild.get_role(ROLE_VERIFIED_ID)
            if unverified and unverified in member.roles:
                await member.remove_roles(unverified)
            if verified:
                await member.add_roles(verified)
        await interaction.response.send_message("✅ العضو تم تفعيله.", ephemeral=True)

    @discord.ui.button(label="❌ رفض", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not only_verify_team(interaction):
            await interaction.response.send_message("❌ هذا الزر للفريق فقط.", ephemeral=True)
            return
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        if member:
            try:
                await member.send("❌ عذرا تم رفضك في التفعيل لخادم غالاكسي. نتمنى لك حظاً أوفر المرة القادمة.")
            except:
                pass
        await interaction.response.send_message("🚫 العضو تم رفضه.", ephemeral=True)

# ============ نموذج الاستمارة ============
class VerificationFormModal(discord.ui.Modal, title="نموذج التفعيل — GALAXY RP"):
    q1 = discord.ui.TextInput(label="ما هو اسمك الحقيقي؟", required=True)
    q2 = discord.ui.TextInput(label="كم عمرك؟", required=True)
    q3 = discord.ui.TextInput(label="هل قرأت القوانين؟", required=True)
    q4 = discord.ui.TextInput(label="لماذا تريد الانضمام؟", required=True)
    q5 = discord.ui.TextInput(label="هل لديك خبرة في RP؟", required=True)
    q6 = discord.ui.TextInput(label="من اين عرفت السيرفر؟", required=True)
    q7 = discord.ui.TextInput(label="أي ملاحظات إضافية؟", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        apps_ch = interaction.guild.get_channel(CHANNEL_APPLICATIONS_ID)
        if not apps_ch:
            await interaction.response.send_message("❌ لم يتم العثور على روم الاستمارات.", ephemeral=True)
            return

        embed = discord.Embed(
            title="طلب تفعيل جديد — GALAXY RP",
            description=f"**المتقدم:** {interaction.user.mention}\n**ID:** `{interaction.user.id}`",
            color=discord.Color.blurple()
        )
        embed.set_image(url=BANNER_URL)
        embed.add_field(name="اسمك الحقيقي", value=self.q1.value, inline=False)
        embed.add_field(name="عمرك", value=self.q2.value, inline=False)
        embed.add_field(name="هل قرأت القوانين؟", value=self.q3.value, inline=False)
        embed.add_field(name="سبب الانضمام", value=self.q4.value, inline=False)
        embed.add_field(name="الخبرة في RP", value=self.q5.value, inline=False)
        embed.add_field(name="من أين عرفت السيرفر", value=self.q6.value, inline=False)
        embed.add_field(name="ملاحظات إضافية", value=self.q7.value or "—", inline=False)

        view = ApplicationActionView(interaction.user.id)
        await apps_ch.send(embed=embed, view=view)
        await apps_ch.send("──────────────────────────────")  # فاصل
        await interaction.response.send_message("✅ تم إرسال استمارتك، سيتم مراجعتها قريباً.", ephemeral=True)

# ============ زر التفعيل ============
class VerificationButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 اضغط هنا للتفعيل", style=discord.ButtonStyle.blurple)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_role(interaction.user, ROLE_BLACKLIST_ID):
            await interaction.response.send_message("🚫 لا يمكنك التفعيل لأنك في البلاك ليست.", ephemeral=True)
            return
        await interaction.response.send_modal(VerificationFormModal())

# ============ أمر نشر لوحة التفعيل ============
@bot.tree.command(name="post_verification_panel", description="ينشر لوحة التفعيل في روم التفعيل")
async def post_verification_panel(interaction: discord.Interaction):
    if interaction.channel.id != CHANNEL_VERIFY_ID:
        await interaction.response.send_message("❌ هذا الأمر فقط في روم التفعيل.", ephemeral=True)
        return

    embed = discord.Embed(
        title="GALAXY RP VERIFICATION CENTRE",
        description=(
            "مرحبا بك في نظام التفعيل لخادم غالاكسي\n\n"
            "📖 الرجاء قراءة القوانين للمعرفة الكاملة بالقوانين\n"
            "⚠️ عدم قراءة القوانين يعرضك لرفض التفعيل\n\n"
            "بعد القراءة اضغط زر **التفعيل** بالأسفل واملأ الاستمارة ليتم إرسالها للفريق.\n\n"
            "GALAXY RP VERIFICATION TEAM"
        ),
        color=discord.Color.blurple()
    )
    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message("✅ تم إرسال لوحة التفعيل.", ephemeral=True)
    await interaction.channel.send(embed=embed, view=VerificationButton())

# ============ تشغيل البوت ============
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced ({len(synced)}).")
    except Exception as e:
        print(f"❌ خطأ في مزامنة الأوامر: {e}")

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
