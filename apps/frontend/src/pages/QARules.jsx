import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  CheckCircle, XCircle, AlertTriangle, RefreshCw,
  Play, Download, Clock, Info,
  Shield, Code2, Copy, Layers, AlertCircle, Eye, LayoutDashboard
} from "lucide-react";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa" },
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

const MCQ_RULES = [
  {
    id: "MCQ-STRUCT",
    title: "Structural rules",
    desc: "MCQ must have exactly 4 choices A/B/C/D, one correct choice, a valid correct_choice key, and no empty option text.",
    category: "Structural",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo backend quality service",
    icon: CheckSquare,
    affectedIds: [],
    codes: [
      "mcq_missing_choices",
      "mcq_invalid_choice_count",
      "mcq_invalid_choice_key",
      "mcq_duplicate_choice_key",
      "mcq_missing_correct_choice",
      "mcq_correct_choice_not_found",
      "mcq_multiple_correct_choices",
      "mcq_no_correct_choice_flagged",
      "mcq_empty_choice_text",
    ],
    checks: [
      "Question type multiple_choice requires choices.",
      "Allowed keys are A, B, C, D.",
      "Exactly one option is marked correct.",
      "correct_choice must point to the marked correct option.",
    ],
    savePolicy: "Blocking issue: cannot save until fixed.",
  },
  {
    id: "MCQ-DISTRACTOR",
    title: "Distractor rules",
    desc: "Distractors must be distinct from each other and must not duplicate or symbolically equal the correct answer.",
    category: "Distractor",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo backend quality service",
    icon: Copy,
    affectedIds: [],
    codes: [
      "mcq_duplicate_choice_content",
      "mcq_distractor_equals_correct_answer",
      "mcq_all_choices_too_similar",
    ],
    checks: [
      "Normalize text, whitespace, and LaTeX before comparison.",
      "Detect duplicate option content.",
      "Detect distractors equal to the correct answer.",
      "Warn when all choices are too similar.",
    ],
    savePolicy: "Duplicate/equal distractors are blocking; similarity can be reviewed.",
  },
  {
    id: "MCQ-SYMBOLIC",
    title: "Symbolic rules",
    desc: "When a solver is available, the correct choice must match the symbolic result and distractors must not be equivalent to it.",
    category: "Symbolic",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo SymbolicMCQValidator",
    icon: Code2,
    affectedIds: [],
    codes: [
      "symbolic_correct_answer_verified",
      "symbolic_correct_answer_mismatch",
      "symbolic_distractor_equals_correct",
      "symbolic_distractor_duplicate",
      "symbolic_parse_failed",
      "solver_not_available",
    ],
    checks: [
      "Run solver_code through the solver executor.",
      "Compare correct answer with solver output using symbolic simplification.",
      "Compare distractors against solver output and each other.",
      "Report parser and solver failures without crashing the pipeline.",
    ],
    savePolicy: "Mismatch and equivalent distractors block save; missing solver is a warning.",
  },
  {
    id: "MCQ-TAXONOMY",
    title: "Taxonomy rules",
    desc: "Question metadata must align with the Calculus 1 taxonomy: chapter, topic, problem type, difficulty, and skills.",
    category: "Taxonomy",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo taxonomy quality endpoint",
    icon: Layers,
    affectedIds: [],
    codes: [
      "taxonomy_low_confidence",
      "taxonomy_missing_code",
      "taxonomy_invalid_code",
      "difficulty_mismatch",
    ],
    checks: [
      "Validate chapter/topic/problem type codes.",
      "Surface low-confidence AI Matching results.",
      "Compare generated difficulty against source and taxonomy context.",
      "Keep skills consistent with the selected problem type.",
    ],
    savePolicy: "Warnings route the question to review; invalid taxonomy needs correction.",
  },
  {
    id: "MCQ-SEMANTIC",
    title: "Semantic duplicate rules",
    desc: "Generated MCQs are compared with the existing bank so near-duplicate statements or formulas can be blocked or reviewed.",
    category: "Semantic",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo semantic search quality",
    icon: Shield,
    affectedIds: [],
    codes: [
      "exact_duplicate_statement",
      "semantic_duplicate_candidate",
      "invalid_formula_payload",
    ],
    checks: [
      "Compare normalized statement text.",
      "Use semantic search for near-duplicate candidates.",
      "Include formula payloads and choice text in duplicate context.",
      "Show duplicate question ids and similarity scores for review.",
    ],
    savePolicy: "Exact duplicates block save; semantic duplicates require review.",
  },
  {
    id: "MCQ-SAVE",
    title: "Save policy",
    desc: "The save endpoint persists MCQs only when the merged validation report has no blocking issues.",
    category: "Policy",
    status: "ok",
    passRate: 100,
    issues: 0,
    lastRun: "Theo generation save endpoint",
    icon: FileText,
    affectedIds: [],
    codes: [
      "can_save_false",
      "blocking_issues",
      "warnings",
      "validation_report",
    ],
    checks: [
      "Merge structural, distractor, symbolic, taxonomy, and semantic findings.",
      "Block save when blocking_issues is not empty.",
      "Allow save with warnings but persist validation_report.",
      "Store choices, correct_choice, solver_code, and generation_method.",
    ],
    savePolicy: "Only candidates with can_save=true are stored in the question bank.",
  },
];

const statusCfg = {
  idle: { label: "Chưa chạy", icon: Clock, bg: "bg-slate-50", text: "text-slate-500", border: "border-slate-200", dot: "bg-slate-300" },
  ok:   { label: "Đã qua", icon: CheckCircle,    bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", dot: "bg-emerald-500" },
  warn: { label: "Cảnh báo", icon: AlertTriangle, bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-200",   dot: "bg-amber-500" },
  error:{ label: "Lỗi",      icon: XCircle,       bg: "bg-red-50",     text: "text-red-700",     border: "border-red-200",     dot: "bg-red-500" },
};

const catColor = {
  "Cú pháp": "bg-blue-50 text-blue-700 border-blue-200",
  "Metadata": "bg-purple-50 text-purple-700 border-purple-200",
  "Nội dung": "bg-teal-50 text-teal-700 border-teal-200",
  "Vector": "bg-indigo-50 text-indigo-700 border-indigo-200",
  Structural: "bg-blue-50 text-blue-700 border-blue-200",
  Distractor: "bg-teal-50 text-teal-700 border-teal-200",
  Symbolic: "bg-indigo-50 text-indigo-700 border-indigo-200",
  Taxonomy: "bg-purple-50 text-purple-700 border-purple-200",
  Semantic: "bg-amber-50 text-amber-700 border-amber-200",
  Policy: "bg-slate-50 text-slate-700 border-slate-200",
};

export default function QARules({
  activePage = "qa",
  onNavigate = () => {},
  selectedQualityContext = null,
}) {
  const [filterStatus, setFilterStatus] = useState("all");
  const [selected, setSelected] = useState(null);
  const [running, setRunning] = useState(false);

  const hasQualityContext = Boolean(selectedQualityContext?.quality);
  const isTaxonomyQualityContext = selectedQualityContext?.type === "taxonomy";

  const qualityResult = selectedQualityContext?.quality;
  const candidate = selectedQualityContext?.candidate;
  const question = selectedQualityContext?.question;

  const warnings = qualityResult?.warnings || [];
  const blockingIssues = qualityResult?.blocking_issues || [];
  const semanticDuplicates = qualityResult?.semantic_duplicates || [];
  const symbolicChecks = qualityResult?.symbolic_checks || [];

  const qualityRules = hasQualityContext
    ? [
        isTaxonomyQualityContext
          ? {
              id: "QA-TAXONOMY",
              title: "Kiểm định AI Matching theo cây tri thức",
              desc: qualityResult.can_accept
                ? "Câu hỏi đạt kiểm định taxonomy."
                : "Câu hỏi có vấn đề trong kết quả AI Matching.",
              category: "Metadata",
              status: blockingIssues.length
                ? "error"
                : warnings.length
                  ? "warn"
                  : "ok",
              passRate: blockingIssues.length
                ? 60
                : warnings.length
                  ? 85
                  : 100,
              issues: warnings.length + blockingIssues.length,
              lastRun: "Vừa kiểm định",
              icon: Shield,
              affectedIds: [selectedQualityContext.questionId].filter(Boolean),
            }
          : {
              id: "QA-CANDIDATE",
              title: "Kiểm định candidate sinh biến thể",
              desc: selectedQualityContext.quality.can_save
                ? "Candidate đạt điều kiện lưu vào corpus."
                : "Candidate có vấn đề chặn lưu vào corpus.",
              category: "Nội dung",
              status: selectedQualityContext.quality.blocking_issues?.length
                ? "error"
                : selectedQualityContext.quality.warnings?.length
                  ? "warn"
                  : "ok",
              passRate: selectedQualityContext.quality.blocking_issues?.length
                ? 60
                : selectedQualityContext.quality.warnings?.length
                  ? 85
                  : 100,
              issues:
                (selectedQualityContext.quality.warnings?.length || 0) +
                (selectedQualityContext.quality.blocking_issues?.length || 0),
              lastRun: "Vừa kiểm định",
              icon: Shield,
              affectedIds: [selectedQualityContext.variantId].filter(Boolean),
            },
      ]
    : MCQ_RULES.map((rule) => ({
        ...rule,
        legacyRuleCount: RULES.length,
        status: "idle",
        passRate: 0,
        issues: 0,
        lastRun: "Chưa chạy",
        affectedIds: [],
      }));

  const filtered = qualityRules.filter((r) =>
    filterStatus === "all" ? true : r.status === filterStatus
  );

  const counts = {
    all: qualityRules.length,
    ok: qualityRules.filter((r) => r.status === "ok").length,
    warn: qualityRules.filter((r) => r.status === "warn").length,
    error: qualityRules.filter((r) => r.status === "error").length,
    idle: qualityRules.filter((r) => r.status === "idle").length,
  };

  const selectedRule = selected || filtered[0] || qualityRules[0];

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
              const isSelected = selectedRule?.id === rule.id;
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
                    <div className={`h-full rounded-full transition-all ${rule.status === "ok"
                      ? "bg-emerald-500"
                      : rule.status === "warn"
                        ? "bg-amber-400"
                        : rule.status === "error"
                          ? "bg-red-500"
                          : "bg-slate-300"}`}
                      style={{ width: `${rule.passRate}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detail panel */}
          {selectedRule && (
            <div className="w-72 flex-shrink-0 border-l border-slate-100 bg-white overflow-y-auto p-4 space-y-4">
              {(() => {
                const sc = statusCfg[selectedRule.status];
                return (
                  <>
                    <div className={`rounded-xl p-4 ${sc.bg} border ${sc.border}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <sc.icon size={16} className={sc.text} />
                        <span className={`text-[11px] font-bold ${sc.text}`}>{sc.label.toUpperCase()}</span>
                      </div>
                      <p className="text-[13px] font-bold text-slate-800 mb-1">{selectedRule.title}</p>
                      <p className="text-[11px] text-slate-600 leading-relaxed">{selectedRule.desc}</p>
                    </div>

                    {hasQualityContext && candidate && (
                      <div className="bg-blue-50 border border-blue-100 rounded-xl p-3">
                        <p className="text-[11px] font-bold text-blue-700 mb-2">
                          Candidate đang kiểm định
                        </p>
                        <code className="block text-[10px] font-mono text-blue-800 bg-white/70 border border-blue-100 rounded-lg px-2 py-1 mb-2 break-all">
                          {candidate.formulas?.[0]?.latex || candidate.answer || "Không có công thức"}
                        </code>
                        <p className="text-[11px] text-slate-600 leading-relaxed">
                          {candidate.statement}
                        </p>
                      </div>
                    )}

                    {hasQualityContext && isTaxonomyQualityContext && question && (
                      <div className="bg-blue-50 border border-blue-100 rounded-xl p-3">
                        <p className="text-[11px] font-bold text-blue-700 mb-2">
                          Câu hỏi đang kiểm định
                        </p>

                        <code className="block text-[10px] font-mono text-blue-800 bg-white/70 border border-blue-100 rounded-lg px-2 py-1 mb-2 break-all">
                          {question.id}
                        </code>

                        <p className="text-[11px] text-slate-600 leading-relaxed mb-2">
                          {question.statement}
                        </p>

                        <div className="space-y-1 text-[10px] text-slate-500">
                          <p>
                            Chương:{" "}
                            <span className="font-semibold text-slate-700">
                              {question.chapter_name || "Chưa có"}
                            </span>
                          </p>
                          <p>
                            Chủ đề:{" "}
                            <span className="font-semibold text-slate-700">
                              {question.topic_name || "Chưa có"}
                            </span>
                          </p>
                          <p>
                            Dạng bài:{" "}
                            <span className="font-semibold text-slate-700">
                              {question.problem_type_name || "Chưa có"}
                            </span>
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="bg-slate-50 rounded-xl p-3 space-y-2">
                      <p className="text-[11px] font-bold text-slate-600 mb-2">Thông tin chi tiết</p>
                      {[
                        { label: "Rule ID", val: selectedRule.id },
                        { label: "Danh mục", val: selectedRule.category },
                        { label: "Pass rate", val: `${selectedRule.passRate}%` },
                        { label: "Số vấn đề", val: selectedRule.issues === 0 ? "Không có" : selectedRule.issues },
                        { label: "Lần quét", val: selectedRule.lastRun },
                      ].map((row) => (
                        <div key={row.label} className="flex justify-between items-center">
                          <span className="text-[11px] text-slate-500">{row.label}</span>
                          <span className="text-[11px] font-semibold text-slate-700">{row.val}</span>
                        </div>
                      ))}
                    </div>

                    {selectedRule.checks?.length > 0 && (
                      <div className="bg-white border border-slate-100 rounded-xl p-3">
                        <p className="text-[11px] font-bold text-slate-600 mb-2">
                          Checklist
                        </p>
                        <div className="space-y-1.5">
                          {selectedRule.checks.map((check) => (
                            <div key={check} className="flex items-start gap-2">
                              <CheckCircle size={11} className="mt-0.5 text-emerald-600 flex-shrink-0" />
                              <span className="text-[10px] text-slate-600 leading-relaxed">
                                {check}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedRule.codes?.length > 0 && (
                      <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
                        <p className="text-[11px] font-bold text-slate-600 mb-2">
                          Backend quality codes
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedRule.codes.map((code) => (
                            <code
                              key={code}
                              className="rounded-md border border-slate-200 bg-white px-1.5 py-1 text-[9px] font-semibold text-slate-600"
                            >
                              {code}
                            </code>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedRule.savePolicy && (
                      <div className="rounded-xl border border-blue-100 bg-blue-50 p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Shield size={12} className="text-blue-600" />
                          <p className="text-[11px] font-bold text-blue-700">
                            Save policy
                          </p>
                        </div>
                        <p className="text-[10px] text-blue-700 leading-relaxed">
                          {selectedRule.savePolicy}
                        </p>
                      </div>
                    )}

                    {hasQualityContext && blockingIssues.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-red-700 mb-2">
                          Lỗi chặn lưu
                        </p>
                        <div className="space-y-1.5">
                          {blockingIssues.map((issue) => (
                            <div key={`${issue.code}-${issue.field || "general"}`} className="rounded-lg border border-red-100 bg-red-50 px-2.5 py-2">
                              <div className="flex items-center gap-1.5 mb-1">
                                <XCircle size={11} className="text-red-600" />
                                <span className="text-[10px] font-bold text-red-700">{issue.code}</span>
                                {issue.field && (
                                  <span className="text-[10px] text-red-500">({issue.field})</span>
                                )}
                              </div>
                              <p className="text-[10px] text-red-700 leading-relaxed">
                                {issue.message}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {hasQualityContext && warnings.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-amber-700 mb-2">
                          Cảnh báo
                        </p>
                        <div className="space-y-1.5">
                          {warnings.map((issue) => (
                            <div key={`${issue.code}-${issue.field || "general"}`} className="rounded-lg border border-amber-100 bg-amber-50 px-2.5 py-2">
                              <div className="flex items-center gap-1.5 mb-1">
                                <AlertTriangle size={11} className="text-amber-600" />
                                <span className="text-[10px] font-bold text-amber-700">{issue.code}</span>
                                {issue.field && (
                                  <span className="text-[10px] text-amber-600">({issue.field})</span>
                                )}
                              </div>
                              <p className="text-[10px] text-amber-700 leading-relaxed">
                                {issue.message}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {hasQualityContext && symbolicChecks.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-blue-700 mb-2">
                          Symbolic checks
                        </p>
                        <div className="space-y-1.5">
                          {symbolicChecks.map((check, index) => (
                            <div
                              key={`${check.code || "symbolic"}-${index}`}
                              className={`rounded-lg border px-2.5 py-2 ${
                                check.passed
                                  ? "border-emerald-100 bg-emerald-50"
                                  : "border-blue-100 bg-blue-50"
                              }`}
                            >
                              <div className="flex items-center gap-1.5 mb-1">
                                {check.passed ? (
                                  <CheckCircle size={11} className="text-emerald-600" />
                                ) : (
                                  <AlertTriangle size={11} className="text-blue-600" />
                                )}
                                <span
                                  className={`text-[10px] font-bold ${
                                    check.passed ? "text-emerald-700" : "text-blue-700"
                                  }`}
                                >
                                  {check.code || "symbolic_check"}
                                </span>
                              </div>
                              {check.message && (
                                <p
                                  className={`text-[10px] leading-relaxed ${
                                    check.passed ? "text-emerald-700" : "text-blue-700"
                                  }`}
                                >
                                  {check.message}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {hasQualityContext && semanticDuplicates.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-purple-700 mb-2">
                          Bài tương đồng semantic
                        </p>
                        <div className="space-y-1.5">
                          {semanticDuplicates.map((duplicate) => (
                            <div key={duplicate.question_id} className="rounded-lg border border-purple-100 bg-purple-50 px-2.5 py-2">
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <span className="text-[10px] font-mono font-bold text-purple-700 truncate">
                                  {duplicate.question_id}
                                </span>
                                <span className="text-[10px] font-bold text-purple-700">
                                  {Math.round(duplicate.score * 100)}%
                                </span>
                              </div>
                              <p className="text-[10px] text-purple-700 leading-relaxed line-clamp-2">
                                {duplicate.statement}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {hasQualityContext &&
                      blockingIssues.length === 0 &&
                      warnings.length === 0 &&
                      semanticDuplicates.length === 0 && (
                        <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <CheckCircle size={13} className="text-emerald-600" />
                            <p className="text-[11px] font-bold text-emerald-700">
                              Không có vấn đề chất lượng
                            </p>
                          </div>
                          <p className="text-[10px] text-emerald-700 leading-relaxed">
                            {isTaxonomyQualityContext
                              ? "Kết quả AI Matching của câu hỏi đạt các rule taxonomy."
                              : "Candidate có thể được lưu vào corpus."}
                          </p>
                        </div>
                      )}

                    {selectedRule.affectedIds.length > 0 && (
                      <div>
                        <p className="text-[11px] font-bold text-slate-600 mb-2">Bài tập bị ảnh hưởng (mẫu)</p>
                        <div className="space-y-1">
                          {selectedRule.affectedIds.map((id) => (
                            <div key={id} className="flex items-center gap-2 px-2.5 py-1.5 bg-red-50 border border-red-100 rounded-lg">
                              <AlertCircle size={11} className="text-red-500" />
                              <span className="text-[11px] font-mono text-red-700">{id}</span>
                              <button className="ml-auto">
                                <Eye size={11} className="text-red-400 hover:text-red-600" />
                              </button>
                            </div>
                          ))}
                          {selectedRule.issues > selectedRule.affectedIds.length && (
                            <p className="text-[10px] text-slate-400 text-center pt-1">
                              +{selectedRule.issues - selectedRule.affectedIds.length} bài khác...
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="space-y-2">
                      <button className="w-full flex items-center justify-center gap-2 px-3 py-2 text-[11px] font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all">
                        <Play size={12} /> Chạy rule này
                      </button>
                      {selectedRule.issues > 0 && (
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
