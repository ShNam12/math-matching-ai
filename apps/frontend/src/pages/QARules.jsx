import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  CheckCircle, XCircle, AlertTriangle, RefreshCw,
  ChevronDown, Filter, Play, Download, Clock, Info,
  Shield, Code2, Copy, Layers, AlertCircle, Eye
} from "lucide-react";

const NAV = [
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", active: true, badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const RULES = [
  {
    id: "QA-001",
    title: "Kiểm tra cú pháp LaTeX",
    desc: "Phát hiện cú pháp LaTeX không hợp lệ: thiếu dấu đóng ngoặc, lệnh không xác định, môi trường math không đúng.",
    category: "Cú pháp",
    status: "error",
    passRate: 94.2,
    issues: 23,
    lastRun: "07/05/2026 14:30",
    icon: Code2,
    affectedIds: ["BK-2023-M1-012", "NEU-2024-C2-034", "VNU-2024-M2-007"],
  },
  {
    id: "QA-002",
    title: "Phân loại độ khó nhất quán",
    desc: "Phát hiện 17 bài gắn nhãn 'Dễ' nhưng cosine similarity với nhóm 'Khó' vượt ngưỡng 0.85 — có thể phân loại sai.",
    category: "Metadata",
    status: "warn",
    passRate: 98.7,
    issues: 17,
    lastRun: "07/05/2026 14:30",
    icon: Layers,
    affectedIds: ["HUST-2023-M3-045", "BK-2023-M1-089"],
  },
  {
    id: "QA-003",
    title: "Phát hiện bài tập trùng lặp",
    desc: "So sánh cosine similarity > 0.97 giữa tất cả các cặp bài tập. Không tìm thấy trùng lặp trong corpus hiện tại.",
    category: "Nội dung",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "07/05/2026 14:30",
    icon: Copy,
    affectedIds: [],
  },
  {
    id: "QA-004",
    title: "Metadata bắt buộc đầy đủ",
    desc: "Kiểm tra các trường bắt buộc: source, difficulty, topic, skill. Phát hiện 8 bài thiếu metadata — không thể index.",
    category: "Metadata",
    status: "error",
    passRate: 99.4,
    issues: 8,
    lastRun: "07/05/2026 14:30",
    icon: Info,
    affectedIds: ["NEU-2024-C2-103", "NEU-2024-C2-104"],
  },
  {
    id: "QA-005",
    title: "Embedding vector dimension",
    desc: "Xác minh tất cả vector có đúng chiều 1024-dim và chuẩn hóa L2 hợp lệ. Không phát hiện vector bất thường.",
    category: "Vector",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "07/05/2026 14:30",
    icon: Shield,
    affectedIds: [],
  },
  {
    id: "QA-006",
    title: "Lời giải tham chiếu",
    desc: "412 bài chưa có lời giải kèm theo. Khuyến nghị bổ sung trước khi export ra đề thi hoặc chia sẻ.",
    category: "Nội dung",
    status: "warn",
    passRate: 96.8,
    issues: 412,
    lastRun: "07/05/2026 14:30",
    icon: FileText,
    affectedIds: [],
  },
  {
    id: "QA-007",
    title: "Kiểm tra ngôn ngữ đề bài",
    desc: "Phát hiện 5 bài viết lẫn Tiếng Anh trong đề bài Tiếng Việt. Yêu cầu đồng nhất ngôn ngữ toàn corpus.",
    category: "Nội dung",
    status: "error",
    passRate: 99.96,
    issues: 5,
    lastRun: "07/05/2026 14:30",
    icon: AlertCircle,
    affectedIds: ["HUST-2023-M3-112", "HUST-2023-M3-113"],
  },
  {
    id: "QA-008",
    title: "Độ dài đề bài hợp lệ",
    desc: "Kiểm tra đề bài không quá ngắn (< 20 ký tự) hoặc quá dài (> 1000 ký tự). Tất cả bài tập đều trong ngưỡng.",
    category: "Cú pháp",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "07/05/2026 14:30",
    icon: CheckCircle,
    affectedIds: [],
  },
];

const statusCfg = {
  ok:   { label: "Đã qua", icon: CheckCircle,    bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", dot: "bg-emerald-500" },
  warn: { label: "Cảnh báo", icon: AlertTriangle, bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-200",   dot: "bg-amber-500" },
  error:{ label: "Lỗi",      icon: XCircle,       bg: "bg-red-50",     text: "text-red-700",     border: "border-red-200",     dot: "bg-red-500" },
};

const catColor = {
  "Cú pháp": "bg-blue-50 text-blue-700 border-blue-200",
  "Metadata": "bg-purple-50 text-purple-700 border-purple-200",
  "Nội dung": "bg-teal-50 text-teal-700 border-teal-200",
  "Vector": "bg-indigo-50 text-indigo-700 border-indigo-200",
};

export default function QARules({ activePage = "qa", onNavigate = () => {} }) {
  const [filterStatus, setFilterStatus] = useState("all");
  const [selected, setSelected] = useState(RULES[0]);
  const [running, setRunning] = useState(false);

  const filtered = RULES.filter((r) =>
    filterStatus === "all" ? true : r.status === filterStatus
  );

  const counts = {
    all: RULES.length,
    ok: RULES.filter((r) => r.status === "ok").length,
    warn: RULES.filter((r) => r.status === "warn").length,
    error: RULES.filter((r) => r.status === "error").length,
  };

  const handleRun = () => {
    setRunning(true);
    setTimeout(() => setRunning(false), 2000);
  };

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
            <div key={item.id} onClick={() => onNavigate(item.id)} className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"}`}>
              <item.icon size={15} className={isActive ? "text-blue-600" : "text-slate-400"} strokeWidth={isActive ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>{item.label}</p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>}
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
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">QA Rules — Kiểm định chất lượng</h1>
            <p className="text-[11px] text-slate-400">
              Lần quét gần nhất: 07/05/2026 14:30 ·&nbsp;
              <span className="text-red-600 font-semibold">{counts.error} lỗi</span> ·&nbsp;
              <span className="text-amber-600 font-semibold">{counts.warn} cảnh báo</span> ·&nbsp;
              <span className="text-emerald-600 font-semibold">{counts.ok} đã qua</span>
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleRun}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold rounded-lg transition-all ${running ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}`}>
              {running ? <RefreshCw size={12} className="animate-spin" /> : <Play size={12} />}
              {running ? "Đang quét..." : "Quét lại toàn bộ"}
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
              <Download size={12} /> Xuất báo cáo
            </button>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        {/* Summary bar */}
        <div className="bg-white border-b border-slate-100 px-5 py-2 flex items-center gap-4 flex-shrink-0">
          {[
            { key: "all", label: "Tất cả", count: counts.all, color: "text-slate-700" },
            { key: "error", label: "Lỗi", count: counts.error, color: "text-red-600" },
            { key: "warn", label: "Cảnh báo", count: counts.warn, color: "text-amber-600" },
            { key: "ok", label: "Đã qua", count: counts.ok, color: "text-emerald-600" },
          ].map((tab) => (
            <button key={tab.key} onClick={() => setFilterStatus(tab.key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold transition-all ${
                filterStatus === tab.key ? "bg-slate-100" : "hover:bg-slate-50"
              } ${tab.color}`}>
              <span>{tab.label}</span>
              <span className="bg-white border border-slate-200 px-1.5 py-0.5 rounded-full text-[10px]">{tab.count}</span>
            </button>
          ))}
          <div className="ml-auto flex items-center gap-1.5 text-[11px] text-slate-400">
            <Clock size={11} />
            Tự động quét mỗi 24 giờ
          </div>
        </div>

        <div className="flex-1 overflow-hidden flex">
          {/* Rule list */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {filtered.map((rule) => {
              const sc = statusCfg[rule.status];
              const isSelected = selected?.id === rule.id;
              return (
                <div key={rule.id} onClick={() => setSelected(rule)}
                  className={`bg-white border rounded-xl p-4 cursor-pointer transition-all ${
                    isSelected ? "border-blue-300 ring-1 ring-blue-200 shadow-sm" : "border-slate-100 hover:border-blue-100 hover:shadow-sm"
                  }`}>
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${sc.bg} border ${sc.border}`}>
                      <sc.icon size={15} className={sc.text} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold text-slate-400">{rule.id}</span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${catColor[rule.category]}`}>{rule.category}</span>
                        <span className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${sc.bg} ${sc.text} ${sc.border}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
                          {sc.label}
                        </span>
                      </div>
                      <p className="text-[12px] font-bold text-slate-700 mb-0.5">{rule.title}</p>
                      <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-1">{rule.desc}</p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                      <p className={`text-[14px] font-bold ${rule.status === "ok" ? "text-emerald-600" : rule.status === "warn" ? "text-amber-600" : "text-red-600"}`}>
                        {rule.passRate}%
                      </p>
                      <p className="text-[10px] text-slate-400">pass rate</p>
                      {rule.issues > 0 && (
                        <p className="text-[10px] text-slate-500 mt-0.5 font-semibold">{rule.issues} vấn đề</p>
                      )}
                    </div>
                  </div>
                  {/* Progress bar */}
                  <div className="mt-2.5 ml-11 w-full h-1 rounded-full bg-slate-100 overflow-hidden">
                    <div className={`h-full rounded-full transition-all ${rule.status === "ok" ? "bg-emerald-500" : rule.status === "warn" ? "bg-amber-400" : "bg-red-500"}`}
                      style={{ width: `${rule.passRate}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detail panel */}
          {selected && (
            <div className="w-72 flex-shrink-0 border-l border-slate-100 bg-white overflow-y-auto p-4 space-y-4">
              {(() => {
                const sc = statusCfg[selected.status];
                return (
                  <>
                    <div className={`rounded-xl p-4 ${sc.bg} border ${sc.border}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <sc.icon size={16} className={sc.text} />
                        <span className={`text-[11px] font-bold ${sc.text}`}>{sc.label.toUpperCase()}</span>
                      </div>
                      <p className="text-[13px] font-bold text-slate-800 mb-1">{selected.title}</p>
                      <p className="text-[11px] text-slate-600 leading-relaxed">{selected.desc}</p>
                    </div>

                    <div className="bg-slate-50 rounded-xl p-3 space-y-2">
                      <p className="text-[11px] font-bold text-slate-600 mb-2">Thông tin chi tiết</p>
                      {[
                        { label: "Rule ID", val: selected.id },
                        { label: "Danh mục", val: selected.category },
                        { label: "Pass rate", val: `${selected.passRate}%` },
                        { label: "Số vấn đề", val: selected.issues === 0 ? "Không có" : selected.issues },
                        { label: "Lần quét", val: selected.lastRun },
                      ].map((row) => (
                        <div key={row.label} className="flex justify-between items-center">
                          <span className="text-[11px] text-slate-500">{row.label}</span>
                          <span className="text-[11px] font-semibold text-slate-700">{row.val}</span>
                        </div>
                      ))}
                    </div>

                    {selected.affectedIds.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-slate-600 mb-2">Bài tập bị ảnh hưởng (mẫu)</p>
                        <div className="space-y-1">
                          {selected.affectedIds.map((id) => (
                            <div key={id} className="flex items-center gap-2 px-2.5 py-1.5 bg-red-50 border border-red-100 rounded-lg">
                              <AlertCircle size={11} className="text-red-500" />
                              <span className="text-[11px] font-mono text-red-700">{id}</span>
                              <button className="ml-auto">
                                <Eye size={11} className="text-red-400 hover:text-red-600" />
                              </button>
                            </div>
                          ))}
                          {selected.issues > selected.affectedIds.length && (
                            <p className="text-[10px] text-slate-400 text-center pt-1">
                              +{selected.issues - selected.affectedIds.length} bài khác...
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="space-y-2">
                      <button className="w-full flex items-center justify-center gap-2 px-3 py-2 text-[11px] font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all">
                        <Play size={12} /> Chạy rule này
                      </button>
                      {selected.issues > 0 && (
                        <button className="w-full flex items-center justify-center gap-2 px-3 py-2 text-[11px] font-semibold text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-all">
                          <Download size={12} /> Xuất danh sách lỗi
                        </button>
                      )}
                    </div>
                  </>
                );
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
