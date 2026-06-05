import { Bot, FileSearch, ScanText, TableProperties } from "lucide-react";

export default function Pipeline() {
  const steps = [
    {
      label: "OCR",
      detail: "Text layer detected",
      icon: ScanText,
      status: "Complete",
    },
    {
      label: "Regex Extraction",
      detail: "5 key fields matched",
      icon: FileSearch,
      status: "Complete",
    },
    {
      label: "Groq Analysis",
      detail: "Context validated",
      icon: Bot,
      status: "Review",
    },
    {
      label: "Structured Output",
      detail: "JSON normalized",
      icon: TableProperties,
      status: "Ready",
    },
  ];

  return (
    <section className="rounded-lg border border-[#E7E5DF] bg-white p-4 shadow-[0_16px_42px_rgba(37,37,37,0.045)] sm:p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-[#252525]">Processing Pipeline</h2>
        <span className="rounded-full bg-[#E9EDDF] px-3 py-1 text-xs font-semibold text-[#606C38]">
          Live run
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {steps.map((step) => (
          <div
            className="relative overflow-hidden rounded-lg border border-[#E7E5DF] bg-[#FBFAF7] p-4"
            key={step.label}
          >
            <div className="mb-5 flex items-center justify-between">
              <div className="grid h-10 w-10 place-items-center rounded-lg bg-white text-[#606C38] shadow-sm">
                <step.icon size={20} strokeWidth={1.9} />
              </div>
              <span className="text-xs font-semibold text-[#606C38]">
                {step.status}
              </span>
            </div>
            <p className="font-semibold text-[#252525]">{step.label}</p>
            <p className="mt-1 text-sm text-[#6B6B63]">{step.detail}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
