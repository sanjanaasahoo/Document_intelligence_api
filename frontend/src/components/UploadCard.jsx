import { FileUp, FolderOpen, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

export default function UploadCard({ error, onUpload, loading, selectedFileName }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      onUpload(file);
      e.target.value = "";
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white p-4 shadow-[0_18px_50px_rgba(37,37,37,0.06)] sm:p-5">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#606C38]">
            Upload
          </p>
          <h2 className="mt-1 text-xl font-semibold text-[#252525]">
            Add documents for extraction
          </h2>
        </div>
        <p className="text-sm text-[#6B6B63]">PDF, scanned invoice, receipt, form</p>
      </div>

      <div
        className={`flex min-h-56 flex-col items-center justify-center rounded-lg border border-dashed p-6 text-center transition sm:p-8 ${
          isDragging
            ? "border-[#606C38] bg-[#F7F6F2]"
            : "border-[#A3B18A] bg-[#FBFAF7]"
        }`}
        onDragLeave={() => setIsDragging(false)}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDrop={handleDrop}
      >
        <div className="mb-4 grid h-14 w-14 place-items-center rounded-lg bg-[#E9EDDF] text-[#606C38]">
          <UploadCloud size={28} strokeWidth={1.8} />
        </div>

        <h3 className="text-base font-semibold text-[#252525]">
          Drag and drop PDF documents here
        </h3>
        <p className="mt-2 max-w-xl text-sm leading-6 text-[#6B6B63]">
          Upload invoices, contracts, receipts, reports, and forms for OCR,
          Regex extraction, and Groq analysis.
        </p>

        <div className="mt-5 flex flex-col items-center gap-3 sm:flex-row">
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[#606C38] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#4F5B2D] disabled:cursor-not-allowed disabled:opacity-65"
            disabled={loading}
            onClick={() => inputRef.current?.click()}
            type="button"
          >
            <FolderOpen size={17} />
            Browse files
          </button>
          <span className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-[#E7E5DF] bg-white px-3 text-sm text-[#6B6B63]">
            <FileUp size={16} className="text-[#606C38]" />
            {selectedFileName || "No file selected"}
          </span>
        </div>

        <input
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleChange}
          ref={inputRef}
          type="file"
        />

        {loading && (
          <div className="mt-5 h-1.5 w-full max-w-sm overflow-hidden rounded-full bg-[#E7E5DF]">
            <div className="h-full w-2/3 animate-pulse rounded-full bg-[#606C38]" />
          </div>
        )}

        {error && (
          <p className="mt-4 max-w-xl rounded-lg border border-[#F0D0C7] bg-[#FFF6F3] px-3 py-2 text-sm text-[#8A2F1B]">
            {error}
          </p>
        )}
      </div>
    </section>
  );
}
