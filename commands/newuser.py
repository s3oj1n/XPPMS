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
    @bot.slash_command(name="유저등록", description="사전예약 제품에 유저를 등록합니다.")
    async def 유저등록(
        interaction: disnake.ApplicationCommandInteraction,
        제품이름: str,
        유저: disnake.Member
    ):
        await interaction.response.defer()
        author: disnake.Member = interaction.author
        role = interaction.guild.get_role(adminid)

        # 🔒 관리자 권한 확인
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

        # 📄 preorder.json 불러오기
        preorder_path = "jsons/preorder.json"
        try:
            with open(preorder_path, "r", encoding="utf-8") as f:
                preorder_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            preorder_data = {}

        # ❌ 제품 존재 확인
        if 제품이름 not in preorder_data:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 등록 실패**",
                    description=f"'{제품이름}' 제품은 존재하지 않습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        # 🧩 제품 데이터가 리스트인지 확인
        if not isinstance(preorder_data[제품이름], list):
            preorder_data[제품이름] = []

        # ⚠️ 중복 등록 방지
        if any(entry["id"] == str(유저.id) for entry in preorder_data[제품이름]):
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="**<:banned_1162727777523478548:1400072243525976146> | 이미 등록된 유저**",
                    description=f"{유저.mention} 님은 이미 '{제품이름}' 제품에 등록되어 있습니다.",
                    color=0xff4040
                ),
                ephemeral=True
            )
            return

        # 📝 새 유저 등록 정보 추가
        new_entry = {
            "id": str(유저.id),
            "TimeStamp": datetime.now(timezone(timedelta(hours=9))).strftime("%Y년 %m월 %d일 %H:%M"),
            "HdAdmin": str(author.name)
        }
        preorder_data[제품이름].append(new_entry)

        # 💾 저장
        os.makedirs("jsons", exist_ok=True)
        with open(preorder_path, "w", encoding="utf-8") as f:
            json.dump(preorder_data, f, ensure_ascii=False, indent=4)

        # 🪶 로그 채널 전송 (타임아웃 보호)
        log_channel = bot.get_channel(logch)
        if log_channel:
            embed = disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 유저 등록됨**",
                description=(
                    f"관리자: {author.mention}\n"
                    f"등록된 유저: {유저.mention}\n"
                    f"제품 이름: `{제품이름}`"
                ),
                color=0x59ff85,
                timestamp=datetime.now()
            )
            try:
                await asyncio.wait_for(log_channel.send(embed=embed), timeout=10)
            except asyncio.TimeoutError:
                print("⚠️ 로그 채널 전송이 10초 내에 완료되지 않아 스킵합니다.")
            except Exception as e:
                print(f"⚠️ 로그 채널 전송 중 오류 발생: {e}")

        # 📩 유저에게 DM 전송 (타임아웃 보호)
        try:
            dm_embed = disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 사전예약 등록 완료**",
                description=(
                    f"안녕하세요 {유저.mention} 님!\n\n"
                    f"'{제품이름}' 제품의 사전예약이 정상적으로 등록되었습니다.\n"
                    f"등록 일시: `{new_entry['TimeStamp']}`\n"
                    f"등록 담당자: `{author.name}`"
                ),
                color=0x59ff85
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
        except asyncio.TimeoutError:
            print(f"⚠️ {유저} DM 전송이 10초를 초과해 스킵됨")
        except Exception as e:
            print(f"⚠️ DM 전송 중 오류 발생: {e}")

        # 🎉 완료 메시지 (이모지 그대로 유지)
        await interaction.followup.send(
            embed=disnake.Embed(
                title="**<:CHECK_1141002471297253538:1400072262765514854> | 유저 등록 완료**",
                description=f"{유저.mention} 님을 '{제품이름}' 사전예약 제품에 등록했습니다.",
                color=0x59ff85
            )
        )
