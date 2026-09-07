from io import BytesIO
import zipfile

import pandas as pd


STOP_CODONS = {"TAA", "TAG", "TGA"}
VALID_BASES = set("ACGTN")


def analyze_sequence(dna_seq: str):
    """Clean a DNA sequence and calculate reusable sequence metrics."""
    clean_seq = "".join(dna_seq.strip().upper().split())

    if not clean_seq:
        return None

    invalid = sorted(set(clean_seq) - VALID_BASES)
    length = len(clean_seq)

    g_count = clean_seq.count("G")
    c_count = clean_seq.count("C")
    a_count = clean_seq.count("A")
    t_count = clean_seq.count("T")

    gc_content = ((g_count + c_count) / length) * 100
    at_content = ((a_count + t_count) / length) * 100

    return {
        "length": length,
        "gc_content": gc_content,
        "at_content": at_content,
        "has_start": clean_seq.startswith("ATG"),
        "has_stop": clean_seq[-3:] in STOP_CODONS if length >= 3 else False,
        "rna": clean_seq.replace("T", "U"),
        "invalid_bases": invalid,
        "sequence": clean_seq,
    }


def parse_fasta(text: str):
    """Parse standard multi-line FASTA text into (header, sequence) records."""
    records = []
    current_header = None
    current_parts = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith(">"):
            if current_header is not None:
                records.append((current_header, "".join(current_parts)))

            current_header = line[1:].strip()
            current_parts = []

        else:
            if current_header is None:
                raise ValueError(
                    "FASTA sequence data was found before the first header."
                )

            current_parts.append(line)

    if current_header is not None:
        records.append((current_header, "".join(current_parts)))

    if not records:
        raise ValueError("No FASTA records were found.")

    return records


def run_pipeline(
    file_bytes: bytes,
    filename: str,
    min_length: int = 10,
    require_start: bool = False,
):
    """
    Run sequence QC and generate explicit pass/fail reasons.

    Each sequence receives:
      - QC_Status
      - QC_Pass_Reason
      - QC_Fail_Reason

    The output also contains separate passed/rejected dataframes and
    downloadable CSV, report, and ZIP files.
    """

    text = file_bytes.decode("utf-8-sig")
    records = parse_fasta(text)

    all_results = []
    failed = []

    for header, sequence in records:
        metrics = analyze_sequence(sequence)

        if metrics is None:
            row = {
                "Gene_Header": header,
                "Length_bp": 0,
                "GC_Content_Pct": 0.0,
                "AT_Content_Pct": 0.0,
                "Has_ATG_Start": False,
                "Has_Terminal_Stop": False,
                "RNA_Transcript": "",
                "QC_Status": "Rejected",
                "QC_Pass_Reason": "No sequence data available to evaluate.",
                "QC_Fail_Reason": "Empty sequence",
            }
            all_results.append(row)
            failed.append((header, "Empty sequence"))
            continue

        pass_checks = []
        fail_checks = []

        # Length QC
        if metrics["length"] >= min_length:
            pass_checks.append(f"Length ≥ {min_length} bp")
        else:
            fail_checks.append(
                f"Length below minimum threshold ({min_length} bp)"
            )

        # ATG QC
        if require_start:
            if metrics["has_start"]:
                pass_checks.append("ATG start codon present")
            else:
                fail_checks.append("Missing ATG start codon")
        else:
            pass_checks.append("ATG requirement disabled")

        # DNA symbol QC
        if metrics["invalid_bases"]:
            invalid_symbols = ", ".join(metrics["invalid_bases"])
            fail_checks.append(
                f"Contains invalid DNA symbols: {invalid_symbols}"
            )
        else:
            pass_checks.append("Valid DNA symbols")

        qc_status = "Passed" if not fail_checks else "Rejected"
        qc_pass_reason = "; ".join(pass_checks) if pass_checks else "—"
        qc_fail_reason = "; ".join(fail_checks) if fail_checks else "—"

        row = {
            "Gene_Header": header,
            "Length_bp": metrics["length"],
            "GC_Content_Pct": round(metrics["gc_content"], 2),
            "AT_Content_Pct": round(metrics["at_content"], 2),
            "Has_ATG_Start": metrics["has_start"],
            "Has_Terminal_Stop": metrics["has_stop"],
            "RNA_Transcript": metrics["rna"],
            "QC_Status": qc_status,
            "QC_Pass_Reason": qc_pass_reason,
            "QC_Fail_Reason": qc_fail_reason,
        }

        all_results.append(row)

        if qc_status == "Rejected":
            failed.append((header, qc_fail_reason))

    columns = [
        "Gene_Header",
        "Length_bp",
        "GC_Content_Pct",
        "AT_Content_Pct",
        "Has_ATG_Start",
        "Has_Terminal_Stop",
        "RNA_Transcript",
        "QC_Status",
        "QC_Pass_Reason",
        "QC_Fail_Reason",
    ]

    all_df = pd.DataFrame(all_results, columns=columns)

    passed_df = all_df[all_df["QC_Status"] == "Passed"].copy()
    failed_df = all_df[all_df["QC_Status"] == "Rejected"].copy()

    total = len(records)
    passed_count = len(passed_df)
    failed_count = len(failed_df)

    average_gc = (
        float(passed_df["GC_Content_Pct"].mean())
        if passed_count
        else 0.0
    )

    pass_rate = (passed_count / total * 100) if total else 0.0

    # Count individual failure reasons for a compact summary.
    rejection_summary = {}

    for reason in failed_df["QC_Fail_Reason"].tolist():
        for individual_reason in reason.split("; "):
            if individual_reason and individual_reason != "—":
                rejection_summary[individual_reason] = (
                    rejection_summary.get(individual_reason, 0) + 1
                )

    summary = {
        "filename": filename,
        "total_sequences": total,
        "passed_sequences": passed_count,
        "failed_sequences": failed_count,
        "pass_rate": pass_rate,
        "average_gc": average_gc,
        "min_length": min_length,
        "require_start": require_start,
        "rejection_reasons": rejection_summary,
    }

    csv_bytes = passed_df.to_csv(index=False).encode("utf-8")

    report_lines = [
        "=" * 64,
        "       GENE QC & PROFILER PIPELINE - RUN SUMMARY",
        "=" * 64,
        "",
        f"Input FASTA file: {filename}",
        f"Total sequences analyzed: {total}",
        f"Total sequences passed QC: {passed_count}",
        f"Total sequences rejected: {failed_count}",
        f"Pass rate: {pass_rate:.2f}%",
        f"Average GC content of passed genes: {average_gc:.2f}%",
        f"Minimum sequence length: {min_length} bp",
        f"ATG start codon required: {'Yes' if require_start else 'No'}",
        "",
        "Sequence-level QC results:",
    ]

    for _, row in all_df.iterrows():
        report_lines.extend(
            [
                "",
                f"Sequence: {row['Gene_Header']}",
                f"Status: {row['QC_Status']}",
                f"Pass reason: {row['QC_Pass_Reason']}",
                f"Fail reason: {row['QC_Fail_Reason']}",
            ]
        )

    report_lines.extend(["", "Rejection reason summary:"])

    if rejection_summary:
        for reason, count in rejection_summary.items():
            report_lines.append(f"- {reason}: {count}")
    else:
        report_lines.append("- None")

    report_bytes = ("\n".join(report_lines) + "\n").encode("utf-8")

    all_csv_bytes = all_df.to_csv(index=False).encode("utf-8")
    rejected_csv_bytes = failed_df.to_csv(index=False).encode("utf-8")

    zip_buffer = BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        zf.writestr("qc_passed_genes.csv", csv_bytes)
        zf.writestr("pipeline_summary.txt", report_bytes)
        zf.writestr("complete_qc_results.csv", all_csv_bytes)
        zf.writestr("rejected_sequences.csv", rejected_csv_bytes)

    return {
        "summary": summary,
        "all_df": all_df,
        "passed_df": passed_df,
        "failed_df": failed_df,
        "failed": failed,
        "csv_bytes": csv_bytes,
        "report_bytes": report_bytes,
        "zip_bytes": zip_buffer.getvalue(),
    }
