
from disnake.ext import commands
import os, importlib, disnake, json

token = "" # 봇토큰
intents = disnake.Intents.default()
bot = commands.InteractionBot(intents=intents)


@bot.event
async def on_ready():
    activity = disnake.Game(name="사전예약 관리")
    await bot.change_presence(status=disnake.Status.idle, activity=activity)
    print("Bot is ready!")
    



# 명령어 로드 함수
def load_commands():
    base_path = "commands"
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file).replace("/", ".").replace("\\", ".")[:-3]
                module = importlib.import_module(module_path)
                if hasattr(module, "setup"):
                    module.setup(bot)



# 명령어 로드
load_commands()

# 점검 상태 확인 함수
def is_maintenance():
    try:
        with open("maint.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("maintenance", False)
    except FileNotFoundError:
        return False

# 점검 모드 활성화/비활성화 명령어 (관리자용)
@bot.slash_command(name="점검모드")
async def maintenance_mode(inter: disnake.ApplicationCommandInteraction, 상태: bool):
    """점검 모드를 설정합니다 (관리자만 사용 가능)."""
    if not inter.author.guild_permissions.administrator:
        await inter.response.send_message(embed=disnake.Embed(title="```오류!```", description='권한이 없습니다.', color=0xff4040), ephemeral=False)
        return

    # 설정 파일 수정
    with open("maint.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    config["maintenance"] = 상태
    with open("maint.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    mode = "활성화" if 상태 else "비활성화"
    await inter.response.send_message(embed=disnake.Embed(title="**<:CHECK:1141002471297253538> | 점검 모드 활성화**", description=f"점검 모드가 **{mode}**되었습니다!", color=0x59ff85))

# 모든 명령어 실행 전에 점검 상태 확인
@bot.on_application_command
async def maintenance_check(ctx):
    if is_maintenance():

        await ctx.response.send_message(embed=disnake.Embed(title="**<:HammerAndSpanner:1147091339348029543>** | 점검 모드 안내", description='현재 봇이 점검중입니다.', color=0xFFB443), ephemeral=False)
        return False
    await bot.process_application_commands(ctx)

bot.run(token)