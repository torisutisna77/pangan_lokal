import io
from datetime import datetime
import pandas as pd
from fpdf import FPDF


def export_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame ke format Excel (.xlsx)"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Hasil Analisis")
    return output.getvalue()


def export_pdf(df: pd.DataFrame, title: str = "Laporan Analisis Pangan Lokal") -> bytes:
    """Export DataFrame ke format PDF (kompatibel dengan berbagai versi fpdf2)"""
    pdf = FPDF()
    pdf.add_page()

    # Judul
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=True, align="C")

    # Tanggal
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 8, f"Dicetak: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # Ambil kolom (maksimal 6 agar muat)
    cols = list(df.columns)[:6]

    if len(cols) == 0:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Tidak ada data untuk ditampilkan", ln=True)
    else:
        col_width = 190 / len(cols)

        # Header
        pdf.set_font("Arial", "B", 7)
        for col in cols:
            header = str(col)[:13]
            pdf.cell(col_width, 7, header, border=1)
        pdf.ln()

        # Isi data (maksimal 35 baris)
        pdf.set_font("Arial", "", 6)
        for _, row in df.head(35).iterrows():
            for col in cols:
                val = "" if pd.isna(row[col]) else str(row[col])
                pdf.cell(col_width, 6, val[:13], border=1)
            pdf.ln()

    # ========== PERBAIKAN OUTPUT PDF ==========
    try:
        # Cara modern fpdf2
        result = pdf.output()
    except TypeError:
        # Fallback untuk versi lama
        result = pdf.output(dest="S")

    # Pastikan hasilnya selalu bytes
    if isinstance(result, bytes):
        return result
    elif isinstance(result, bytearray):
        return bytes(result)
    elif isinstance(result, str):
        return result.encode("latin-1")
    else:
        # Last resort
        return bytes(str(result), encoding="latin-1")