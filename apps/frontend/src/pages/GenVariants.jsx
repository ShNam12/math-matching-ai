import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  ArrowLeft, ChevronRight, Zap, Download, DatabaseZap,
  RefreshCw, Copy, CheckCircle, Sliders, ArrowUpRight,
  ArrowDownRight, Minus, Eye, Plus, LayoutDashboard
} from "lucide-react";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen", active: true },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const ORIGINAL = {
  id: "BK-2023-M1-042",
  latex: "\\int x^2 e^x \\, dx",
  topic: "Tích phân từng phần",
  difficulty: "Khó",
};

const VARIANTS_DATA = [
  {
    id: "VAR-001",
    latex: "\\int x^3 e^x \\, dx",
    statement: "Tính tích phân bất định ∫ x³·eˣ dx bằng phương pháp tích phân từng phần. Cần áp dụng công thức 3 lần liên tiếp.",
    difficulty: "Khó hơn",
    diffIcon: ArrowUpRight,
    diffColor: "text-red-600 bg-red-50 border-red-200",
    strategy: "Tăng bậc đa thức: n=2 → n=3",
    qaScore: 98,
    selected: true,
  },
  {
    id: "VAR-002",
    latex: "\\int x^2 \\sin x \\, dx",
    statement: "Tính tích phân bất định ∫ x²·sin(x) dx. Thay hàm mũ bằng hàm lượng giác, cấu trúc lời giải tương tự.",
    difficulty: "Tương đương",
    diffIcon: Minus,
    diffColor: "text-amber-600 bg-amber-50 border-amber-200",
    strategy: "Thay eˣ bằng sin(x)",
    qaScore: 96,
    selected: true,
  },
  {
    id: "VAR-003",
    latex: "\\int x e^{2x} \\, dx",
    statement: "Tính tích phân ∫ x·e²ˣ dx. Giảm bậc đa thức và thay đổi tham số mũ — đơn giản hơn bài gốc một bước.",
    difficulty: "Dễ hơn",
    diffIcon: ArrowDownRight,
    diffColor: "text-emerald-600 bg-emerald-50 border-emerald-200",
    strategy: "Giảm bậc n=2 → n=1, đổi hệ số mũ",
    qaScore: 99,
    selected: false,
  },
  {
    id: "VAR-004",
    latex: "\\int x^2 \\cos(2x) \\, dx",
    statement: "Tính tích phân ∫ x²·cos(2x) dx. Kết hợp tăng tần số hàm lượng giác với giữ nguyên bậc đa thức.",
    difficulty: "Tương đương",
    diffIcon: Minus,
    diffColor: "text-amber-600 bg-amber-50 border-amber-200",
    strategy: "Thay eˣ bằng cos(2x)",
    qaScore: 94,
    selected: false,
  },
  {
    id: "VAR-005",
    latex: "\\int x^4 e^{-x} \\, dx",
    statement: "Tính tích phân ∫ x⁴·e⁻ˣ dx. Tăng bậc và đổi dấu mũ — yêu cầu áp dụng công thức tích phân từng phần 4 lần.",
    difficulty: "Khó hơn",
    diffIcon: ArrowUpRight,
    diffColor: "text-red-600 bg-red-50 border-red-200",
    strategy: "Tăng bậc n=2→4, thêm e⁻ˣ",
    qaScore: 91,
    selected: true,
  },
];

export default function GenVariants({ activePage = "gen", onNavigate = () => {} }) {
  const [variants, setVariants] = useState(VARIANTS_DATA);
  const [strategy, setStrategy] = useState("Đổi tham số");
  const [count, setCount] = useState("5");
  const [targetDiff, setTargetDiff] = useState("Tương đương");
  const [note, setNote] = useState("Giữ cấu trúc tích phân từng phần nhưng thay đổi hàm và bậc");
  const [generating, setGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const toggleSelect = (id) =>
    setVariants((vs) => vs.map((v) => v.id === id ? { ...v, selected: !v.selected } : v));

  const handleGen = () => {
    setGenerating(true);
    setTimeout(() => setGenerating(false), 2000);
  };

  const handleCopy = (id) => {
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const selectedCount = variants.filter((v) => v.selected).length;

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
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-1.5 text-[11px] text-blue-600 font-semibold bg-blue-50 px-2.5 py-1.5 rounded-lg">
              <ArrowLeft size={12} /> Chi tiết bài tập
            </button>
            <div className="flex items-center gap-1 text-[11px] text-slate-400">
              <span>{ORIGINAL.id}</span><ChevronRight size={11} /><span className="text-slate-600 font-semibold">Sinh biến thể</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden flex gap-0">
          {/* Left: config */}
          <div className="w-64 flex-shrink-0 border-r border-slate-100 bg-white overflow-y-auto p-4 space-y-4">
            <div>
              <p className="text-[11px] font-bold text-slate-700 mb-3 flex items-center gap-2">
                <Sliders size={13} className="text-blue-600" /> Cấu hình sinh
              </p>

              {/* Original */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 mb-4">
                <p className="text-[10px] font-bold text-blue-700 mb-1.5 uppercase tracking-wide">Bài gốc</p>
                <code className="text-[12px] font-mono text-blue-800 font-bold block mb-1">{ORIGINAL.latex}</code>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-blue-600 bg-blue-100 px-2 py-0.5 rounded">{ORIGINAL.topic}</span>
                  <span className="text-[10px] text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">{ORIGINAL.difficulty}</span>
                </div>
              </div>

              {/* Form fields */}
              <div className="space-y-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">Chiến lược biến thể</label>
                  <select value={strategy} onChange={(e) => setStrategy(e.target.value)}
                    className="w-full px-2.5 py-2 border border-slate-200 rounded-lg text-[11px] bg-slate-50 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400">
                    <option>Đổi tham số</option>
                    <option>Đổi hàm</option>
                    <option>Tăng độ khó</option>
                    <option>Giảm độ khó</option>
                    <option>Đa dạng hóa</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">Số biến thể</label>
                  <div className="flex gap-1.5">
                    {["3", "5", "10"].map((n) => (
                      <button key={n} onClick={() => setCount(n)}
                        className={`flex-1 py-1.5 text-[11px] font-semibold rounded-lg border transition-all ${count === n ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-500 border-slate-200 hover:border-blue-300"}`}>
                        {n}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">Độ khó mục tiêu</label>
                  <div className="space-y-1">
                    {[
                      { val: "Dễ hơn", icon: ArrowDownRight, color: "text-emerald-700" },
                      { val: "Tương đương", icon: Minus, color: "text-amber-700" },
                      { val: "Khó hơn", icon: ArrowUpRight, color: "text-red-700" },
                    ].map((d) => (
                      <label key={d.val} className={`flex items-center gap-2 px-2.5 py-2 rounded-lg border cursor-pointer transition-all ${targetDiff === d.val ? "border-blue-300 bg-blue-50" : "border-slate-200 hover:border-slate-300"}`}>
                        <input type="radio" name="diff" checked={targetDiff === d.val} onChange={() => setTargetDiff(d.val)} className="sr-only" />
                        <div className={`w-3.5 h-3.5 rounded-full border-2 flex items-center justify-center ${targetDiff === d.val ? "border-blue-600" : "border-slate-300"}`}>
                          {targetDiff === d.val && <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />}
                        </div>
                        <d.icon size={12} className={d.color} />
                        <span className={`text-[11px] font-medium ${targetDiff === d.val ? "text-blue-700" : "text-slate-600"}`}>{d.val}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">Ghi chú cho AI</label>
                  <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={3}
                    className="w-full px-2.5 py-2 border border-slate-200 rounded-lg text-[11px] bg-slate-50 text-slate-700 resize-none focus:outline-none focus:ring-1 focus:ring-blue-400 leading-relaxed" />
                </div>
              </div>

              <button onClick={handleGen}
                className={`w-full mt-3 flex items-center justify-center gap-2 py-2.5 text-[12px] font-bold rounded-xl transition-all ${generating ? "bg-slate-200 text-slate-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}`}>
                {generating ? <RefreshCw size={13} className="animate-spin" /> : <Sparkles size={13} />}
                {generating ? "Đang sinh..." : "Sinh biến thể"}
              </button>
            </div>
          </div>

          {/* Right: results */}
          <div className="flex-1 overflow-y-auto p-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-bold text-slate-700">Kết quả sinh</span>
                <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{variants.length} biến thể</span>
                <span className="text-[10px] bg-blue-100 text-blue-700 font-semibold px-2 py-0.5 rounded-full">{selectedCount} đã chọn</span>
              </div>
              <div className="flex items-center gap-2">
                {selectedCount > 0 && (
                  <>
                    <button className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-all">
                      <Download size={12} /> Export LaTeX ({selectedCount})
                    </button>
                    <button className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg hover:bg-emerald-100 transition-all">
                      <DatabaseZap size={12} /> Thêm vào corpus
                    </button>
                  </>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {variants.map((v) => {
                const DiffIcon = v.diffIcon;
                const isSelected = v.selected;
                return (
                  <div key={v.id}
                    className={`bg-white border rounded-xl overflow-hidden transition-all ${isSelected ? "border-blue-300 ring-1 ring-blue-200" : "border-slate-100 hover:border-blue-100"}`}>
                    <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(v.id)}
                          className="w-3.5 h-3.5 rounded accent-blue-600 cursor-pointer" />
                        <span className="text-[10px] font-bold text-slate-400 font-mono">{v.id}</span>
                        <span className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${v.diffColor}`}>
                          <DiffIcon size={10} /> {v.difficulty}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <span className="text-[10px] text-slate-400">QA:</span>
                          <span className={`text-[11px] font-bold ${v.qaScore >= 96 ? "text-emerald-600" : "text-amber-600"}`}>{v.qaScore}%</span>
                          <div className="w-10 h-1 rounded-full bg-slate-100 overflow-hidden">
                            <div className={`h-full rounded-full ${v.qaScore >= 96 ? "bg-emerald-500" : "bg-amber-400"}`} style={{ width: `${v.qaScore}%` }} />
                          </div>
                        </div>
                        <button onClick={() => handleCopy(v.id)}
                          className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
                          {copiedId === v.id ? <CheckCircle size={12} className="text-emerald-500" /> : <Copy size={12} />}
                        </button>
                        <button className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
                          <Eye size={12} />
                        </button>
                      </div>
                    </div>
                    <div className="px-4 py-3">
                      <div className="flex items-center gap-3 mb-2.5">
                        <div className="w-5 h-5 rounded bg-purple-600 flex items-center justify-center flex-shrink-0">
                          <span className="text-white font-bold" style={{ fontSize: 9 }}>∫</span>
                        </div>
                        <code className="text-[12px] font-mono text-purple-700 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-100 font-bold">
                          {v.latex}
                        </code>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed mb-2">{v.statement}</p>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-400">Chiến lược:</span>
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">{v.strategy}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* AI Explanation */}
            <div className="mt-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-white">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={13} className="text-blue-400" />
                <span className="text-[11px] font-bold text-blue-300">Giải thích từ AI</span>
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed">
                5 biến thể được tạo bằng cách thay đổi có kiểm soát một hoặc hai tham số duy nhất trong mỗi lần sinh, đảm bảo bảo toàn cấu trúc cốt lõi của phương pháp tích phân từng phần. Tất cả biến thể đều qua QA tự động — không có vấn đề về cú pháp LaTeX. Biến thể VAR-004 có QA score thấp hơn (94%) do độ phức tạp tăng, khuyến nghị kiểm tra thủ công trước khi sử dụng.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
