import {
  BadgeCheck,
  BookOpen,
  ChevronRight,
  Clock,
  Code2,
  FileText,
  History,
  Inbox,
  Loader2,
  Server,
  Settings,
  UploadCloud,
} from "lucide-react";
import { useEffect, useState } from "react";
import JsonViewer from "./components/JsonViewer";
import Pipeline from "./components/Pipeline";
import Sidebar from "./components/Sidebar";
import UploadCard from "./components/UploadCard";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const viewLabels = {
  dashboard: "Dashboard",
  upload: "Upload Documents",
  history: "Processing History",
  "api-docs": "API Docs",
  settings: "Settings",
};

function Header({ activeView }) {
  return (
    <header className="flex flex-col gap-4 border-b border-[#E7E5DF] bg-[#F7F6F2]/95 px-4 py-5 backdrop-blur sm:px-6 xl:flex-row xl:items-center xl:justify-between">
      <div>
        <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-[#606C38]">
          <span>Workspace</span>
          <ChevronRight size={15} />
          <span>{viewLabels[activeView] || "Dashboard"}</span>
        </div>
        <h1 className="mt-2 text-2xl font-semibold tracking-normal text-[#252525] sm:text-3xl">
          Document Intelligence Platform
        </h1>
        <p className="mt-2 text-sm text-[#6B6B63]">
          OCR + Regex + Groq Extraction
        </p>
      </div>

      <div className="inline-flex w-fit items-center gap-2 rounded-lg border border-[#E7E5DF] bg-white px-3 py-2 text-sm font-semibold text-[#252525] shadow-sm">
        <Server size={16} className="text-[#606C38]" />
        POST /parse-pdf
      </div>
    </header>
  );
}

function EmptyState({ icon: Icon = Inbox, title, message }) {
  return (
    <div className="flex min-h-44 flex-col items-center justify-center rounded-lg border border-dashed border-[#D8D5CB] bg-[#FBFAF7] p-6 text-center">
      <div className="grid h-11 w-11 place-items-center rounded-lg bg-[#E9EDDF] text-[#606C38]">
        <Icon size={21} />
      </div>
      <p className="mt-3 font-semibold text-[#252525]">{title}</p>
      <p className="mt-1 max-w-md text-sm leading-6 text-[#6B6B63]">{message}</p>
    </div>
  );
}

function DashboardPage({ history, latestResult, loading, onNavigate }) {
  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-[#E7E5DF] bg-white p-5 shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#606C38]">
              Dashboard
            </p>
            <h2 className="mt-2 text-xl font-semibold text-[#252525]">
              Ready for document extraction
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#6B6B63]">
              Upload a PDF to send it to the backend and review the latest
              structured response.
            </p>
          </div>
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[#606C38] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#4F5B2D]"
            onClick={() => onNavigate("upload")}
            type="button"
          >
            <UploadCloud size={17} />
            Upload PDF
          </button>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Files processed this session" value={history.length} />
        <MetricCard
          label="Latest fields found"
          value={latestResult?.total_fields_found ?? 0}
        />
        <MetricCard
          label="Current status"
          value={loading ? "Processing" : latestResult ? "Complete" : "Idle"}
        />
      </div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-lg border border-[#E7E5DF] bg-white p-4 shadow-[0_16px_42px_rgba(37,37,37,0.04)]">
      <p className="text-sm text-[#6B6B63]">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-[#252525]">{value}</p>
    </div>
  );
}

function DocumentList({ history, selectedFileName }) {
  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="border-b border-[#E7E5DF] p-4">
        <h2 className="font-semibold text-[#252525]">Uploaded document</h2>
        <p className="mt-1 text-sm text-[#6B6B63]">
          Only the latest extraction result is displayed.
        </p>
      </div>

      <div className="p-4">
        {selectedFileName ? (
          <div className="rounded-lg border border-[#A3B18A] bg-[#F3F5EA] p-3">
            <div className="flex items-start gap-3">
              <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-white text-[#606C38]">
                <FileText size={19} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-[#252525]">
                  {selectedFileName}
                </p>
                <p className="mt-1 text-xs text-[#6B6B63]">
                  {history[0]?.completedAt
                    ? `Completed ${history[0].completedAt}`
                    : "Waiting for backend response"}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <EmptyState
            icon={FileText}
            message="Choose a PDF from the upload area to begin."
            title="No document selected"
          />
        )}
      </div>
    </section>
  );
}

function PdfPreview({ fileName, previewUrl }) {
  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="border-b border-[#E7E5DF] p-4">
        <h2 className="font-semibold text-[#252525]">PDF preview viewer</h2>
        <p className="mt-1 truncate text-sm text-[#6B6B63]">
          {fileName || "No PDF selected"}
        </p>
      </div>

      <div className="bg-[#FBFAF7] p-4">
        {previewUrl ? (
          <iframe
            className="h-[560px] w-full rounded-lg border border-[#E7E5DF] bg-white"
            src={previewUrl}
            title="PDF preview"
          />
        ) : (
          <EmptyState
            icon={FileText}
            message="The selected PDF will appear here before and after processing."
            title="Preview is empty"
          />
        )}
      </div>
    </section>
  );
}

function getFirstValue(data, keys) {
  for (const key of keys) {
    if (data?.[key] !== undefined && data[key] !== null && data[key] !== "") {
      return Array.isArray(data[key]) ? data[key].join(", ") : String(data[key]);
    }
  }

  return "";
}

function ExtractedFields({ result }) {
  const data = result?.data || {};
  const fieldRows = [
    ["Vendor Name", getFirstValue(data, ["seller_name", "vendor_name", "supplier_name"])],
    ["Invoice Number", getFirstValue(data, ["invoice_number", "document_number"])],
    ["GSTIN", getFirstValue(data, ["seller_gstin", "gstin", "buyer_gstin"])],
    ["Amount", getFirstValue(data, ["total_amount", "grand_total", "invoice_total", "amount"])],
    ["Date", getFirstValue(data, ["invoice_date", "date", "document_date"])],
  ];
  const hasData = Boolean(result && Object.keys(data).length);

  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="border-b border-[#E7E5DF] p-4">
        <h2 className="font-semibold text-[#252525]">Extracted fields</h2>
        <p className="mt-1 text-sm text-[#6B6B63]">
          Values appear after the backend returns a successful response.
        </p>
      </div>

      <div className="space-y-3 p-4">
        {hasData ? (
          fieldRows.map(([label, value]) => (
            <div
              className="rounded-lg border border-[#E7E5DF] bg-[#FBFAF7] p-3"
              key={label}
            >
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#6B6B63]">
                {label}
              </p>
              <p className="mt-1 break-words text-sm font-semibold text-[#252525]">
                {value || "Not found"}
              </p>
            </div>
          ))
        ) : (
          <EmptyState
            icon={BadgeCheck}
            message="Upload a PDF and wait for the extraction response."
            title="No extracted fields yet"
          />
        )}
      </div>
    </section>
  );
}

function UploadPage({
  error,
  history,
  latestResult,
  loading,
  onUpload,
  previewUrl,
  selectedFileName,
}) {
  return (
    <div className="space-y-5">
      <UploadCard
        error={error}
        loading={loading}
        onUpload={onUpload}
        selectedFileName={selectedFileName}
      />

      {loading && (
        <div className="flex items-center gap-2 rounded-lg border border-[#E7E5DF] bg-white px-4 py-3 text-sm font-semibold text-[#606C38]">
          <Loader2 className="animate-spin" size={16} />
          Uploading PDF and waiting for the backend extraction response.
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-[300px_minmax(0,1fr)_340px]">
        <DocumentList history={history} selectedFileName={selectedFileName} />
        <PdfPreview fileName={selectedFileName} previewUrl={previewUrl} />
        <ExtractedFields result={latestResult} />
      </div>

      <JsonViewer data={latestResult} />
    </div>
  );
}

function HistoryPage({ history }) {
  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="border-b border-[#E7E5DF] p-4">
        <h2 className="text-lg font-semibold text-[#252525]">Processing History</h2>
        <p className="mt-1 text-sm text-[#6B6B63]">
          This session only shows PDFs uploaded through the current UI.
        </p>
      </div>

      <div className="p-4">
        {history.length ? (
          <div className="space-y-3">
            {history.map((item) => (
              <div
                className="flex flex-col gap-3 rounded-lg border border-[#E7E5DF] bg-[#FBFAF7] p-4 sm:flex-row sm:items-center sm:justify-between"
                key={item.id}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center rounded-lg bg-white text-[#606C38]">
                    <History size={18} />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-[#252525]">
                      {item.fileName}
                    </p>
                    <p className="mt-1 text-xs text-[#6B6B63]">
                      {item.completedAt} • {item.fieldsFound} fields found
                    </p>
                  </div>
                </div>
                <span className="w-fit rounded-full bg-[#E9EDDF] px-3 py-1 text-xs font-semibold text-[#606C38]">
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Clock}
            message="Completed uploads will appear here during this browser session."
            title="No processing history"
          />
        )}
      </div>
    </section>
  );
}

function ApiDocsPage() {
  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
      <div className="border-b border-[#E7E5DF] p-4">
        <h2 className="text-lg font-semibold text-[#252525]">API Docs</h2>
        <p className="mt-1 text-sm text-[#6B6B63]">
          Frontend uploads use the local Vite proxy and submit multipart form data.
        </p>
      </div>

      <div className="grid gap-4 p-4 lg:grid-cols-2">
        <div className="rounded-lg border border-[#E7E5DF] bg-[#FBFAF7] p-4">
          <div className="flex items-center gap-2 font-semibold text-[#252525]">
            <BookOpen size={18} className="text-[#606C38]" />
            Upload endpoint
          </div>
          <p className="mt-3 font-mono text-sm text-[#252525]">POST /api/parse-pdf</p>
          <p className="mt-2 text-sm leading-6 text-[#6B6B63]">
            Form field: <span className="font-mono text-[#252525]">file</span>
          </p>
        </div>

        <div className="rounded-lg border border-[#E7E5DF] bg-[#FBFAF7] p-4">
          <div className="flex items-center gap-2 font-semibold text-[#252525]">
            <Code2 size={18} className="text-[#606C38]" />
            Response shape
          </div>
          <p className="mt-3 text-sm leading-6 text-[#6B6B63]">
            The UI displays the exact backend response after a successful upload.
            The extracted values are read from the response&apos;s{" "}
            <span className="font-mono text-[#252525]">data</span> object.
          </p>
        </div>
      </div>
    </section>
  );
}

function SettingsPage() {
  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-[#E7E5DF] bg-white p-5 shadow-[0_16px_42px_rgba(37,37,37,0.045)]">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-[#E9EDDF] text-[#606C38]">
            <Settings size={19} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[#252525]">Settings</h2>
            <p className="mt-1 text-sm text-[#6B6B63]">
              Review how documents move through the extraction workflow.
            </p>
          </div>
        </div>
      </section>

      <Pipeline />
    </div>
  );
}

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [history, setHistory] = useState([]);
  const [latestResult, setLatestResult] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleUpload = async (file) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are accepted.");
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setActiveView("upload");
    setSelectedFileName(file.name);
    setPreviewUrl(URL.createObjectURL(file));
    setLatestResult(null);
    setError("");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/parse-pdf`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(payload?.detail || "PDF processing failed.");
      }

      setLatestResult(payload);
      setHistory((items) => [
        {
          id: `${file.name}-${Date.now()}`,
          completedAt: new Date().toLocaleString(),
          fieldsFound: payload?.total_fields_found ?? 0,
          fileName: file.name,
          status: payload?.status || "success",
        },
        ...items,
      ]);
    } catch (uploadError) {
      setLatestResult(null);
      setError(uploadError.message || "Unable to upload the PDF.");
    } finally {
      setLoading(false);
    }
  };

  let currentPage = (
    <DashboardPage
      history={history}
      latestResult={latestResult}
      loading={loading}
      onNavigate={setActiveView}
    />
  );

  if (activeView === "upload") {
    currentPage = (
      <UploadPage
        error={error}
        history={history}
        latestResult={latestResult}
        loading={loading}
        onUpload={handleUpload}
        previewUrl={previewUrl}
        selectedFileName={selectedFileName}
      />
    );
  }

  if (activeView === "history") {
    currentPage = <HistoryPage history={history} />;
  }

  if (activeView === "api-docs") {
    currentPage = <ApiDocsPage />;
  }

  if (activeView === "settings") {
    currentPage = <SettingsPage />;
  }

  return (
    <div className="min-h-screen bg-[#F7F6F2] text-[#252525]">
      <Sidebar activeView={activeView} compact onNavigate={setActiveView} />
      <div className="lg:flex">
        <Sidebar activeView={activeView} onNavigate={setActiveView} />

        <main className="min-w-0 flex-1">
          <Header activeView={activeView} />
          <div className="px-4 py-5 sm:px-6">{currentPage}</div>
        </main>
      </div>
    </div>
  );
}
