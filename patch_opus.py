import os
import site

def patch_voice_recv():
    for path in site.getsitepackages() + [site.getusersitepackages()]:
        opus_file = os.path.join(path, "discord", "ext", "voice_recv", "opus.py")
        if os.path.exists(opus_file):
            print(f"✅ Найден файл: {opus_file}")

            with open(opus_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Если патч уже стоит — не трогаем
            if "ПРОПУЩЕН ПОВРЕЖДЁННЫЙ ПАКЕТ" in content:
                print("✅ Патч уже установлен.")
                return

            # Минимальный патч — только одна строка decode
            old_line = '            pcm = self._decoder.decode(packet.decrypted_data, fec=False)'
            new_line = """            try:
                pcm = self._decoder.decode(packet.decrypted_data, fec=False)
            except Exception as e:
                if "corrupted" in str(e).lower() or "opus" in str(e).lower():
                    print(f"⚠️ ПРОПУЩЕН ПОВРЕЖДЁННЫЙ ПАКЕТ (DAVE)")
                    pcm = b''
                else:
                    raise"""

            content = content.replace(old_line, new_line)

            with open(opus_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Минимальный патч успешно применён!")
            print("   Теперь бот не будет крашиться на damaged packets.")
            return

    print("❌ Не удалось найти opus.py")

if __name__ == "__main__":
    patch_voice_recv()