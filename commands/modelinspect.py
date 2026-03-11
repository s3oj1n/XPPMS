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
    @bot.slash_command(name="제품조회", description="특정 제품에 등록된 유저 목록을 조회합니다.")
    async def 제품조회(
        interaction: disnake.ApplicationCommandInteraction,
        제품이름: str
    ):
        await interaction.response.defer()
        author: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 🔒 관리자만 조회 가능
        if role not in author.roles:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 접근 제한**",
                    description="이 명령어는 관리자만 사용할 수 있습니다.",
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

        # ❌ 제품 존재 확인
        if 제품이름 not in preorder_data or not isinstance(preorder_data[제품이름], list):
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 조회 실패**",
                    description=f"'{제품이름}' 제품은 존재하지 않거나 등록된 유저가 없습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        entries = preorder_data[제품이름]

        # ❌ 등록된 유저가 없는 경우
        if len(entries) == 0:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 등록된 유저 없음**",
                    description=f"'{제품이름}' 제품에는 현재 등록된 유저가 없습니다.",
                    color=0xffc000
                ),
                ephemeral=True
            )
            return

        # 🧾 유저 목록 구성
        user_list = []
        for entry in entries:
            user_id = entry.get("id", "알 수 없음")
            timestamp = entry.get("TimeStamp", "정보 없음")
            hdadmin = entry.get("HdAdmin", "정보 없음")
            user_mention = f"<@{user_id}>"
            user_list.append(f"👤 {user_mention} | 등록일: {timestamp} | 담당자: {hdadmin}")

        # ✅ 결과 출력
        embed = disnake.Embed(
            title=f"**<:Receipt_1145338109488275486:1400072389840212039> | '{제품이름}' 사전예약 목록**",
            description="\n".join(user_list),
            color=0x59ff85,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"총 {len(user_list)}명 등록됨")
        await interaction.followup.send(embed=embed, ephemeral=True)
