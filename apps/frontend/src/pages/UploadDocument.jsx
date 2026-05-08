import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell, ChevronDown,
  User, Settings, BarChart2, FileText, Database, Activity,
  CloudUpload, FileType, X, CheckCircle, Loader, AlertCircle,
  Eye, Trash2, RefreshCw, FolderOpen, Sparkles, LayoutDashboard
} from "lucide-react";
  
const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload", active: true },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const DOCS = [
  {
    name: "Giải_tích_1_BK_2023.pdf",
    size: "12.4 MB",
    pages: 342,
    date: "05/05/2026",
    status: "done",
    problems: 1247,
    type: "pdf",
    color: "#A32D2D",
    bg: "#FCEBEB",
  },
  {
    name: "De_thi_NEU_HK2_2024.docx",
    size: "3.2 MB",
    pages: 48,
    date: "04/05/2026",
    status: "done",
    problems: 156,
    type: "docx",
    color: "#185FA5",
    bg: "#E6F1FB",
  },
  {
    name: "Calculus_VNU_Textbook.tex",
    size: "890 KB",
    pages: null,
    date: "07/05/2026",
    status: "processing",
    progress: 67,
    type: "tex",
    color: "#534AB7",
    bg: "#EEEDFE",
  },
  {
    name: "HUST_Giai_tich_2_2023.pdf",
    size: "18.7 MB",
    pages: 521,
    date: "06/05/2026",
    status: "done",
    problems: 2103,
    type: "pdf",
    color: "#A32D2D",
    bg: "#FCEBEB",
  },
  {
    name: "Chuoi_so_ham_so_UD.pdf",
    size: "5.1 MB",
    pages: 98,
    date: "07/05/2026",
    status: "processing",
    progress: 23,
    type: "pdf",
    color: "#A32D2D",
    bg: "#FCEBEB",
  },
  {
    name: "Stewart_Calculus_8e_EN.pdf",
    size: "47.3 MB",
    pages: 1368,
    date: "03/05/2026",
    status: "error",
    errorMsg: "File quá lớn — giới hạn 40 MB",
    type: "pdf",
    color: "#A32D2D",
    bg: "#FCEBEB",
  },
];

function FileTypeIcon({ type, color, bg }) {
  const labels = { pdf: "PDF", docx: "DOC", tex: "TEX", txt: "TXT" };
  return (
    <div style={{ background: bg, border: `1px solid ${color}30` }}
      className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0">
      <span style={{ color, fontSize: 9, fontWeight: 700, letterSpacing: 0.5 }}>
        {labels[type] || "FILE"}
      </span>
    </div>
  );
}

function StatusBadge({ status, progress, errorMsg }) {
  if (status === "done")
    return (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
        <CheckCircle size={10} /> Hoàn thành
      </span>
    );
  if (status === "processing")
    return (
      <div className="flex flex-col items-end gap-1">
        <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
          <Loader size={10} className="animate-spin" /> Đang xử lý {progress}%
        </span>
        <div className="w-24 h-1.5 rounded-full bg-slate-100 overflow-hidden">
          <div className="h-full rounded-full bg-amber-400 transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>
    );
  return (
    <span className="flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 border border-red-200 px-2.5 py-0.5 rounded-full">
      <AlertCircle size={10} /> Lỗi
    </span>
  );
}

export default function UploadDocument({ activePage = "upload", onNavigate = () => {} }) {
  const [dragging, setDragging] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");

  const filtered = DOCS.filter((d) =>
    filterStatus === "all" ? true : d.status === filterStatus
  );
  const totalProblems = DOCS.filter((d) => d.status === "done").reduce((a, b) => a + (b.problems || 0), 0);

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-white border-r border-slate-100 flex flex-col">
        <div className="px-4 py-4 border-b border-slate-100 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Hash size={15} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-800 leading-none">Calculus AI</p>
            <p className="text-[10px] text-slate-400 mt-0.5 tracking-widest uppercase">System v2.1</p>
          </div>
        </div>

        <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-2 mb-1.5">Chức năng</p>
          {NAV.map((item) => {
            const isActive = activePage === item.id;
            return (
            <div key={item.id} onClick={() => onNavigate(item.id)}
              className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${
                isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"
              }`}>
              <item.icon size={15}
                className={isActive ? "text-blue-600" : "text-slate-400"}
                strokeWidth={isActive ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>
                  {item.label}
                </p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && (
                <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>
              )}
            </div>
            );
          })}
        </nav>

        <div className="px-2 pb-3 border-t border-slate-100 pt-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer">
            <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold">N</div>
            <div>
              <p className="text-[11px] font-semibold text-slate-700">Nguyễn V. An</p>
              <p className="text-[10px] text-slate-400">Administrator</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-slate-100 px-6 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">Upload Document</h1>
            <p className="text-[11px] text-slate-400">Ingestion — bóc tách &amp; xử lý tài liệu toán học</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right mr-2">
              <p className="text-[10px] text-slate-400">Tổng bài tập đã ingested</p>
              <p className="text-sm font-bold text-blue-700">{totalProblems.toLocaleString()}</p>
            </div>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={15} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-5">
          {/* Upload zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={() => setDragging(false)}
            className={`border-2 border-dashed rounded-xl p-8 text-center mb-5 cursor-pointer transition-all ${
              dragging
                ? "border-blue-400 bg-blue-50"
                : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
            }`}>
            <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto mb-3">
              <CloudUpload size={28} className="text-blue-500" strokeWidth={1.5} />
            </div>
            <p className="text-sm font-semibold text-slate-700 mb-1">Kéo &amp; thả tài liệu vào đây</p>
            <p className="text-[12px] text-slate-400 mb-3">hoặc nhấn để chọn file từ máy tính của bạn</p>
            <div className="flex items-center justify-center gap-2 mb-4">
              {["PDF", "DOCX", "TEX", "TXT", "EPUB"].map((f) => (
                <span key={f} className="text-[10px] font-semibold px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-500">{f}</span>
              ))}
            </div>
            <button className="flex items-center gap-2 mx-auto px-5 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-lg hover:bg-blue-700 transition-colors">
              <FolderOpen size={14} /> Chọn file
            </button>
            <p className="text-[10px] text-slate-400 mt-2.5">Giới hạn 40 MB/file · Hỗ trợ LaTeX, Unicode, MathML</p>
          </div>

          {/* File list header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <span className="text-[12px] font-bold text-slate-700">Tài liệu đã upload</span>
              <span className="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{DOCS.length} files</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex rounded-lg overflow-hidden border border-slate-200">
                {[["all", "Tất cả"], ["done", "Hoàn thành"], ["processing", "Đang xử lý"], ["error", "Lỗi"]].map(([v, l]) => (
                  <button key={v} onClick={() => setFilterStatus(v)}
                    className={`text-[11px] px-2.5 py-1.5 transition-all ${
                      filterStatus === v ? "bg-blue-600 text-white font-semibold" : "bg-white text-slate-500 hover:bg-slate-50"
                    }`}>
                    {l}
                  </button>
                ))}
              </div>
              <button className="flex items-center gap-1.5 text-[11px] text-slate-500 border border-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-50">
                <RefreshCw size={11} /> Làm mới
              </button>
            </div>
          </div>

          {/* File rows */}
          <div className="space-y-2">
            {filtered.map((doc, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-xl p-3.5 flex items-center gap-3 hover:border-blue-100 hover:shadow-sm transition-all">
                <FileTypeIcon type={doc.type} color={doc.color} bg={doc.bg} />
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] font-semibold text-slate-700 truncate">{doc.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] text-slate-400">{doc.size}</span>
                    {doc.pages && <><span className="text-slate-200">·</span><span className="text-[10px] text-slate-400">{doc.pages} trang</span></>}
                    <span className="text-slate-200">·</span>
                    <span className="text-[10px] text-slate-400">{doc.date}</span>
                    {doc.status === "error" && (
                      <><span className="text-slate-200">·</span><span className="text-[10px] text-red-500">{doc.errorMsg}</span></>
                    )}
                  </div>
                </div>
                {doc.problems && (
                  <div className="text-right mr-2">
                    <p className="text-[13px] font-bold text-blue-700">{doc.problems.toLocaleString()}</p>
                    <p className="text-[10px] text-slate-400">bài tập</p>
                  </div>
                )}
                <StatusBadge status={doc.status} progress={doc.progress} errorMsg={doc.errorMsg} />
                <div className="flex items-center gap-1 ml-1">
                  <button className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
                    <Eye size={13} />
                  </button>
                  <button className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all">
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Summary bar */}
          <div className="mt-4 bg-white border border-slate-100 rounded-xl p-3.5 flex items-center gap-6">
            {[
              { label: "Tổng dung lượng", value: "87.7 MB", icon: Database },
              { label: "Bài tập đã index", value: totalProblems.toLocaleString(), icon: FileText },
              { label: "Đang xử lý", value: "2 files", icon: Loader },
              { label: "Lỗi cần xử lý", value: "1 file", icon: AlertCircle },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-2">
                <s.icon size={14} className="text-slate-400" />
                <div>
                  <p className="text-[10px] text-slate-400">{s.label}</p>
                  <p className="text-[12px] font-bold text-slate-700">{s.value}</p>
                </div>
                {i < 3 && <div className="w-px h-6 bg-slate-100 ml-4" />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
