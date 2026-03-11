import disnake, json, os, sys, asyncio
from disnake.ext import commands
from datetime import datetime, timedelta, timezone

# ⚙️ Windows 환경 asyncio 안정화
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True  # DM 전송 위해 필요

# 📂 config.json 불러오기
try:
    with open("jsons/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("⚠️ config.json 파일을 찾을 수 없습니다.")
    sys.exit(1)

adminid = int(config["AdminRole"])
logch = config["logch"]

def setup(bot):
    @bot.slash_command(name="유저삭제", description="사전예약 제품에서 유저를 삭제합니다.")
    async def 유저삭제(
        interaction: disnake.ApplicationCommandInteraction,
        제품이름: str,
        유저: disnake.Member
    ):
        await interaction.response.defer()
        author: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 🔒 관리자 확인
        if role not in author.roles:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 권한 부족**",
                    description="이 명령어를 사용할 권한이 없습니다. 관리자 역할이 필요합니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        preorder_path = "jsons/preorder.json"
        try:
            with open(preorder_path, "r", encoding="utf-8") as f:
                preorder_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="⚠️ 데이터 없음",
                    description="사전예약 데이터 파일이 존재하지 않습니다.",
                    color=0xffc000
                ),
                ephemeral=True
            )
            return

        # ❌ 제품 확인
        if 제품이름 not in preorder_data or not isinstance(preorder_data[제품이름], list):
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 삭제 실패**",
                    description=f"'{제품이름}' 제품은 존재하지 않습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        # ⚙️ 유저 존재 여부 확인
        before_count = len(preorder_data[제품이름])
        preorder_data[제품이름] = [
            entry for entry in preorder_data[제품이름] if entry["id"] != str(유저.id)
        ]

        if len(preorder_data[제품이름]) == before_count:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 유저 미등록**",
                    description=f"{유저.mention} 님은 '{제품이름}' 제품에 등록되어 있지 않습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        # 💾 저장
        with open(preorder_path, "w", encoding="utf-8") as f:
            json.dump(preorder_data, f, ensure_ascii=False, indent=4)

        # 🪶 로그 채널 전송
        log_channel = bot.get_channel(logch)
        if log_channel:
            embed = disnake.Embed(
                title="**<:banned_1162727777523478548:1400072243525976146> | 유저 삭제됨**",
                description=f"관리자: {author.mention}\n삭제된 유저: {유저.mention}\n제품 이름: `{제품이름}`",
                color=0xff4040,
                timestamp=datetime.now()
            )
            try:
                await asyncio.wait_for(log_channel.send(embed=embed), timeout=10)
            except asyncio.TimeoutError:
                print("⚠️ 로그 채널 전송이 10초 내에 완료되지 않아 스킵합니다.")

        # 📩 DM 알림
        try:
            dm_embed = disnake.Embed(
                title="**<:banned_1162727777523478548:1400072243525976146> | 사전예약 삭제 안내**",
                description=f"안녕하세요 {유저.mention} 님,\n\n'{제품이름}' 제품의 사전예약 등록이 관리자에 의해 삭제되었습니다.\n삭제 담당자: `{author.name}`",
                color=0xff4040
            )
            await asyncio.wait_for(유저.send(embed=dm_embed), timeout=10)
        except disnake.Forbidden:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="⚠️ DM 전송 실패",
                    description=f"{유저.mention} 님에게 DM을 보낼 수 없습니다. (DM 차단 또는 설정 문제)",
                    color=0xffc000
                ),
                ephemeral=True
            )

        # 🎉 완료 메시지
        await interaction.followup.send(
            embed=disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 유저 삭제 완료**",
                description=f"{유저.mention} 님을 '{제품이름}' 사전예약 목록에서 삭제했습니다.",
                color=0x59ff85
            )
        )