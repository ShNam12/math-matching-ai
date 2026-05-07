import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  ArrowLeft, Copy, Share2, Star, Eye, GitBranch,
  Zap, ChevronRight, CheckCircle, BookMarked,
  TrendingUp, Tag, Clock, User, Printer, Download
} from "lucide-react";

const NAV = [
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail", active: true },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const PROBLEM = {
  id: "BK-2023-M1-042",
  topic: "Tích phân",
  subtopic: "Tích phân từng phần",
  chapter: "Chương 3",
  difficulty: "Khó",
  skill: "Tính toán",
  source: "Giải tích 1 — BK 2023",
  addedBy: "Nguyễn V. An",
  addedDate: "05/05/2026",
  latex: "\\int x^2 e^x \\, dx",
  statement:
    "Tính tích phân bất định ∫ x²·eˣ dx bằng phương pháp tích phân từng phần (integration by parts). Yêu cầu viết đầy đủ các bước trung gian, chỉ rõ việc chọn u và dv ở mỗi lần áp dụng công thức, và kiểm tra lại kết quả bằng cách lấy đạo hàm của biểu thức tìm được.",
  tags: ["Giải tích 1", "Đề thi HK2", "Integration by parts"],
  similarCount: 18,
  variantCount: 5,
};

const STEPS = [
  {
    num: 1,
    title: "Áp dụng tích phân từng phần lần 1",
    content: "Đặt u = x², dv = eˣ dx. Suy ra du = 2x dx và v = eˣ. Áp dụng công thức ∫u dv = uv − ∫v du:",
    latex: "\\int x^2 e^x \\, dx = x^2 e^x - \\int 2x \\cdot e^x \\, dx",
  },
  {
    num: 2,
    title: "Áp dụng tích phân từng phần lần 2",
    content: "Tiếp tục xử lý ∫ 2xeˣ dx. Đặt u = 2x, dv = eˣ dx → du = 2 dx, v = eˣ:",
    latex: "\\int 2x e^x \\, dx = 2x e^x - \\int 2e^x \\, dx = 2xe^x - 2e^x",
  },
  {
    num: 3,
    title: "Ghép kết quả & rút gọn",
    content: "Thay kết quả bước 2 vào bước 1, nhóm và rút gọn các hạng tử:",
    latex: "\\int x^2 e^x \\, dx = x^2 e^x - 2xe^x + 2e^x + C = e^x(x^2 - 2x + 2) + C",
  },
  {
    num: 4,
    title: "Kiểm tra bằng đạo hàm",
    content: "Lấy đạo hàm của F(x) = eˣ(x²−2x+2) theo quy tắc tích số:",
    latex: "F'(x) = e^x(x^2 - 2x + 2) + e^x(2x - 2) = e^x \\cdot x^2 = x^2 e^x \\checkmark",
  },
];

const SIMILAR = [
  { id: "BK-2023-M1-038", latex: "\\int x^3 e^x \\, dx", match: 94 },
  { id: "NEU-2024-C2-011", latex: "\\int x^2 \\sin x \\, dx", match: 88 },
  { id: "VNU-2024-M2-029", latex: "\\int x e^{2x} \\, dx", match: 82 },
];

export default function ProblemDetail({ activePage = "detail", onNavigate = () => {} }) {
  const [starred, setStarred] = useState(true);
  const [copiedLatex, setCopiedLatex] = useState(false);

  const handleCopy = () => {
    setCopiedLatex(true);
    setTimeout(() => setCopiedLatex(false), 1500);
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
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-1.5 text-[11px] text-blue-600 hover:text-blue-800 font-semibold bg-blue-50 px-2.5 py-1.5 rounded-lg transition-all">
              <ArrowLeft size={12} /> Quay lại kết quả
            </button>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <span>Semantic Search</span>
              <ChevronRight size={11} />
              <span className="font-mono font-semibold text-slate-600">{PROBLEM.id}</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button onClick={() => setStarred((s) => !s)}
              className={`p-2 rounded-lg transition-all ${starred ? "text-amber-500 bg-amber-50" : "text-slate-400 hover:bg-slate-50"}`}>
              <Star size={14} fill={starred ? "currentColor" : "none"} />
            </button>
            <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-50 transition-all">
              <Share2 size={14} />
            </button>
            <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-50 transition-all">
              <Printer size={14} />
            </button>
            <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-50 transition-all">
              <Download size={14} />
            </button>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400 ml-1">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold ml-1">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-5 flex gap-5">
          {/* Left — problem + solution */}
          <div className="flex-1 min-w-0 space-y-4">
            {/* Hero card */}
            <div className="bg-blue-600 rounded-2xl p-5 text-white">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[10px] font-bold bg-white/20 px-2.5 py-0.5 rounded-full">{PROBLEM.chapter}</span>
                <ChevronRight size={11} className="opacity-60" />
                <span className="text-[11px] opacity-80">{PROBLEM.topic}</span>
                <ChevronRight size={11} className="opacity-60" />
                <span className="text-[11px] opacity-80">{PROBLEM.subtopic}</span>
              </div>
              <div className="bg-white/15 rounded-xl px-4 py-3 mb-3 font-mono text-[15px] font-bold flex items-center gap-3">
                <span className="text-2xl opacity-70">∫</span>
                {PROBLEM.latex}
                <button onClick={handleCopy} className="ml-auto text-white/60 hover:text-white transition-colors">
                  {copiedLatex ? <CheckCircle size={14} /> : <Copy size={14} />}
                </button>
              </div>
              <p className="text-[12px] leading-relaxed text-white/90">{PROBLEM.statement}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-[10px] font-semibold bg-red-400/30 border border-red-300/30 text-white px-2.5 py-1 rounded-full">{PROBLEM.difficulty}</span>
                <span className="text-[10px] font-semibold bg-white/15 border border-white/20 text-white px-2.5 py-1 rounded-full">{PROBLEM.skill}</span>
                {PROBLEM.tags.map((t) => (
                  <span key={t} className="text-[10px] bg-white/10 text-white/80 px-2.5 py-1 rounded-full">{t}</span>
                ))}
              </div>
            </div>

            {/* Solution */}
            <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100 flex items-center gap-2">
                <BookMarked size={14} className="text-blue-600" />
                <span className="text-[12px] font-bold text-slate-700">Lời giải từng bước</span>
                <span className="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full ml-1">{STEPS.length} bước</span>
              </div>
              <div className="divide-y divide-slate-50">
                {STEPS.map((step) => (
                  <div key={step.num} className="px-5 py-4 flex gap-4">
                    <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0 mt-0.5">
                      {step.num}
                    </div>
                    <div className="flex-1">
                      <p className="text-[12px] font-bold text-slate-700 mb-1">{step.title}</p>
                      <p className="text-[11px] text-slate-500 leading-relaxed mb-2">{step.content}</p>
                      <div className="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
                        <code className="text-[11px] font-mono text-blue-800 break-all leading-relaxed">
                          {step.latex}
                        </code>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-xl hover:bg-blue-700 transition-all">
                <Zap size={13} /> Sinh biến thể từ bài này
              </button>
              <button className="flex items-center gap-2 px-4 py-2.5 text-blue-600 bg-blue-50 border border-blue-200 text-[12px] font-semibold rounded-xl hover:bg-blue-100 transition-all">
                <GitBranch size={13} /> Tìm bài tương tự
              </button>
              <button className="flex items-center gap-2 px-4 py-2.5 text-slate-600 bg-slate-50 border border-slate-200 text-[12px] font-semibold rounded-xl hover:bg-slate-100 transition-all ml-auto">
                <Download size={13} /> Export LaTeX
              </button>
            </div>
          </div>

          {/* Right panel */}
          <div className="w-60 flex-shrink-0 space-y-3">
            {/* Metadata */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Thông tin bài tập</p>
              {[
                { icon: Tag, label: "Mã bài", val: PROBLEM.id },
                { icon: BookOpen, label: "Nguồn", val: PROBLEM.source },
                { icon: TrendingUp, label: "Độ khó", val: PROBLEM.difficulty },
                { icon: CheckCircle, label: "Kỹ năng", val: PROBLEM.skill },
                { icon: User, label: "Thêm bởi", val: PROBLEM.addedBy },
                { icon: Clock, label: "Ngày thêm", val: PROBLEM.addedDate },
              ].map((row) => (
                <div key={row.label} className="flex items-start gap-2 py-1.5 border-b border-slate-50 last:border-0">
                  <row.icon size={11} className="text-slate-400 mt-0.5 flex-shrink-0" />
                  <span className="text-[10px] text-slate-400 flex-shrink-0 w-16">{row.label}</span>
                  <span className="text-[11px] font-semibold text-slate-700 truncate">{row.val}</span>
                </div>
              ))}
            </div>

            {/* Stats */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Thống kê</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: "Bài tương tự", val: PROBLEM.similarCount },
                  { label: "Biến thể đã sinh", val: PROBLEM.variantCount },
                  { label: "Lượt xem", val: 142 },
                  { label: "Lần dùng đề", val: 3 },
                ].map((s) => (
                  <div key={s.label} className="bg-slate-50 rounded-lg p-2.5 text-center">
                    <p className="text-[15px] font-bold text-blue-700">{s.val}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">{s.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Similar problems */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Bài tập tương tự</p>
              <div className="space-y-2">
                {SIMILAR.map((s) => (
                  <div key={s.id} className="flex items-center gap-2 p-2.5 border border-slate-100 rounded-lg hover:border-blue-200 cursor-pointer transition-all group">
                    <div className="flex-1 min-w-0">
                      <p className="text-[10px] font-bold text-slate-500 font-mono">{s.id}</p>
                      <code className="text-[10px] font-mono text-blue-700 truncate block mt-0.5">{s.latex}</code>
                    </div>
                    <div className="flex flex-col items-end gap-0.5">
                      <span className="text-[11px] font-bold text-indigo-700">{s.match}%</span>
                      <div className="w-8 h-1 rounded-full bg-slate-100 overflow-hidden">
                        <div className="h-full rounded-full bg-indigo-500" style={{ width: `${s.match}%` }} />
                      </div>
                    </div>
                  </div>
                ))}
                <button className="w-full text-[11px] text-blue-500 hover:text-blue-700 font-medium py-1 transition-colors">
                  Xem tất cả {PROBLEM.similarCount} bài →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
