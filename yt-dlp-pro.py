import subprocess
import sys
import re
import shutil

# ========== Warna ANSI ========== #
def warna(teks, kode):
    return f"\033[{kode}m{teks}\033[0m"

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

# ========== Cek Dependensi ========== #
def cek_dependensi():
    if not shutil.which("yt-dlp"):
        print(MERAH("Error: yt-dlp tidak ditemukan. Harap instal terlebih dahulu."))
        sys.exit(1)
    
    if not shutil.which("ffmpeg"):
        print(MERAH("Error: FFmpeg tidak ditemukan. Diperlukan untuk menggabungkan audio dan video."))
        print(KUNING("Silakan instal FFmpeg terlebih dahulu."))
        sys.exit(1)

# ========== Ambil format dari yt-dlp ========== #
def ambil_format(url):
    try:
        hasil = subprocess.run(["yt-dlp", "-F", url], capture_output=True, text=True, check=True)
        return hasil.stdout
    except subprocess.CalledProcessError:
        print(MERAH("Gagal mendapatkan format. Periksa URL atau koneksi internet."))
        sys.exit(1)

# ========== Filter format ========== #
def filter_format(format_list, tipe="audio"):
    lines = format_list.splitlines()
    hasil = []
    
    for line in lines:
        if tipe == "audio" and re.search(r'\baudio only\b', line):
            # Prioritaskan format audio yang kompatibel (m4a/aac/mp3)
            if any(x in line.lower() for x in ['m4a', 'aac', 'mp3', 'opus']):
                hasil.append((line.strip().split()[0], line.strip()))
        elif tipe == "video" and re.search(r'\bvideo only\b', line):
            # Prioritaskan format video yang kompatibel (mp4/webm)
            if any(x in line.lower() for x in ['mp4', 'webm']):
                hasil.append((line.strip().split()[0], line.strip()))
        elif tipe == "combined" and not re.search(r'\b(?:audio only|video only)\b', line):
            # Format yang sudah mengandung audio dan video
            hasil.append((line.strip().split()[0], line.strip()))
    
    return hasil

# ========== Tampilkan pilihan ========== #
def tampilkan_dan_pilih(format_data, label="format"):
    print(BIRU(f"\nPilih {label}:"))
    for i, (kode, detail) in enumerate(format_data, 1):
        print(f"[{i}] {HIJAU(kode)} - {detail}")
    
    while True:
        pilihan = input(KUNING("Masukkan nomor pilihan: ")).strip()
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(format_data):
            return format_data[int(pilihan)-1][0]
        print(MERAH("Pilihan tidak valid. Silakan coba lagi."))

# ========== Proses Unduh ========== #
def unduh(url, format_kode, gabungkan=False):
    ikon = "🔊" if "audio" in format_kode.lower() else "🎬"
    print(CYAN(f"\n{ikon} Mengunduh format {format_kode}...\n"))
    
    cmd = [
        "yt-dlp",
        "-f", format_kode,
        "--embed-thumbnail",
        "--embed-metadata",
        "--no-warnings",
        "--ignore-errors",
        "--output", "%(title)s.%(ext)s",
        url
    ]
    
    if gabungkan:
        cmd.extend([
            "--merge-output-format", "mp4",
            "--audio-format", "best",
            "--recode-video", "mp4",
            "--postprocessor-args", "-c:v copy -c:a aac"  # Pastikan audio dikonversi ke AAC yang kompatibel
        ])
    
    try:
        subprocess.run(cmd, check=True)
        print(HIJAU("\nUnduhan berhasil!"))
    except subprocess.CalledProcessError as e:
        print(MERAH(f"\nError saat mengunduh: {e}"))
        sys.exit(1)

# ========== Main Program ========== #
def main():
    tampilkan_banner()
    cek_dependensi()

    url = input(BIRU("Masukkan URL video: ")).strip()
    if not url:
        print(MERAH("URL tidak boleh kosong."))
        sys.exit(1)

    print(HIJAU("\nPilih jenis unduhan:"))
    print("[1] Audio saja")
    print("[2] Video dengan audio (rekomendasi)")
    print("[3] Pilih manual video dan audio terpisah")
    pilihan = input(KUNING("Pilihan (1/2/3): ")).strip()

    format_list = ambil_format(url)

    if pilihan == "1":
        audio_list = filter_format(format_list, "audio")
        if not audio_list:
            print(MERAH("Format audio tidak ditemukan."))
            sys.exit(1)
        kode = tampilkan_dan_pilih(audio_list, "audio")
        unduh(url, kode)

    elif pilihan == "2":
        combined_list = filter_format(format_list, "combined")
        if combined_list:
            print(HIJAU("\nFormat yang sudah mengandung video dan audio:"))
            kode = tampilkan_dan_pilih(combined_list, "video+audio")
            unduh(url, kode)
        else:
            print(KUNING("\nTidak ada format gabungan, mencoba menggabungkan terpisah..."))
            video_list = filter_format(format_list, "video")
            if not video_list:
                print(MERAH("Format video tidak ditemukan."))
                sys.exit(1)
            kode_video = tampilkan_dan_pilih(video_list, "video")

            audio_list = filter_format(format_list, "audio")
            if not audio_list:
                print(MERAH("Format audio tidak ditemukan."))
                sys.exit(1)
            kode_audio = tampilkan_dan_pilih(audio_list, "audio")

            unduh(url, f"{kode_video}+{kode_audio}", gabungkan=True)

    elif pilihan == "3":
        video_list = filter_format(format_list, "video")
        if not video_list:
            print(MERAH("Format video tidak ditemukan."))
            sys.exit(1)
        kode_video = tampilkan_dan_pilih(video_list, "video")

        audio_list = filter_format(format_list, "audio")
        if not audio_list:
            print(MERAH("Format audio tidak ditemukan."))
            sys.exit(1)
        kode_audio = tampilkan_dan_pilih(audio_list, "audio")

        unduh(url, f"{kode_video}+{kode_audio}", gabungkan=True)

    else:
        print(MERAH("Pilihan tidak valid."))
        sys.exit(1)

if __name__ == "__main__":
    main()
