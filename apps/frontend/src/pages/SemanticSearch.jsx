import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles, Filter,
  TrendingUp, Eye, GitBranch, Zap, X, ChevronDown,
  Cpu, SlidersHorizontal, ArrowRight, Star, Copy, Share2
} from "lucide-react";

const NAV = [
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search", active: true },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const PROBLEMS = [
  {
    id: "BK-2023-M1-042",
    topic: "Tích phân",
    subtopic: "Tích phân từng phần",
    difficulty: "Khó",
    skill: "Tính toán",
    match: 97,
    latex: "\\int x^2 e^x \\, dx",
    statement: "Tính tích phân ∫ x²·eˣ dx bằng phương pháp tích phân từng phần (integration by parts). Viết đầy đủ các bước trung gian và kiểm tra lại kết quả bằng cách lấy đạo hàm của kết quả tìm được.",
    tags: ["Giải tích 1", "Đề thi HK2"],
    starred: true,
  },
  {
    id: "NEU-2024-C2-018",
    topic: "Đạo hàm",
    subtopic: "Đạo hàm hàm hợp",
    difficulty: "Vừa",
    skill: "Tính toán",
    match: 93,
    latex: "f(x) = \\ln(\\sin^2 x + 1)",
    statement: "Cho hàm số f(x) = ln(sin²(x) + 1). Tính f'(x) và xác định tất cả các điểm cực trị của hàm số trên đoạn [0, 2π]. Biện luận tính đơn điệu.",
    tags: ["Giải tích 1", "Cực trị"],
    starred: false,
  },
  {
    id: "VNU-2024-M2-067",
    topic: "Chuỗi số",
    subtopic: "Chuỗi lũy thừa",
    difficulty: "Khó",
    skill: "Chứng minh",
    match: 89,
    latex: "\\sum_{n=2}^{\\infty} \\frac{(-1)^n}{n \\ln n}",
    statement: "Chứng minh rằng chuỗi số Σ (−1)ⁿ/(n·ln n) hội tụ bằng tiêu chuẩn Leibniz. Tìm miền hội tụ của chuỗi lũy thừa tương ứng Σ xⁿ/(n·ln n).",
    tags: ["Giải tích 2", "Hội tụ"],
    starred: false,
  },
  {
    id: "HUST-2023-M3-091",
    topic: "Tích phân",
    subtopic: "Tích phân bội đôi",
    difficulty: "Khó",
    skill: "Tính toán",
    match: 85,
    latex: "\\iint_D x \\cdot y \\, dA",
    statement: "Tính tích phân kép ∬_D x·y dA, trong đó D là miền giới hạn bởi parabol y = x² và đường thẳng y = x + 2. Đổi sang tọa độ cực nếu cần thiết để đơn giản hóa tính toán.",
    tags: ["Giải tích 2", "Tích phân bội"],
    starred: true,
  },
];

const diffConfig = {
  Dễ: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", bar: "bg-emerald-500" },
  Vừa: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", bar: "bg-amber-500" },
  Khó: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", bar: "bg-red-500" },
};

export default function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [diff, setDiff] = useState("");
  const [skill, setSkill] = useState("");
  const [expanded, setExpanded] = useState(null);
  const [starred, setStarred] = useState({ "BK-2023-M1-042": true, "HUST-2023-M3-091": true });

  const filtered = PROBLEMS.filter((p) => {
    return (
      (!topic || p.topic === topic) &&
      (!diff || p.difficulty === diff) &&
      (!skill || p.skill === skill) &&
      (!query || p.statement.toLowerCase().includes(query.toLowerCase()) || p.latex.includes(query))
    );
  });

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
          {NAV.map((item) => (
            <div key={item.id} className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${item.active ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"}`}>
              <item.icon size={15} className={item.active ? "text-blue-600" : "text-slate-400"} strokeWidth={item.active ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${item.active ? "text-blue-700" : "text-slate-500"}`}>{item.label}</p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>}
            </div>
          ))}
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
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex-shrink-0">
          <div className="flex items-center gap-3 mb-2.5">
            {/* Search bar */}
            <div className="flex-1 relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Nhập từ khóa ngữ nghĩa hoặc mã LaTeX  (vd: \int x^2 dx, tích phân từng phần)..."
                className="w-full pl-9 pr-9 py-2.5 text-[12px] font-mono bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400/30 focus:border-blue-400 text-slate-700 placeholder:text-slate-400 transition-all"
              />
              {query && (
                <button onClick={() => setQuery("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <X size={13} />
                </button>
              )}
            </div>
            <button className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-xl hover:bg-blue-700 transition-colors flex-shrink-0">
              <Sparkles size={13} /> Tìm kiếm AI
            </button>
            <div className="flex items-center gap-1.5 ml-2">
              <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
                <Bell size={14} />
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
              </button>
              <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
            </div>
          </div>

          {/* Filter row */}
          <div className="flex items-center gap-2">
            <Filter size={12} className="text-slate-400" />
            <span className="text-[11px] text-slate-400 font-medium">Lọc:</span>
            {[
              { label: "Chuyên đề", val: topic, setter: setTopic, opts: ["Đạo hàm", "Tích phân", "Chuỗi số", "Giới hạn", "Vi phân"] },
              { label: "Độ khó", val: diff, setter: setDiff, opts: ["Dễ", "Vừa", "Khó"] },
              { label: "Kỹ năng", val: skill, setter: setSkill, opts: ["Tính toán", "Chứng minh", "Ứng dụng"] },
            ].map((f) => (
              <div key={f.label} className="relative">
                <select value={f.val} onChange={(e) => f.setter(e.target.value)}
                  className={`appearance-none pl-2.5 pr-6 py-1.5 text-[11px] border rounded-lg cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-400 transition-all ${
                    f.val ? "bg-blue-50 border-blue-300 text-blue-700 font-semibold" : "bg-white border-slate-200 text-slate-500"
                  }`}
                  style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23888'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 6px center" }}>
                  <option value="">{f.label}</option>
                  {f.opts.map((o) => <option key={o}>{o}</option>)}
                </select>
              </div>
            ))}
            {(topic || diff || skill) && (
              <button onClick={() => { setTopic(""); setDiff(""); setSkill(""); }}
                className="flex items-center gap-1 text-[11px] text-red-500 hover:text-red-700 px-2 py-1.5 rounded-lg hover:bg-red-50 transition-all font-medium">
                <X size={10} /> Xóa lọc
              </button>
            )}
            <div className="ml-auto flex items-center gap-1.5 text-[11px] text-slate-400">
              <Cpu size={12} className="text-blue-500" />
              Model: <span className="font-semibold text-blue-600">BGE-M3</span>
              <span className="text-slate-300 mx-1">|</span>
              <span className="font-bold text-slate-700">{filtered.length}</span> kết quả
            </div>
          </div>
        </header>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-2 gap-3">
            {filtered.map((p) => {
              const dc = diffConfig[p.difficulty];
              const isExp = expanded === p.id;
              const isStarred = starred[p.id];
              const matchColor = p.match >= 95 ? "text-blue-700 bg-blue-50 border-blue-200" : p.match >= 88 ? "text-indigo-700 bg-indigo-50 border-indigo-200" : "text-slate-600 bg-slate-50 border-slate-200";

              return (
                <div key={p.id} className="bg-white border border-slate-100 rounded-xl overflow-hidden hover:border-blue-100 hover:shadow-md transition-all duration-200">
                  {/* Top bar */}
                  <div className="px-3.5 py-2 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-bold text-slate-400 tracking-wide">{p.id}</span>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${dc.bg} ${dc.text} ${dc.border}`}>{p.difficulty}</span>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white border border-slate-200 text-slate-500">{p.skill}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className={`flex items-center gap-1 px-2 py-0.5 rounded-lg border text-[11px] font-bold ${matchColor}`}>
                        <TrendingUp size={10} />
                        {p.match}%
                        <div className="ml-1 w-10 h-1 rounded-full bg-slate-200 overflow-hidden">
                          <div className="h-full rounded-full bg-current opacity-60" style={{ width: `${p.match}%` }} />
                        </div>
                      </div>
                      <button onClick={() => setStarred((s) => ({ ...s, [p.id]: !s[p.id] }))}
                        className={`p-1 rounded transition-all ${isStarred ? "text-amber-500" : "text-slate-300 hover:text-amber-400"}`}>
                        <Star size={12} fill={isStarred ? "currentColor" : "none"} />
                      </button>
                    </div>
                  </div>

                  {/* Body */}
                  <div className="p-3.5">
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">{p.topic}</span>
                      <ArrowRight size={9} className="text-slate-300" />
                      <span className="text-[10px] text-slate-400">{p.subtopic}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-2.5">
                      <div className="w-5 h-5 rounded bg-blue-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold" style={{ fontSize: 9 }}>∫</span>
                      </div>
                      <code className="text-[11px] font-mono text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100 flex-1 truncate">
                        {p.latex}
                      </code>
                      <button className="p-1 text-slate-400 hover:text-blue-600 transition-colors">
                        <Copy size={11} />
                      </button>
                    </div>
                    <p className={`text-[11px] text-slate-600 leading-relaxed ${!isExp ? "line-clamp-2" : ""}`}>
                      {p.statement}
                    </p>
                    <button onClick={() => setExpanded(isExp ? null : p.id)}
                      className="text-[10px] text-blue-500 hover:text-blue-700 font-medium mt-1 transition-colors">
                      {isExp ? "Thu gọn ▲" : "Đọc đầy đủ ▼"}
                    </button>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {p.tags.map((t) => (
                        <span key={t} className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-500 rounded font-medium">{t}</span>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="px-3.5 pb-3 flex items-center gap-1.5">
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold text-slate-600 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-all">
                      <Eye size={11} /> Xem lời giải
                    </button>
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-all">
                      <GitBranch size={11} /> Bài tương tự
                    </button>
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold text-purple-600 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-all ml-auto">
                      <Zap size={11} /> Sinh biến thể
                    </button>
                    <button className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-50 transition-all">
                      <Share2 size={11} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
              <Search size={32} className="mb-3 opacity-30" />
              <p className="text-sm font-medium">Không tìm thấy bài tập phù hợp</p>
              <p className="text-xs mt-1">Thử điều chỉnh bộ lọc hoặc từ khóa</p>
            </div>
          )}

          {filtered.length > 0 && (
            <div className="mt-4 text-center">
              <button className="text-[11px] text-blue-500 hover:text-blue-700 font-medium px-4 py-2 rounded-lg border border-blue-200 hover:bg-blue-50 transition-all">
                Tải thêm kết quả →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
