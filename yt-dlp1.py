import subprocess
import sys
import re
import shutil

# ========== Warna ANSI ========== #
def warna(teks, kode): return f"\033[{kode}m{teks}\033[0m"
MERAH = lambda teks: warna(teks, "91")
HIJAU = lambda teks: warna(teks, "92")
KUNING = lambda teks: warna(teks, "93")
BIRU = lambda teks: warna(teks, "94")
CYAN = lambda teks: warna(teks, "96")
TEBAL = lambda teks: warna(teks, "1")

# ========== Banner ========== #
def tampilkan_banner():
    print(KUNING("=" * 60))
    print(CYAN(r"""
     █████╗      ██╗      ██╗   ██╗ ██████╗     ██╗  ██╗███████╗██████╗ 
    ██╔══██╗     ██║      ██║   ██║██╔═══██╗    ██║ ██╔╝██╔════╝██╔══██╗
    ███████║     ██║      ██║   ██║██║   ██║    █████╔╝ █████╗  ██████╔╝
    ██╔══██║     ██║      ╚██╗ ██╔╝██║   ██║    ██╔═██╗ ██╔══╝  ██╔═══╝ 
    ██║  ██║     ███████╗  ╚████╔╝ ╚██████╔╝    ██║  ██╗███████╗██║     
    ╚═╝  ╚═╝     ╚══════╝   ╚═══╝   ╚═════╝     ╚═╝  ╚═╝╚══════╝╚═╝     
                             By A.M_356_HUNTER
    """))
    print(KUNING("=" * 60))


# ========== Ambil format dari yt-dlp ========== #
def ambil_format(url):
    hasil = subprocess.run(["yt-dlp", "-F", url], capture_output=True, text=True)
    return hasil.stdout

# ========== Filter format berdasarkan tipe ========== #
def filter_format(format_list, tipe="audio"):
    lines = format_list.splitlines()
    hasil = []
    for line in lines:
        if tipe == "audio" and re.search(r'\baudio only\b', line):
            kode = line.strip().split()[0]
            hasil.append(kode)
        elif tipe == "video" and not re.search(r'\baudio only\b', line) and not re.search(r'unknown', line):
            kode = line.strip().split()[0]
            hasil.append(kode)
    return hasil

# ========== Tampilkan pilihan ========== #
def tampilkan_dan_pilih(kode_list, label="format"):
    print(BIRU(f"\nPilih {label}:"))
    for i, kode in enumerate(kode_list, 1):
        print(f"[{i}] {HIJAU(kode)}")
    pilihan = input(KUNING("Masukkan nomor pilihan: "))
    try:
        index = int(pilihan) - 1
        return kode_list[index]
    except (ValueError, IndexError):
        print(MERAH("Pilihan tidak valid."))
        sys.exit(1)

# ========== Proses Unduh ========== #
def unduh(url, format_kode):
    ikon = "🔊" if "audio" in format_kode.lower() else "🎬"
    print(CYAN(f"\n{ikon} Mengunduh format {format_kode}...\n"))
    subprocess.run(["yt-dlp", "-f", format_kode, url])

# ========== Main Program ========== #
def main():
    tampilkan_banner()

    if not shutil.which("yt-dlp"):
        print(MERAH("yt-dlp tidak ditemukan. Pastikan sudah diinstal."))
        sys.exit(1)

    url = input(BIRU("Masukkan URL video: ")).strip()
    if not url:
        print(MERAH("URL tidak boleh kosong."))
        sys.exit(1)

    print(HIJAU("\nPilih jenis unduhan:"))
    print("[1] Audio")
    print("[2] Video")
    pilihan = input(KUNING("Pilihan (1/2): ")).strip()

    format_list = ambil_format(url)

    if pilihan == "1":
        audio_list = filter_format(format_list, "audio")
        kode = tampilkan_dan_pilih(audio_list, "audio")
        unduh(url, kode)

    elif pilihan == "2":
        video_list = filter_format(format_list, "video")
        kode_video = tampilkan_dan_pilih(video_list, "video")

        gabung = input(KUNING("Gabungkan dengan audio? (y/n): ")).strip().lower()
        if gabung == 'y':
            audio_list = filter_format(format_list, "audio")
            kode_audio = tampilkan_dan_pilih(audio_list, "audio")
            unduh(url, f"{kode_video}+{kode_audio}")
        else:
            unduh(url, kode_video)
    else:
        print(MERAH("Pilihan tidak valid."))
        sys.exit(1)

if __name__ == "__main__":
    main()
