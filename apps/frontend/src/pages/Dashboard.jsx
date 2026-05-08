import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles, LayoutDashboard,
  Zap, Clock, Activity, AlertTriangle, Loader,
  HelpCircle, ChevronRight, TrendingUp, ArrowUpRight,
  Star, Bookmark, Filter
} from "lucide-react";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: BookOpen, label: "Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const HEALTH = [
  {
    label: "Tổng bài tập",
    value: "12,847",
    delta: "↑ 234 tuần này",
    trend: "up",
    icon: FileText,
    iconBg: "#E6F1FB",
    iconColor: "#185FA5",
  },
  {
    label: "Đang xử lý",
    value: "2 files",
    delta: "67% · 23% tiến độ",
    trend: "warn",
    icon: Loader,
    iconBg: "#FAEEDA",
    iconColor: "#854F0B",
  },
  {
    label: "Lỗi QA cần xử lý",
    value: "36",
    delta: "3 rule bị lỗi",
    trend: "error",
    icon: AlertTriangle,
    iconBg: "#FCEBEB",
    iconColor: "#A32D2D",
  },
  {
    label: "Truy vấn hôm nay",
    value: "3,891",
    delta: "↑ 18% vs hôm qua",
    trend: "up",
    icon: Activity,
    iconBg: "#EAF3DE",
    iconColor: "#3B6D11",
  },
];

const RECENT_PROBLEMS = [
  {
    symbol: "∫",
    latex: "\\int x^2 e^x \\, dx",
    statement: "Tính tích phân bất định bằng phương pháp tích phân từng phần, viết đầy đủ các bước...",
    topic: "Tích phân", topicColor: "blue",
    diff: "Khó", diffColor: "red",
    source: "BK-2023-M1",
    match: 97,
  },
  {
    symbol: "∂",
    latex: "f(x) = \\ln(\\sin^2 x + 1)",
    statement: "Tính f'(x) và xác định các điểm cực trị của hàm số trên đoạn [0, 2π]...",
    topic: "Đạo hàm", topicColor: "blue",
    diff: "Vừa", diffColor: "amber",
    source: "NEU-2024-C2",
    match: 93,
  },
  {
    symbol: "Σ",
    latex: "\\sum_{n=2}^{\\infty} \\frac{(-1)^n}{n\\ln n}",
    statement: "Chứng minh chuỗi hội tụ bằng tiêu chuẩn Leibniz, tìm miền hội tụ chuỗi lũy thừa...",
    topic: "Chuỗi số", topicColor: "blue",
    diff: "Khó", diffColor: "red",
    source: "VNU-2024-M2",
    match: 89,
  },
  {
    symbol: "∬",
    latex: "\\iint_D x \\cdot y \\, dA",
    statement: "Tính tích phân kép trên miền giới hạn bởi parabol y = x² và đường thẳng y = x + 2...",
    topic: "Tích phân bội", topicColor: "blue",
    diff: "Khó", diffColor: "red",
    source: "HUST-2023-M3",
    match: 85,
  },
  {
    symbol: "lim",
    latex: "\\lim_{x\\to 0} \\frac{\\sin x - x}{x^3}",
    statement: "Tính giới hạn bằng khai triển Taylor hoặc quy tắc L'Hôpital, so sánh kết quả...",
    topic: "Giới hạn", topicColor: "blue",
    diff: "Vừa", diffColor: "amber",
    source: "BK-2023-M1",
    match: 81,
  },
];

const ACTIVITIES = [
  { dot: "amber", action: "Upload", detail: "Calculus_VNU.tex đang xử lý 67%", time: "14:32" },
  { dot: "green", action: "Gen", detail: "3 biến thể ∫x²eˣdx đã tạo xong", time: "13:17" },
  { dot: "red", action: "QA Scan", detail: "36 vấn đề cần xử lý", time: "11:45" },
  { dot: "green", action: "Upload", detail: "HUST_GT2.pdf hoàn thành, 2,103 bài", time: "09:22" },
];

const TOPICS = [
  { name: "Tích phân", count: "4,891", color: "#185FA5" },
  { name: "Đạo hàm", count: "3,456", color: "#534AB7" },
  { name: "Chuỗi số", count: "3,260", color: "#0F6E56" },
  { name: "Giới hạn", count: "1,240", color: "#854F0B" },
];

const QUICK_ACTIONS = [
  { icon: Upload, label: "Upload tài liệu", color: "text-blue-600 bg-blue-50 border-blue-200" },
  { icon: Sparkles, label: "Sinh biến thể", color: "text-purple-600 bg-purple-50 border-purple-200" },
  { icon: CheckSquare, label: "Kiểm tra QA", color: "text-red-600 bg-red-50 border-red-200" },
  { icon: BarChart2, label: "Xem analytics", color: "text-teal-600 bg-teal-50 border-teal-200" },
];

const RECENT_QUERIES = [
  "\\int x^2 e^x dx",
  "chuỗi hội tụ Leibniz",
  "đạo hàm hàm hợp cực trị",
  "\\iint_D dA tọa độ cực",
];

const diffStyle = {
  red: "bg-red-50 text-red-800 border-red-200",
  amber: "bg-amber-50 text-amber-800 border-amber-200",
};

const dotColor = {
  green: "bg-emerald-500",
  amber: "bg-amber-400",
  red: "bg-red-500",
};

export default function MainDashboard({ activePage = "dashboard", onNavigate = () => {} }) {
  const [query, setQuery] = useState("");
  const [starred, setStarred] = useState({});

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="w-52 flex-shrink-0 bg-white border-r border-slate-100 flex flex-col">
        <div className="px-4 py-4 border-b border-slate-100 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Hash size={15} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-800 leading-none">Calculus AI</p>
            <p className="text-[10px] text-slate-400 mt-0.5 tracking-widest uppercase">System v2.1</p>
          </div>
        </div>

        <nav className="flex-1 px-2 py-3 overflow-y-auto space-y-0.5">
          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-2 mb-1.5">Chức năng</p>
          {NAV.map((item) => {
  const isActive = activePage === item.id;

  return (
    <div
      key={item.id}
      onClick={() => onNavigate(item.id)}
      className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"}`}
    >
      <item.icon
        size={14}
        className={isActive ? "text-blue-600" : "text-slate-400"}
        strokeWidth={isActive ? 2.5 : 1.8}
      />

      <div className="flex-1 min-w-0">
        <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>
          {item.label}
        </p>
        <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
      </div>

      {item.badge && (
        <span className="text-[9px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">
          {item.badge}
        </span>
      )}
    </div>
  );
})}

        </nav>

        <div className="px-2 pb-3 border-t border-slate-100 pt-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer">
            <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">N</div>
            <div>
              <p className="text-[11px] font-semibold text-slate-700">Nguyễn V. An</p>
              <p className="text-[10px] text-slate-400">Administrator</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="bg-white border-b border-slate-100 px-5 py-2.5 flex items-center justify-between flex-shrink-0">
          <div>
            <p className="text-sm font-bold text-slate-800">Dashboard</p>
            <p className="text-[11px] text-slate-400">Chào buổi sáng, An — corpus đang hoạt động ổn định</p>
          </div>
          <div className="flex items-center gap-1.5">
            <button className="relative w-7 h-7 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-slate-100">
              <Bell size={13} />
              <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-red-500 border border-white" />
            </button>
            <button className="w-7 h-7 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-slate-100">
              <HelpCircle size={13} />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold cursor-pointer ml-0.5">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">

          {/* ① Hero Search */}
          <div className="bg-white border border-slate-100 rounded-xl p-4">
            <div className="flex items-end justify-between mb-2.5">
              <div>
                <p className="text-[13px] font-bold text-slate-800">Tìm kiếm bài tập</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Nhập từ khóa ngữ nghĩa hoặc công thức LaTeX để tìm trong corpus</p>
              </div>
            </div>

            {/* Search bar */}
            <div className="flex gap-2 mb-2.5">
              <div className="flex-1 relative">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="\int x^2 dx  —  tích phân, đạo hàm, chuỗi số, giới hạn..."
                  className="w-full pl-8 pr-3 py-2.5 text-[12px] font-mono bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400/25 focus:border-blue-400 text-slate-700 placeholder:text-slate-400 transition-all"
                />
              </div>
              <button className="flex items-center gap-1.5 px-4 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-lg hover:bg-blue-700 transition-colors flex-shrink-0">
                <Sparkles size={12} /> Tìm kiếm AI
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 mb-2.5">
              <Filter size={11} className="text-slate-400 flex-shrink-0" />
              {[
                { label: "Chuyên đề", opts: ["Đạo hàm", "Tích phân", "Chuỗi số", "Giới hạn"] },
                { label: "Độ khó", opts: ["Dễ", "Vừa", "Khó"] },
                { label: "Kỹ năng", opts: ["Tính toán", "Chứng minh"] },
                { label: "Nguồn tài liệu", opts: ["BK 2023", "VNU 2024", "NEU 2024"] },
              ].map((f) => (
                <select key={f.label}
                  className="appearance-none pl-2.5 pr-6 py-1.5 text-[11px] bg-white border border-slate-200 rounded-lg text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400 cursor-pointer"
                  style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='9' height='5'%3E%3Cpath d='M0 0l4.5 5L9 0z' fill='%23888'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 6px center" }}>
                  <option>{f.label}</option>
                  {f.opts.map((o) => <option key={o}>{o}</option>)}
                </select>
              ))}
            </div>

            {/* Recent queries */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] text-slate-400 flex-shrink-0">Gần đây:</span>
              {RECENT_QUERIES.map((q) => (
                <button key={q} onClick={() => setQuery(q)}
                  className="text-[10px] font-mono text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-full hover:bg-blue-100 transition-all whitespace-nowrap">
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* ② Corpus Health */}
          <div className="grid grid-cols-4 gap-2.5">
            {HEALTH.map((h, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-xl p-3 flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: h.iconBg }}>
                  <h.icon size={16} style={{ color: h.iconColor }} strokeWidth={1.8} />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] text-slate-400 truncate">{h.label}</p>
                  <p className={`text-[15px] font-bold leading-tight ${h.trend === "error" ? "text-red-700" : "text-slate-800"}`}>{h.value}</p>
                  <p className={`text-[10px] mt-0.5 ${h.trend === "up" ? "text-emerald-600" : h.trend === "error" ? "text-red-600" : "text-amber-600"}`}>
                    {h.delta}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* ③ Bottom 2-col */}
          <div className="grid gap-2.5" style={{ gridTemplateColumns: "1fr 256px" }}>

            {/* Left: Recent problems */}
            <div className="bg-white border border-slate-100 rounded-xl overflow-hidden">
              <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock size={13} className="text-blue-600" />
                  <span className="text-[12px] font-bold text-slate-700">Bài tập đã xem gần đây</span>
                </div>
                <button className="text-[11px] text-blue-500 hover:text-blue-700 font-medium flex items-center gap-0.5">
                  Xem tất cả <ChevronRight size={11} />
                </button>
              </div>

              <div className="divide-y divide-slate-50">
                {RECENT_PROBLEMS.map((p, i) => (
                  <div key={i} className="flex items-start gap-3 px-4 py-2.5 hover:bg-slate-50 cursor-pointer transition-all group">
                    <div className="w-7 h-7 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-[11px] font-bold text-blue-700">{p.symbol}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <code className="text-[11px] font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 inline-block mb-1.5 max-w-full truncate">{p.latex}</code>
                      <p className="text-[11px] text-slate-500 leading-snug truncate">{p.statement}</p>
                      <div className="flex items-center gap-1.5 mt-1.5">
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded border bg-blue-50 text-blue-800 border-blue-200">{p.topic}</span>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${diffStyle[p.diffColor]}`}>{p.diff}</span>
                        <span className="text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{p.source}</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1 flex-shrink-0">
                      <div className="flex items-center gap-1">
                        <TrendingUp size={10} className="text-blue-500" />
                        <span className="text-[11px] font-bold text-blue-700">{p.match}%</span>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); setStarred((s) => ({ ...s, [i]: !s[i] })); }}
                        className={`transition-all ${starred[i] ? "text-amber-400" : "text-slate-200 group-hover:text-slate-300"}`}>
                        <Star size={12} fill={starred[i] ? "currentColor" : "none"} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right col */}
            <div className="flex flex-col gap-2.5">

              {/* Quick actions */}
              <div className="bg-white border border-slate-100 rounded-xl overflow-hidden">
                <div className="px-3.5 py-2.5 border-b border-slate-100 flex items-center gap-2">
                  <Zap size={13} className="text-blue-600" />
                  <span className="text-[12px] font-bold text-slate-700">Thao tác nhanh</span>
                </div>
                <div className="p-2.5 grid grid-cols-2 gap-2">
                  {QUICK_ACTIONS.map((a, i) => (
                    <button key={i} className={`flex flex-col items-center gap-1.5 py-3 rounded-lg border text-[10px] font-semibold transition-all hover:scale-[1.02] ${a.color}`}>
                      <a.icon size={16} />
                      {a.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Topic shortcuts */}
              <div className="bg-white border border-slate-100 rounded-xl overflow-hidden">
                <div className="px-3.5 py-2.5 border-b border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BookOpen size={13} className="text-blue-600" />
                    <span className="text-[12px] font-bold text-slate-700">Chủ đề phổ biến</span>
                  </div>
                  <button className="text-[10px] text-blue-500 font-medium">Taxonomy →</button>
                </div>
                <div className="px-3 py-2 space-y-0.5">
                  {TOPICS.map((t, i) => (
                    <div key={i} className="flex items-center gap-2.5 px-1.5 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer transition-all">
                      <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: t.color }} />
                      <span className="text-[11px] text-slate-600 flex-1">{t.name}</span>
                      <span className="text-[10px] text-slate-400 font-medium">{t.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Activity feed */}
              <div className="bg-white border border-slate-100 rounded-xl overflow-hidden flex-1">
                <div className="px-3.5 py-2.5 border-b border-slate-100 flex items-center gap-2">
                  <Activity size={13} className="text-blue-600" />
                  <span className="text-[12px] font-bold text-slate-700">Hoạt động gần đây</span>
                </div>
                <div className="divide-y divide-slate-50">
                  {ACTIVITIES.map((a, i) => (
                    <div key={i} className="flex items-start gap-2.5 px-3.5 py-2.5">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${dotColor[a.dot]}`} />
                      <div className="flex-1 min-w-0">
                        <span className="text-[11px] font-semibold text-slate-700">{a.action}</span>
                        <span className="text-[11px] text-slate-400"> — {a.detail}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 flex-shrink-0">{a.time}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
