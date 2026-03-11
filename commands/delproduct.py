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
    @bot.slash_command(name="제품삭제", description="사전예약 제품을 삭제합니다.")
    async def 제품삭제(interaction: disnake.ApplicationCommandInteraction, name: str):
        await interaction.response.defer()

        user: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 관리자 역할 확인
        if role is None:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**⚠️ 오류 발생**",
                    description="config.json에 설정된 관리자 역할 ID를 서버에서 찾을 수 없습니다.",
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

        # preorder.json 불러오기
        try:
            with open("jsons/preorder.json", "r", encoding="utf-8") as f:
                preorder_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            preorder_data = {}

        # 존재 여부 확인
        if name not in preorder_data:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="****<:banned_1162727777523478548:1400072243525976146> | 오류 발생**",
                    description=f"'{name}' 제품은 존재하지 않습니다.",
                    color=0xff4040
                )
            )
            return

        # 백업용 JSON 파일 생성
        backup_data = {name: preorder_data[name]}
        backup_path = f"jsons/backup_{name}.json"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)

        # 제품 삭제
        del preorder_data[name]

        # preorder.json 저장
        with open("jsons/preorder.json", "w", encoding="utf-8") as f:
            json.dump(preorder_data, f, ensure_ascii=False, indent=4)

        # 로그 채널 전송
        log_channel = bot.get_channel(logch)
        if log_channel:
            embed = disnake.Embed(
                title="**<:banned_1162727777523478548:1400072243525976146> | 제품 삭제됨",
                description=f"{interaction.author.mention} 님이 '{name}' 사전예약 제품을 삭제했습니다.",
                color=0xff4040,
                timestamp=datetime.now()
            )
            await log_channel.send(embed=embed, file=disnake.File(backup_path))

        # 백업 파일 삭제 (임시 파일 정리)
        try:
            os.remove(backup_path)
        except Exception:
            pass

        # 사용자 피드백
        await interaction.followup.send(
            embed=disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 제품 삭제 완료",
                description=f"'{name}' 사전예약 제품을 삭제했습니다. 로그 채널에 백업 파일이 전송되었습니다.",
                color=0x59ff85
            )
        )
