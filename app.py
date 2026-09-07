import pandas as pd
import streamlit as st
from backend.pipeline import run_pipeline


st.set_page_config(
    page_title="Gene Sequence QC & Profiler",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
.stApp {
    background: #F7F8FC;
    color: #1D2B44;
}

[data-testid="stSidebar"] {
    background: #171C36 !important;
}

[data-testid="stSidebar"] * {
    color: #F3F5FA !important;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #1D2B44;
    margin-bottom: 4px;
}

.main-subtitle {
    font-size: 17px;
    color: #52627A;
    margin-bottom: 25px;
}

.section-heading {
    font-size: 25px;
    font-weight: 750;
    color: #1D2B44;
    margin-top: 18px;
    margin-bottom: 12px;
}

.info-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #E3E7EF;
}

.metric-card {
    background: white;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #E3E7EF;
}

.reason-pass {
    background: #ECFDF3;
    border: 1px solid #B7E4C7;
    color: #176B3A;
    padding: 12px 14px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.reason-fail {
    background: #FFF1F2;
    border: 1px solid #F3B7BD;
    color: #9B1C31;
    padding: 12px 14px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.reason-neutral {
    background: #F5F7FA;
    border: 1px solid #DCE1EA;
    color: #52627A;
    padding: 12px 14px;
    border-radius: 10px;
}

.footer {
    margin-top: 45px;
    padding-top: 18px;
    border-top: 1px solid #DCE1EA;
    text-align: center;
    color: #65738A;
}

.small-note {
    color: #65738A;
    font-size: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)


if "result" not in st.session_state:
    st.session_state.result = None


with st.sidebar:
    st.markdown("## 🧬 Gene QC")

    page = st.radio(
        "Navigation",
        [
            "📤 Upload & Overview",
            "📊 QC Analysis",
            "📥 Export",
            "ℹ️ About Us",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(
        "Built for bioinformatics research, sequence quality control, "
        "and computational biology education."
    )


if page == "📤 Upload & Overview":

    st.markdown(
        '<div class="main-title">🧬 Automated Gene Sequence QC & Profiler</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Upload a multi-FASTA file to automatically clean, profile, "
        "quality-filter, and export gene sequence results."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">What this application does</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-card">
        <b>✔ Multi-FASTA processing</b> — reads sequences across multiple lines and records.<br><br>
        <b>✔ Sequence QC</b> — filters records by minimum length, ATG start codon,
        and valid DNA symbols.<br><br>
        <b>✔ Transparent QC reasons</b> — reports exactly why every sequence passed
        or failed each QC check.<br><br>
        <b>✔ Nucleotide profiling</b> — calculates length, GC%, and AT%.<br><br>
        <b>✔ RNA transcription</b> — converts DNA sequences into RNA transcripts.<br><br>
        <b>✔ Export-ready results</b> — downloads filtered CSV data, complete QC
        tables, summary reports, and a ZIP package.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">Upload your FASTA file</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Choose a multi-FASTA file",
        type=["fasta", "fa", "fna", "txt"],
        help="Upload DNA sequences in standard FASTA format.",
    )

    col1, col2 = st.columns(2)

    with col1:
        min_length = st.number_input(
            "Minimum sequence length (bp)",
            min_value=1,
            value=10,
            step=1,
        )

    with col2:
        require_start = st.checkbox(
            "Require ATG start codon",
            value=False,
        )

    if uploaded:
        st.success(f"Uploaded: **{uploaded.name}**")

        st.markdown(
            f"""
            <div class="small-note">
            QC settings: minimum length = <b>{min_length} bp</b> ·
            ATG requirement = <b>{"Enabled" if require_start else "Disabled"}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚀 Run Sequence QC Pipeline",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(
                "Processing FASTA records and generating QC reports..."
            ):
                try:
                    st.session_state.result = run_pipeline(
                        uploaded.getvalue(),
                        uploaded.name,
                        min_length=min_length,
                        require_start=require_start,
                    )

                    st.success("Pipeline completed successfully.")
                    st.info(
                        "Go to **📊 QC Analysis** to see the pass/fail reason "
                        "for every sequence."
                    )

                except Exception as exc:
                    st.error(f"Pipeline error: {exc}")

    st.markdown(
        """
        <div class="footer">
        🧬 <b>Powered by BioCode Innovators</b><br>
        Developed with precision by Abeera Iftikhar<br>
        Gene Sequence QC & Profiler designed for genomic sequence analysis,
        quality control, and modern bioinformatics education.<br><br>
        ✨ Bridging Biology, Data Science, and Computational Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )


elif page == "📊 QC Analysis":

    st.markdown(
        '<div class="main-title">📊 Sequence QC Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Review sequence quality, nucleotide composition, and the exact "
        "reason each record passed or failed QC."
        "</div>",
        unsafe_allow_html=True,
    )

    result = st.session_state.result

    if not result:
        st.info(
            "Upload a FASTA file on the Upload & Overview page "
            "and run the pipeline first."
        )

    else:
        m = result["summary"]

        cols = st.columns(4)

        metrics = [
            ("Total Sequences", m["total_sequences"]),
            ("Passed QC", m["passed_sequences"]),
            ("Rejected", m["failed_sequences"]),
            ("Pass Rate", f'{m["pass_rate"]:.1f}%'),
        ]

        for col, (label, value) in zip(cols, metrics):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f"<b>{label}</b><h2>{value}</h2>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Full transparent QC table
        st.markdown(
            '<div class="section-heading">🔎 Complete QC Results</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Every sequence is shown here. The pass and fail reason columns "
            "explain which QC checks were satisfied and which checks failed."
        )

        all_df = result["all_df"]

        st.dataframe(
            all_df[
                [
                    "Gene_Header",
                    "Length_bp",
                    "GC_Content_Pct",
                    "AT_Content_Pct",
                    "Has_ATG_Start",
                    "Has_Terminal_Stop",
                    "QC_Status",
                    "QC_Pass_Reason",
                    "QC_Fail_Reason",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Gene_Header": "Sequence / Gene",
                "Length_bp": "Length (bp)",
                "GC_Content_Pct": st.column_config.NumberColumn(
                    "GC (%)",
                    format="%.2f",
                ),
                "AT_Content_Pct": st.column_config.NumberColumn(
                    "AT (%)",
                    format="%.2f",
                ),
                "Has_ATG_Start": "ATG Start",
                "Has_Terminal_Stop": "Terminal Stop",
                "QC_Status": "QC Status",
                "QC_Pass_Reason": "✅ QC Pass Reason",
                "QC_Fail_Reason": "❌ QC Fail Reason",
            },
        )

        # Dedicated pass/fail reason sections
        st.markdown(
            '<div class="section-heading">✅ QC Pass Reasons</div>',
            unsafe_allow_html=True,
        )

        passed = result["passed_df"]

        if passed.empty:
            st.info("No sequences passed all QC criteria.")

        else:
            for _, row in passed.iterrows():
                st.markdown(
                    f"""
                    <div class="reason-pass">
                    <b>✅ {row["Gene_Header"]}</b><br>
                    {row["QC_Pass_Reason"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="section-heading">❌ QC Fail Reasons</div>',
            unsafe_allow_html=True,
        )

        rejected = result["failed_df"]

        if rejected.empty:
            st.success("No sequences were rejected by the selected QC criteria.")

        else:
            for _, row in rejected.iterrows():
                st.markdown(
                    f"""
                    <div class="reason-fail">
                    <b>❌ {row["Gene_Header"]}</b><br>
                    <b>Failed:</b> {row["QC_Fail_Reason"]}<br>
                    <span class="small-note">
                    Checks that passed: {row["QC_Pass_Reason"]}
                    </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Rejection summary
        st.markdown(
            '<div class="section-heading">📌 Rejection Reason Summary</div>',
            unsafe_allow_html=True,
        )

        rejection_summary = m.get("rejection_reasons", {})

        if rejection_summary:
            summary_df = pd.DataFrame(
                [
                    {"QC Fail Reason": reason, "Sequences": count}
                    for reason, count in rejection_summary.items()
                ]
            )
            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.markdown(
                '<div class="reason-neutral">No rejection reasons to report.</div>',
                unsafe_allow_html=True,
            )

        # Passed-sequence details
        st.markdown(
            '<div class="section-heading">Passed sequence details</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            passed,
            use_container_width=True,
            hide_index=True,
        )

        # GC profile
        st.markdown(
            '<div class="section-heading">GC content profile</div>',
            unsafe_allow_html=True,
        )

        if not passed.empty:
            chart_df = passed.set_index("Gene_Header")[
                ["GC_Content_Pct", "AT_Content_Pct"]
            ]
            st.bar_chart(chart_df)
        else:
            st.info("GC profile is unavailable because no sequence passed QC.")

        # Run summary
        st.markdown(
            '<div class="section-heading">Run summary</div>',
            unsafe_allow_html=True,
        )

        st.write(
            f'Average GC content of passed sequences: '
            f'**{m["average_gc"]:.2f}%**'
        )
        st.write(
            f'Minimum sequence length used: **{m["min_length"]} bp**'
        )
        st.write(
            f'ATG start codon requirement: '
            f'**{"Enabled" if m["require_start"] else "Disabled"}**'
        )


elif page == "📥 Export":

    st.markdown(
        '<div class="main-title">📥 Export Results</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Download the filtered data, complete QC results, text summary, "
        "or complete analysis package."
        "</div>",
        unsafe_allow_html=True,
    )

    result = st.session_state.result

    if not result:
        st.info("No completed analysis is available yet.")

    else:
        st.markdown(
            '<div class="section-heading">QC Downloads</div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            "⬇️ Download Passed Genes CSV",
            result["csv_bytes"],
            file_name="qc_passed_genes.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download Complete QC Results CSV",
            result["all_df"].to_csv(index=False).encode("utf-8"),
            file_name="complete_qc_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download Rejected Sequences CSV",
            result["failed_df"].to_csv(index=False).encode("utf-8"),
            file_name="rejected_sequences.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download Pipeline Summary",
            result["report_bytes"],
            file_name="pipeline_summary.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.download_button(
            "📦 Download Complete ZIP Package",
            result["zip_bytes"],
            file_name="gene_sequence_qc_results.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.success(
            "The complete QC table and rejected-sequence report now include "
            "the exact pass/fail reasons."
        )


elif page == "ℹ️ About Us":

    st.markdown(
        '<div class="main-title">ℹ️ About the Application</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### Automated Gene Sequence QC & Profiler Pipeline

        This application converts a command-line FASTA quality-control workflow
        into an interactive Streamlit dashboard.

        **Core workflow**

        1. Upload multi-FASTA sequences.
        2. Parse multi-line FASTA records.
        3. Calculate sequence length, GC%, and AT%.
        4. Transcribe DNA to RNA.
        5. Identify ATG start and terminal stop codons.
        6. Apply configurable QC filters.
        7. Explain why each sequence passed or failed.
        8. Generate downloadable QC reports and result files.

        **Designed for:** bioinformatics learners, genomics workflows,
        teaching demonstrations, and reproducible sequence-quality profiling.
        """
    )

    st.markdown(
        """
        <div class="footer">
        🧬 <b>Powered by BioCode Innovators</b><br>
        Developed with precision by Abeera Iftikhar
        </div>
        """,
        unsafe_allow_html=True,
    )
