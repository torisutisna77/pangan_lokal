import streamlit as st
import pandas as pd
import plotly.express as px
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import shap
import matplotlib.pyplot as plt

from database import run_query
from export_utils import export_excel, export_pdf


def show_dashboard():
    st.header("📊 Dashboard Analisis + XGBoost + SHAP")

    # ==================== AMBIL DATA ====================
    raw = run_query("""
        SELECT 
            d.id as daerah_id,
            d.nama_daerah, 
            d.pulau, 
            k.id as komoditas_id,
            k.nama_komoditas, 
            p.tahun,
            p.produksi_ton, 
            p.luas_ha, 
            p.produktivitas,
            p.curah_hujan_mm, 
            p.suhu_c, 
            p.indeks_kearifan, 
            p.status_gagal_panen
        FROM data_produksi p
        JOIN daerah d ON p.daerah_id = d.id
        JOIN komoditas k ON p.komoditas_id = k.id
        ORDER BY p.tahun DESC
    """)

    if not raw or len(raw) < 5:
        st.warning("Data produksi masih sangat sedikit. Minimal disarankan 15–20 baris data untuk analisis yang baik.")
        st.info("Silakan input data melalui menu **Data Produksi**.")
        return

    df_all = pd.DataFrame(raw)

    # ========== PERBAIKAN TIPE DATA (PENTING) ==========
    numeric_columns = [
        "produksi_ton", "luas_ha", "produktivitas",
        "curah_hujan_mm", "suhu_c", "indeks_kearifan",
        "status_gagal_panen", "tahun"
    ]

    for col in numeric_columns:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")

    # Hapus baris yang memiliki nilai kosong di kolom penting
    df_all = df_all.dropna(subset=[
        "luas_ha", "curah_hujan_mm", "suhu_c",
        "produktivitas", "status_gagal_panen", "indeks_kearifan"
    ])

    if len(df_all) < 5:
        st.warning("Setelah pembersihan data, jumlah data terlalu sedikit.")
        return

    # ==================== FILTER ====================
    st.subheader("🔍 Filter Data Analisis")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        daftar_daerah = ["Semua Daerah"] + sorted(df_all["nama_daerah"].dropna().unique().tolist())
        selected_daerah = st.multiselect(
            "Pilih Daerah",
            options=daftar_daerah,
            default=["Semua Daerah"]
        )

    with col_f2:
        daftar_komoditas = ["Semua Komoditas"] + sorted(df_all["nama_komoditas"].dropna().unique().tolist())
        selected_komoditas = st.multiselect(
            "Pilih Bahan Pangan / Komoditas",
            options=daftar_komoditas,
            default=["Semua Komoditas"]
        )

    with col_f3:
        tahun_min = int(df_all["tahun"].min())
        tahun_max = int(df_all["tahun"].max())
        selected_tahun = st.slider(
            "Rentang Tahun",
            min_value=tahun_min,
            max_value=tahun_max,
            value=(tahun_min, tahun_max)
        )

    # Terapkan filter
    df = df_all.copy()

    if "Semua Daerah" not in selected_daerah and selected_daerah:
        df = df[df["nama_daerah"].isin(selected_daerah)]

    if "Semua Komoditas" not in selected_komoditas and selected_komoditas:
        df = df[df["nama_komoditas"].isin(selected_komoditas)]

    df = df[
        (df["tahun"] >= selected_tahun[0]) &
        (df["tahun"] <= selected_tahun[1])
    ]

    if len(df) < 5:
        st.warning(f"Data setelah filter hanya tersisa **{len(df)}** baris. Perlonggar filter agar analisis bisa berjalan.")
        return

    st.success(f"Menampilkan **{len(df)}** data setelah filter diterapkan.")

    # ==================== METRIK ====================
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Data", len(df))
    c2.metric("Risiko Gagal Panen", f"{df['status_gagal_panen'].mean()*100:.1f}%")
    c3.metric("Rata-rata Produktivitas", f"{df['produktivitas'].mean():.2f} ton/ha")
    c4.metric("Rata-rata Kearifan Lokal", f"{df['indeks_kearifan'].mean():.2f} / 5")

    # ==================== VISUALISASI ====================
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        risiko_pulau = df.groupby("pulau")["status_gagal_panen"].mean().reset_index()
        fig1 = px.bar(
            risiko_pulau,
            x="pulau",
            y="status_gagal_panen",
            title="Rata-rata Risiko Gagal Panen per Pulau",
            labels={"status_gagal_panen": "Proporsi Gagal Panen"},
            color="status_gagal_panen",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_v2:
        fig2 = px.box(
            df,
            x="pulau",
            y="indeks_kearifan",
            title="Distribusi Indeks Kearifan Lokal per Pulau",
            color="pulau"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ==================== MODEL XGBOOST ====================
    st.markdown("---")
    st.subheader("🤖 Hasil Analisis Model XGBoost")

    features = ["luas_ha", "curah_hujan_mm", "suhu_c", "indeks_kearifan", "produktivitas"]

    # Pastikan lagi tipe data numerik
    for col in features:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=features + ["status_gagal_panen"])

    if len(df) < 5:
        st.warning("Setelah pembersihan data, jumlah data terlalu sedikit untuk melatih model.")
        return

    X = df[features]
    y = df["status_gagal_panen"].astype(int)

    if y.nunique() < 2:
        st.warning("Data target (Status Gagal Panen) hanya memiliki 1 kelas setelah difilter. Tidak bisa melatih model klasifikasi.")
        st.info("Coba perlonggar filter atau tambahkan lebih banyak data dengan status yang berbeda (0 dan 1).")
    else:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42, stratify=y
            )

            model = XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                eval_metric="logloss"
            )
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)

            col_m1, col_m2 = st.columns(2)

            with col_m1:
                st.metric("Akurasi Model", f"{acc*100:.1f}%")
                st.text("Classification Report:")
                st.code(classification_report(y_test, y_pred, target_names=["Aman", "Gagal Panen"]))

            with col_m2:
                imp_df = pd.DataFrame({
                    "Fitur": features,
                    "Importance": model.feature_importances_
                }).sort_values("Importance", ascending=True)

                fig_imp = px.bar(
                    imp_df,
                    x="Importance",
                    y="Fitur",
                    orientation="h",
                    title="Feature Importance (XGBoost)",
                    color="Importance",
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_imp, use_container_width=True)

            # ==================== SHAP ====================
            st.subheader("🔍 Interpretasi Model dengan SHAP")
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)

                st.write("**SHAP Summary Plot (Beeswarm)**")
                fig_shap, ax = plt.subplots(figsize=(10, 5))
                shap.summary_plot(shap_values, X_test, show=False)
                st.pyplot(fig_shap)
                plt.clf()

                st.write("**Rata-rata |SHAP Value|**")
                fig_shap2, ax2 = plt.subplots(figsize=(8, 4))
                shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
                st.pyplot(fig_shap2)
                plt.clf()

            except Exception as e:
                st.warning(f"Gagal menampilkan SHAP plot: {e}")

        except Exception as e:
            st.error(f"Gagal melatih model: {e}")

    # ==================== DOWNLOAD HASIL ====================
    st.markdown("---")
    st.subheader("📥 Download Hasil Analisis")

    st.write("Data yang akan diunduh adalah data **setelah filter** diterapkan.")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        excel_data = export_excel(df)
        st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_data,
            file_name=f"hasil_analisis_pangan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_d2:
        pdf_data = export_pdf(df, title="Laporan Analisis Stabilitas Pangan Lokal")
        st.download_button(
            label="📥 Download PDF",
            data=pdf_data,
            file_name=f"hasil_analisis_pangan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Preview data
    with st.expander("🔍 Lihat Data yang Akan Diunduh"):
        st.dataframe(df, use_container_width=True)