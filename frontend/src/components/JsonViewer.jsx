import { Check, Clipboard, Download } from "lucide-react";
import { useMemo, useState } from "react";

export default function JsonViewer({ data }) {
  const [copied, setCopied] = useState(false);
  const formattedJson = useMemo(
    () => (data ? JSON.stringify(data, null, 2) : ""),
    [data],
  );

  const copyJson = async () => {
    if (!formattedJson) return;
    await navigator.clipboard.writeText(formattedJson);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  };

  const downloadJson = () => {
    if (!formattedJson) return;
    const blob = new Blob([formattedJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${data?.data?.invoice_number || "document-extraction"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="flex flex-col gap-3 border-b border-[#E7E5DF] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[#252525]">JSON Output Viewer</h2>
          <p className="mt-1 text-sm text-[#6B6B63]">
            Normalized schema ready for API response or export.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-[#E7E5DF] bg-white px-3 text-sm font-semibold text-[#252525] transition hover:bg-[#F7F6F2] disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!data}
            onClick={copyJson}
            type="button"
          >
            {copied ? <Check size={16} /> : <Clipboard size={16} />}
            {copied ? "Copied" : "Copy JSON"}
          </button>
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[#606C38] px-3 text-sm font-semibold text-white transition hover:bg-[#4F5B2D] disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!data}
            onClick={downloadJson}
            type="button"
          >
            <Download size={16} />
            Download JSON
          </button>
        </div>
      </div>

      <div className="overflow-x-auto bg-[#252525] p-4">
        {data ? (
          <pre className="max-h-80 text-sm leading-6 text-[#EDEBE4]">
            {formattedJson}
          </pre>
        ) : (
          <div className="flex min-h-44 items-center justify-center text-center text-sm text-[#C9C4B8]">
            Upload a PDF to view the backend extraction response.
          </div>
        )}
      </div>
    </section>
  );
}
