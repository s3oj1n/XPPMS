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
    @bot.slash_command(name="제품목록",description="현재 제품별 예약 현황을 확인합니다.")
    async def 제품목록(inter: disnake.ApplicationCommandInteraction):
        """제품별 예약자 수를 표시하는 명령어"""
        await inter.response.defer()
        author: disnake.Member = inter.author
        user: disnake.Member = inter.author
        role = inter.guild.get_role(adminid)

        # 관리자 역할 확인
        if role is None:
            await inter.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 오류 발생**",
                    description="⚠️ config.json에 설정된 관리자 역할 ID를 서버에서 찾을 수 없습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        if role not in user.roles:
            await inter.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 권한 부족**",
                    description="이 명령어를 사용할 권한이 없습니다. 관리자 역할이 필요합니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return
        try:
            # JSON 파일 불러오기
            with open("jsons/Preorder.json", "r", encoding="utf-8") as f:
                preorder_data = json.load(f)

            # 임베드 생성
            embed = disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 제품별 예약 현황**",
                description="사전예약 제품 목록입니다.",
                color=0x59ff85
            )

            total_count = 0

            for product, reservations in preorder_data.items():
                count = len(reservations)
                total_count += count
                embed.add_field(
                    name=f"💡 {product}",
                    value=f"예약 인원: **{count}명**",
                    inline=False
                )

            embed.set_footer(text=f"총 예약 인원 수: {total_count}명")

            await inter.followup.send(embed=embed)

        except FileNotFoundError:
            await inter.followup.send("⚠️ Preorder.json 파일을 찾을 수 없습니다.", ephemeral=True)
        except json.JSONDecodeError:
            await inter.followup.send("⚠️ JSON 파일이 손상되었습니다.", ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"❌ 오류 발생: {e}", ephemeral=True)
