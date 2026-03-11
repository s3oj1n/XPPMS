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
    @bot.slash_command(name="유저조회", description="해당 유저가 사전예약한 모든 제품을 조회합니다.")
    async def 유저조회(
        interaction: disnake.ApplicationCommandInteraction,
        유저: disnake.Member
    ):
        await interaction.response.defer()
        author: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 🔒 권한 제한: 관리자가 아니면 본인만 조회 가능
        if role not in author.roles and 유저.id != author.id:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 접근 제한**",
                    description="본인 정보만 조회할 수 있습니다.\n다른 유저의 정보를 보려면 관리자 권한이 필요합니다.",
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

        # 🔍 해당 유저가 포함된 모든 제품 검색
        user_id = str(유저.id)
        found_products = []
        for product_name, entries in preorder_data.items():
            if isinstance(entries, list) and any(entry["id"] == user_id for entry in entries):
                info = next((e for e in entries if e["id"] == user_id), None)
                timestamp = info.get("TimeStamp", "정보 없음") if info else "정보 없음"
                hdadmin = info.get("HdAdmin", "정보 없음") if info else "정보 없음"
                found_products.append(f"🔹 `{product_name}` (등록: {timestamp}, 담당자: {hdadmin})")

        # ❌ 등록된 제품이 없는 경우
        if not found_products:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 등록 내역 없음**",
                    description=f"{유저.mention} 님은 현재 사전예약된 제품이 없습니다.",
                    color=0xffc000
                ),
                ephemeral=True
            )
            return

        # ✅ 결과 출력
        embed = disnake.Embed(
            title=f"**<:Receipt_1145338109488275486:1400072389840212039> | {유저.display_name} 님의 사전예약 목록**",
            description="\n".join(found_products),
            color=0x59ff85,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"총 {len(found_products)}개 제품 등록됨")

        # 🔐 일반 유저는 본인 정보만 보이게, 관리자도 기본은 ephemeral=True
        await interaction.followup.send(embed=embed, ephemeral=True)
