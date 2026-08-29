from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer


OUTPUT = Path(__file__).resolve().parents[1] / "data" / "UTC-Master-Knowledge-Base.pdf"
CHAPTERS = [
    (
        "BAB 1. PROFIL UTC",
        [
            ("1.1 Tentang UTC", "UNIDA Technology Care (UTC) melayani kebutuhan pemeriksaan, perawatan, dan perbaikan perangkat elektronik serta perlengkapan kantor di lingkungan Universitas Darussalam Gontor."),
            ("1.2 Batas Bantuan Chatbot", "Chatbot UTC memberikan informasi layanan dan arahan awal. Chatbot tidak dapat memastikan diagnosis, biaya, ketersediaan komponen, lama pengerjaan, status perbaikan, atau keputusan teknis."),
        ],
    ),
    (
        "BAB 2. LAYANAN UTC",
        [
            ("2.1 Laptop dan Komputer", "UTC menangani pemeriksaan, perawatan, dan perbaikan laptop, komputer, atau PC. Keluhan dapat meliputi perangkat lambat, tidak menyala, hang, panas berlebih, atau masalah perangkat lunak dan perangkat keras."),
            ("2.2 Handphone dan HP", "UTC menerima pemeriksaan, perawatan, dan perbaikan handphone, HP, atau ponsel. Untuk kerusakan berat atau kebutuhan khusus, penanganan akan dikoordinasikan lebih lanjut."),
            ("2.3 Printer", "UTC menangani pemeriksaan, perawatan, dan perbaikan printer. Sampaikan jenis printer dan gejala seperti hasil cetak bermasalah, tidak terdeteksi, atau pesan kesalahan saat berkonsultasi."),
            ("2.4 Perangkat Kantor", "UTC juga menangani perangkat kantor terkait, termasuk komputer, monitor, mouse, keyboard, dan kebutuhan perlengkapan teknologi yang memerlukan koordinasi layanan."),
        ],
    ),
    (
        "BAB 3. KONSULTASI DAN PENERIMAAN PERANGKAT",
        [
            ("3.1 Informasi Awal", "Pelanggan tidak harus mengetahui nama kerusakan. Sampaikan jenis perangkat, keluhan, dan gejala yang terlihat. Informasi ini membantu UTC melakukan pengecekan awal."),
            ("3.2 Pencatatan Perangkat", "Saat perangkat diterima, data pelanggan, data perangkat, keluhan, dan kondisi fisik awal dicatat. Pelanggan menerima nota penerimaan sebagai bukti untuk pengambilan unit."),
            ("3.3 Konsultasi dan Antar Jemput", "UTC menyediakan konsultasi awal. Ketersediaan layanan antar jemput perlu ditanyakan dan dikoordinasikan terlebih dahulu dengan admin UTC."),
        ],
    ),
    (
        "BAB 4. ALUR PENANGANAN SERVICE",
        [
            ("4.1 Pemeriksaan dan Diagnosis", "Teknisi memeriksa keluhan, kondisi awal, dan sumber masalah perangkat. Hasil diagnosis serta tindakan yang diperlukan disampaikan melalui admin sebelum proses lanjutan."),
            ("4.2 Perbaikan dan Komponen", "Perbaikan dilakukan sesuai hasil diagnosis. Penggantian komponen atau tindakan di luar pemeriksaan awal memerlukan konfirmasi pelanggan sebelum pekerjaan dilanjutkan."),
            ("4.3 Pengujian dan Penyerahan", "Setelah perbaikan, teknisi melakukan pengujian fungsi dan pemeriksaan akhir. Unit selesai diserahkan melalui admin setelah proses layanan dan administrasi diselesaikan."),
        ],
    ),
    (
        "BAB 5. KETENTUAN PELANGGAN",
        [
            ("5.1 Data dan Perangkat", "Pelanggan disarankan mencadangkan data penting sebelum service. UTC menangani perangkat dan kelengkapan yang tercatat pada nota penerimaan."),
            ("5.2 Persetujuan Tindakan", "Pelanggan perlu menyetujui pembongkaran, analisis, atau tindakan perbaikan yang diperlukan. Risiko khusus pada perangkat tertentu akan dijelaskan sebelum tindakan dilakukan."),
            ("5.3 Garansi Service", "Garansi service dapat berlaku untuk jenis kerusakan yang sama sesuai ketentuan pada nota dan kondisi perangkat. Ketentuan garansi suku cadang mengikuti ketentuan distributor atau komponen terkait."),
            ("5.4 Perangkat Lunak", "UTC tidak melayani instalasi perangkat lunak bajakan atau crack. Legalitas perangkat lunak dan sistem operasi pada perangkat pelanggan tetap menjadi tanggung jawab pelanggan."),
        ],
    ),
    (
        "BAB 6. INFORMASI OPERASIONAL",
        [
            ("6.1 Lokasi UTC", "UTC berlokasi di Gedung Zubair 205, Universitas Darussalam Gontor, Ponorogo. Pelanggan disarankan menghubungi admin UTC sebelum datang untuk memastikan informasi layanan terbaru."),
            ("6.2 Jadwal Pengambilan Unit", "Jadwal pengambilan barang service yang tercantum dalam ketentuan layanan adalah Sabtu sampai Kamis, pukul 08.00 sampai 15.00. Konfirmasikan jadwal terbaru kepada admin UTC sebelum datang."),
            ("6.3 Kabar Perbaikan", "Pelanggan menerima kabar perkembangan perbaikan melalui admin. Untuk status terbaru perangkat, hubungi admin UTC dengan menyiapkan informasi pada nota penerimaan."),
            ("6.4 Biaya dan Estimasi", "Biaya, ketersediaan komponen, dan estimasi pengerjaan ditentukan setelah pemeriksaan. UTC akan mengonfirmasi tindakan atau kebutuhan tambahan sebelum pekerjaan dilanjutkan."),
        ],
    ),
    (
        "BAB 7. PERTANYAAN UMUM",
        [
            ("7.1 Apakah UTC Bisa Memperbaiki HP", "Ya. UTC menerima pemeriksaan, perawatan, dan perbaikan handphone, HP, atau ponsel. Sampaikan jenis perangkat dan gejala kerusakannya kepada admin untuk arahan awal."),
            ("7.2 Apakah Harus Tahu Kerusakannya", "Tidak. Pelanggan cukup menjelaskan gejala perangkat, misalnya tidak menyala, lambat, hang, cepat panas, atau hasil cetak bermasalah."),
            ("7.3 Apakah Bisa Menanyakan Harga", "Biaya perbaikan baru dapat dipastikan setelah pemeriksaan perangkat. Admin akan membantu menyampaikan hasil pemeriksaan dan kebutuhan tindakan berikutnya."),
            ("7.4 Di Mana Lokasi UTC", "UTC berada di Gedung Zubair 205, Universitas Darussalam Gontor, Ponorogo. Hubungi admin UTC sebelum datang untuk memastikan informasi layanan terbaru."),
        ],
    ),
]


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"UTC Master Knowledge Base | Halaman {document.page}")
    canvas.restoreState()


def main():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("UtcTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=25, spaceAfter=14)
    subtitle = ParagraphStyle("UtcSubtitle", parent=styles["Normal"], fontSize=10, leading=15, textColor=HexColor("#4D5B64"), spaceAfter=20)
    chapter = ParagraphStyle("UtcChapter", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=20, spaceBefore=4, spaceAfter=13)
    section = ParagraphStyle("UtcSection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=15, spaceBefore=8, spaceAfter=5)
    body = ParagraphStyle("UtcBody", parent=styles["BodyText"], fontSize=10, leading=15, spaceAfter=8)
    story: list[Flowable] = [Paragraph("UTC Master Knowledge Base", title), Paragraph("Informasi layanan publik untuk chatbot UTC. Informasi yang berubah perlu dikonfirmasi kepada admin UTC.", subtitle)]

    for index, (chapter_title, sections) in enumerate(CHAPTERS):
        if index:
            story.append(PageBreak())
        story.append(Paragraph(chapter_title, chapter))
        for section_title, text in sections:
            story.append(Paragraph(section_title, section))
            story.append(Paragraph(text, body))
            story.append(Spacer(1, 4))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm).build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
