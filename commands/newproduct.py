import disnake, asyncio, json, random, sqlite3, os, httpx, sys, string
from disnake.ext import commands
from disnake.ui import View, Button, Modal, TextInput
from disnake.enums import TextInputStyle
from datetime import datetime, timedelta, timezone

intents = disnake.Intents.default()
intents.message_content = True

# config.json 불러오기
try:
    with open("jsons/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("⚠️ config.json 파일을 찾을 수 없습니다.")
    sys.exit(1)

adminid = int(config["AdminRole"])
logch = config["logch"]

def setup(bot):
    @bot.slash_command(name="제품생성", description="")
    async def 제품생성(interaction: disnake.ApplicationCommandInteraction, name: str):
        await interaction.response.defer()
        # config.json 불러오기
        try:
            with open("jsons/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            await interaction.followup.send("🚫 config.json 파일을 찾을 수 없습니다.")
            return
    
        user: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 관리자 역할 확인
        if role is None:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 오류 발생**",
                    description="⚠️ config.json에 설정된 관리자 역할 ID를 서버에서 찾을 수 없습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        if role not in user.roles:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 권한 부족**",
                    description="이 명령어를 사용할 권한이 없습니다. 관리자 역할이 필요합니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return


        log_channel_id = config.get("logch")
        if not log_channel_id:
            await interaction.followup.send("🚫 config.json에 logch 항목이 없습니다.")
            return

        # preorder.json 불러오기
        try:
            with open("jsons/preorder.json", "r", encoding="utf-8") as f:
                preorder_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            preorder_data = {}

        # 이미 존재하는 제품인지 확인
        if name in preorder_data:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 오류 발생**",
                    description=(
                        f"{name}은 이미 존재합니다."
                    ),
                    color=0xff4040
                )
            )
            return

        # 새 항목 생성
        preorder_data[name] = [

        ]


        # 파일 저장
        with open("jsons/preorder.json", "w", encoding="utf-8") as f:
            json.dump(preorder_data, f, ensure_ascii=False, indent=4)

        # 로그 채널로 전송
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 새 제품 생성**",
                description=f"{interaction.author.mention} 님이 새 사전예약 제품인 {name}을(를) 생성했습니다.",
                color=0x59ff85
            )
            await log_channel.send(embed=embed)

        # 유저에게 피드백
        await interaction.followup.send(
            embed=disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 새 제품 생성**",
                description=f"새 사전예약 제품인 {name}을(를) 생성했습니다.",
                color=0x59ff85
            )
        )

