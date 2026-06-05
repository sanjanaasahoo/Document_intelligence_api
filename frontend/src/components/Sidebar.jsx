import {
  BookOpen,
  LayoutDashboard,
  Upload,
  History,
  Settings,
  ShieldCheck,
} from "lucide-react";

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "upload", label: "Upload Documents", icon: Upload },
  { id: "history", label: "Processing History", icon: History },
  { id: "api-docs", label: "API Docs", icon: BookOpen },
  { id: "settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ activeView, compact = false, onNavigate }) {
  return (
    <aside
      className={`bg-[#343A40] text-white ${
        compact
          ? "flex items-center gap-4 overflow-x-auto px-4 py-3 lg:hidden"
          : "hidden min-h-screen w-72 shrink-0 flex-col p-6 lg:flex"
      }`}
    >
      <div className={`flex items-center gap-3 ${compact ? "shrink-0" : "mb-10"}`}>
        <div className="grid h-10 w-10 place-items-center rounded-lg bg-[#A3B18A] text-[#252525] shadow-sm">
          <ShieldCheck size={21} strokeWidth={2.2} />
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-normal">DocIntel</h1>
          {!compact && (
            <p className="text-xs font-medium text-white/50">Extraction OS</p>
          )}
        </div>
      </div>

      <nav className={`${compact ? "flex gap-2" : "space-y-1.5"}`}>
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              className={`flex items-center gap-3 rounded-lg px-3.5 py-3 text-left text-sm font-medium transition ${
                compact ? "shrink-0" : "w-full"
              } ${
                activeView === item.id
                  ? "bg-white text-[#252525] shadow-sm"
                  : "text-white/70 hover:bg-white/8 hover:text-white"
              }`}
              key={item.label}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              <Icon
                className={activeView === item.id ? "text-[#606C38]" : "text-white/55"}
                size={18}
                strokeWidth={2}
              />
              {item.label}
            </button>
          );
        })}
      </nav>

      {!compact && (
        <div className="mt-auto rounded-lg border border-white/10 bg-white/6 p-4">
          <p className="text-sm font-semibold">Backend endpoint</p>
          <p className="mt-1 text-xs leading-5 text-white/55">
            Uploads are sent to POST /parse-pdf through the local Vite API proxy.
          </p>
        </div>
      )}
    </aside>
  );
}
