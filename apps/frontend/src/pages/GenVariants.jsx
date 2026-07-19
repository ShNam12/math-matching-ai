import { useEffect, useState } from "react";
import LatexInline from "../components/LatexInline";
import MathText from "../components/MathText";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  ArrowLeft, ChevronRight, Download, DatabaseZap,
  RefreshCw, Copy, CheckCircle, Sliders, ArrowUpRight,
  ArrowDownRight, Minus, Eye, LayoutDashboard
} from "lucide-react";
import { getQuestion } from "../services/questionApi";
import {
  previewGeneratedQuestions,
  previewConvertToMCQ,
  previewSymbolicMCQ,
  assessGeneratedQuestionQuality,
  saveGeneratedQuestion,
  saveConvertToMCQ,
  saveSymbolicMCQ,
  listSymbolicMCQSolvers,
} from "../services/generationApi";
import { filterNavigationItems } from "../auth/navigation";
import UserMenu from "../components/UserMenu";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa" },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen", active: true },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const GENERATION_MODES = [
  { id: "ai", label: "Sinh trắc nghiệm bằng AI" },
  { id: "symbolic", label: "Sinh theo bộ giải toán" },
  { id: "convert", label: "Chuyển bài gốc thành trắc nghiệm" },
];

const SOLVER_LABELS = {
  DERIV_COMPOSITE: "Đạo hàm hàm hợp",
  DERIV_MONOMIAL: "Đạo hàm hàm lũy thừa",
  INT_MONOMIAL: "Tích phân hàm lũy thừa",
  INT_RATIONAL: "Tích phân hàm hữu tỉ",
  INT_XN_EXP: "Tích phân xⁿeˣ",
  INT_XN_LN: "Tích phân xⁿln(x)",
  LIMIT_ZERO_ZERO: "Giới hạn dạng vô định 0/0",
};

const GENERATION_METHOD_LABELS = {
  ai: "Sinh bằng AI",
  symbolic: "Sinh bằng bộ giải toán",
  convert: "Chuyển từ bài gốc",
  ai_symbolic: "AI kết hợp bộ giải toán",
};

function getSolverLabel(solver) {
  const code = typeof solver === "string" ? solver : solver?.code;

  return SOLVER_LABELS[code] || solver?.name || code || "Không xác định";
}

function getGenerationMethodLabel(method) {
  return GENERATION_METHOD_LABELS[method] || method || "Không xác định";
}

function getValidationReport(candidate) {
  return candidate?.validation_report || {
    can_save: true,
    warnings: [],
    blocking_issues: [],
    symbolic_checks: [],
  };
}

function getIssueCode(issue) {
  return issue?.code || issue?.message || String(issue || "");
}

function getChoiceValue(choice, field) {
  if (!choice || typeof choice !== "object") return null;
  return choice[field] ?? null;
}

function getChoiceDisplayText(choice) {
  const text = getChoiceValue(choice, "text");
  const latex = getChoiceValue(choice, "latex");

  if (latex) return `$${latex}$`;
  if (text) return String(text);
  return "";
}

export default function GenVariants({
  activePage = "gen",
  onNavigate = () => {},
  currentUser = null,
  onLogout = () => {},
  sourceQuestionId = null,
  generationSession = null,
  onOpenQualityContext = () => {},
}) {
  const restoredSession =
    generationSession?.sourceQuestionId === sourceQuestionId
      ? generationSession
      : null;
  const getInitialSessionValue = (key, fallback) =>
    restoredSession?.[key] ?? fallback;
  const [variants, setVariants] = useState(
    () => restoredSession?.variants ?? []
  );
  const [generationMode, setGenerationMode] = useState(
    () => restoredSession?.generationMode ?? "ai"
  );
  const [solvers, setSolvers] = useState([]);
  const [selectedSolverCode, setSelectedSolverCode] = useState(
    () => restoredSession?.selectedSolverCode ?? ""
  );
  const [solverError, setSolverError] = useState(null);
  const [strategy, setStrategy] = useState(
    () => getInitialSessionValue("strategy", "Đổi tham số")
  );
  const [count, setCount] = useState(
    () => getInitialSessionValue("count", "1")
  );
  const [targetDiff, setTargetDiff] = useState(
    () => getInitialSessionValue("targetDiff", "Tương đương")
  );
  const [note, setNote] = useState(
    () => getInitialSessionValue(
      "note",
      "Giữ cấu trúc tích phân từng phần nhưng thay đổi hàm và bậc"
    )
  );
  const [generating, setGenerating] = useState(false);
  const [checkingQuality, setCheckingQuality] = useState(false);
  const [saving, setSaving] = useState(false);
  const [generationError, setGenerationError] = useState(null);
  const [saveMessage, setSaveMessage] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const [sourceQuestion, setSourceQuestion] = useState(null);
  const [sourceLoading, setSourceLoading] = useState(false);
  const [sourceError, setSourceError] = useState(null);

  const toggleSelect = (id) =>
    setVariants((vs) => vs.map((v) => v.id === id ? { ...v, selected: !v.selected } : v));

  const getDifficultyMeta = (difficulty) => {
    if (difficulty === "Khó hơn" || difficulty === "hard") {
      return {
        label: "Khó hơn",
        diffIcon: ArrowUpRight,
        diffColor: "text-red-600 bg-red-50 border-red-200",
      };
    }

    if (difficulty === "Dễ hơn" || difficulty === "easy") {
      return {
        label: "Dễ hơn",
        diffIcon: ArrowDownRight,
        diffColor: "text-emerald-600 bg-emerald-50 border-emerald-200",
      };
    }

    return {
      label: difficulty || "Tương đương",
      diffIcon: Minus,
      diffColor: "text-amber-600 bg-amber-50 border-amber-200",
    };
  };

  const getRequestedDifficulty = () => {
    if (targetDiff === "Dễ hơn") {
      return "easy";
    }

    if (targetDiff === "Khó hơn") {
      return "hard";
    }

    return sourceQuestion?.difficulty || null;
  };

  const getQualityScore = (qualityResult) => {
    if (!qualityResult) {
      return 0;
    }

    if (qualityResult.blocking_issues?.length) {
      return 60;
    }

    if (qualityResult.warnings?.length) {
      return 85;
    }

    return 100;
  };

  const mapCandidateToVariant = (candidate, index) => {
    const difficultyMeta = getDifficultyMeta(candidate.difficulty || targetDiff);
    const firstFormula = candidate.formulas?.[0];

    return {
      id: `GEN-${String(index + 1).padStart(3, "0")}`,
      latex: firstFormula?.latex || candidate.answer || "Generated question",
      statement: candidate.statement,
      solution: candidate.solution,
      answer: candidate.answer,
      questionType: candidate.question_type || "free_response",
      choices: Array.isArray(candidate.choices) ? candidate.choices : [],
      correctChoice: candidate.correct_choice || null,
      validationReport: getValidationReport(candidate),
      generationMethod: candidate.generation_method || generationMode,
      solverCode: candidate.solver_code || null,
      formulas: candidate.formulas || [],
      difficulty: difficultyMeta.label,
      diffIcon: difficultyMeta.diffIcon,
      diffColor: difficultyMeta.diffColor,
      strategy: candidate.quality_warnings?.length
        ? candidate.quality_warnings.join(", ")
        : "Sinh từ backend",
      qaScore: candidate.quality_warnings?.length ? 85 : 100,
      selected: false,
      mode: generationMode,
      candidate,
    };
  };

  const checkVariantQuality = async (variant) => {
    const qualityResult = await assessGeneratedQuestionQuality({
      source_question_id: sourceQuestionId,
      requested_difficulty: getRequestedDifficulty(),
      candidate: variant.candidate,
    });

    return {
      ...variant,
      quality: qualityResult,
      canSave: qualityResult.can_save,
      validationReport: {
        can_save: qualityResult.can_save,
        warnings: qualityResult.warnings || [],
        blocking_issues: qualityResult.blocking_issues || [],
        symbolic_checks: qualityResult.symbolic_checks || [],
      },
      qaScore: getQualityScore(qualityResult),
      strategy: qualityResult.quality_warnings?.length
        ? qualityResult.quality_warnings.join(", ")
        : variant.strategy,
    };
  };

  const handleGen = async () => {
    if (!hasLoadedSource) {
      setGenerationError(
        "Hãy chọn và tải thành công câu hỏi nguồn trước khi sinh biến thể.",
      );
      return;
    }

    setGenerating(true);
    setGenerationError(null);

    try {
      const constraints = {
        subject: sourceQuestion?.subject || null,
        chapter: sourceQuestion?.chapter || null,
        difficulty: getRequestedDifficulty(),
        skills: sourceQuestion?.skills || [],
        note: note.trim() || null,
        preserve_formula_style: true,
        avoid_duplicate: true,
      };

      let data;

      if (generationMode === "convert") {
        data = await previewConvertToMCQ(sourceQuestionId, {
          generation_count: Number(count),
          constraints,
        });
      } else if (generationMode === "symbolic") {
        if (!selectedSolverCode) {
          throw new Error("Chưa có bộ giải toán khả dụng.");
        }

        data = await previewSymbolicMCQ({
          solver_code: selectedSolverCode,
          generation_count: Number(count),
          difficulty: getRequestedDifficulty(),
          subject: sourceQuestion?.subject || null,
          chapter: sourceQuestion?.chapter || null,
          skills: sourceQuestion?.skills || [],
          taxonomy: {
            chapter_code: sourceQuestion?.chapter_code || null,
            topic_code: sourceQuestion?.topic_code || null,
            problem_type_code: sourceQuestion?.problem_type_code || null,
          },
        });
      } else {
        const payload = {
          source_question_id: sourceQuestionId,
          generation_count: Number(count),
          constraints,
        };

        data = await previewGeneratedQuestions(payload);
      }
      const previewVariants = data.candidates.map(mapCandidateToVariant);
      setVariants(previewVariants);

      setCheckingQuality(true);
      const checkedVariants = await Promise.all(
        previewVariants.map((variant) => checkVariantQuality(variant))
      );
      setVariants(checkedVariants);
    } catch (requestError) {
      setGenerationError(requestError.message);
      setVariants([]);
    } finally {
      setGenerating(false);
      setCheckingQuality(false);
    }
  };

  const handleSaveSelected = async () => {
    const selectedVariants = variants.filter((variant) => variant.selected);

    if (!hasLoadedSource || selectedVariants.length === 0) {
      return;
    }

    setSaving(true);
    setGenerationError(null);
    setSaveMessage(null);
    let savingVariantId = null;

    try {
      const savedResults = [];

      for (const variant of selectedVariants) {
        savingVariantId = variant.id;

        if (variant.canSave === false) {
          throw new Error(`Biến thể ${variant.id} chưa đạt chất lượng để lưu`);
        }

        let saved;

        if (variant.mode === "convert") {
          saved = await saveConvertToMCQ(sourceQuestionId, {
            candidate: variant.candidate,
          });
        } else if (variant.mode === "symbolic") {
          saved = await saveSymbolicMCQ({
            source_question_id: sourceQuestionId,
            candidate: variant.candidate,
          });
        } else {
          saved = await saveGeneratedQuestion({
            source_question_id: sourceQuestionId,
            candidate: variant.candidate,
          });
        }

        savedResults.push({ variantId: variant.id, saved });
      }

      setVariants((currentVariants) =>
        currentVariants.map((variant) => {
          const savedResult = savedResults.find(
            (item) => item.variantId === variant.id
          );

          if (!savedResult) {
            return variant;
          }

          return {
            ...variant,
            selected: false,
            savedQuestionId: savedResult.saved.question_id,
            embeddingStatus: savedResult.saved.embedding_status,
          };
        })
      );

      setSaveMessage(
        `Đã lưu ${savedResults.length} biến thể vào corpus`
      );
    } catch (requestError) {
      const preSaveQuality = requestError.detail?.quality_report;

      if (preSaveQuality && savingVariantId) {
        setVariants((currentVariants) =>
          currentVariants.map((variant) => {
            if (variant.id !== savingVariantId) {
              return variant;
            }

            return {
              ...variant,
              previewQuality: variant.previewQuality ?? variant.quality,
              preSaveQuality,
              quality: preSaveQuality,
              canSave: preSaveQuality.can_save,
              qaScore: getQualityScore(preSaveQuality),
            };
          })
        );
      }

      setGenerationError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const handleCopy = (id) => {
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  useEffect(() => {
    let cancelled = false;

    async function loadSolvers() {
      setSolverError(null);

      try {
        const data = await listSymbolicMCQSolvers();
        const nextSolvers = (Array.isArray(data.solvers) ? data.solvers : [])
          .filter((solver) => {
            const hint = solver.taxonomy_hint || "";
            return hint.startsWith("calculus.");
          });

        if (!cancelled) {
          setSolvers(nextSolvers);
          setSelectedSolverCode((current) =>
            current || nextSolvers[0]?.code || ""
          );
        }
      } catch (requestError) {
        if (!cancelled) {
          setSolverError(requestError.message);
        }
      }
    }

    loadSolvers();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!sourceQuestionId) {
      queueMicrotask(() => {
        setSourceQuestion(null);
        setSourceLoading(false);
        setSourceError(null);
        setVariants([]);
        setGenerationError(null);
        setSaveMessage(null);
      });
      return;
    }

    let cancelled = false;

    async function loadSourceQuestion() {
      setSourceQuestion(null);
      setSourceLoading(true);
      setSourceError(null);
      if (
        !generationSession ||
        generationSession.sourceQuestionId !== sourceQuestionId
      ) {
        setVariants([]);
      }
      setGenerationError(null);
      setSaveMessage(null);

      try {
        const data = await getQuestion(sourceQuestionId);

        if (!cancelled) {
          setSourceQuestion(data);
        }
      } catch (requestError) {
        if (!cancelled) {
          setSourceError(requestError.message);
          setSourceQuestion(null);
        }
      } finally {
        if (!cancelled) {
          setSourceLoading(false);
        }
      }
    }

    loadSourceQuestion();

    return () => {
      cancelled = true;
    };
  }, [generationSession, sourceQuestionId]);

  const displayOriginal = sourceQuestion
    ? {
        id: sourceQuestion.id,
        latex: sourceQuestion.formulas?.[0]?.latex || sourceQuestion.marker || "Question",
        topic: sourceQuestion.chapter || sourceQuestion.subject || "Chưa phân loại",
        difficulty: sourceQuestion.difficulty || "Chưa rõ",
        statement: sourceQuestion.statement,
      }
    : null;

  const hasLoadedSource = Boolean(
    sourceQuestion &&
    sourceQuestion.id === sourceQuestionId &&
    !sourceLoading &&
    !sourceError,
  );

  const sourceBreadcrumb = hasLoadedSource
    ? sourceQuestion.id
    : sourceLoading
      ? "Đang tải bài gốc..."
      : sourceError
        ? "Không tải được bài gốc"
        : "Chưa chọn bài gốc";

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
          {filterNavigationItems(NAV, currentUser?.role).map((item) => {
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
          <UserMenu currentUser={currentUser} onLogout={onLogout} />
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
              <span>{sourceBreadcrumb}</span>
              <ChevronRight size={11} />
              <span className="text-slate-600 font-semibold">Sinh biến thể</span>
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

                {!sourceQuestionId && (
                  <p className="text-[10px] text-amber-600 leading-relaxed">
                    Chưa chọn câu hỏi nguồn. Hãy chọn một câu hỏi từ Semantic Search hoặc Chi tiết bài tập.
                  </p>
                )}

                {sourceQuestionId && sourceLoading && (
                  <p className="text-[10px] text-blue-600">
                    Đang tải câu hỏi nguồn...
                  </p>
                )}

                {sourceQuestionId && !sourceLoading && sourceError && (
                  <p className="text-[10px] text-red-600 leading-relaxed">
                    Không thể tải câu hỏi nguồn: {sourceError}
                  </p>
                )}

                {hasLoadedSource && (
                  <>
                    <p className="text-[10px] text-blue-600 font-mono break-all mb-2">
                      {displayOriginal.id}
                    </p>
                    <div className="text-[13px] text-blue-800 font-bold block mb-1">
                      <LatexInline value={displayOriginal.latex} />
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                        {displayOriginal.topic}
                      </span>
                      <span className="text-[10px] text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
                        {displayOriginal.difficulty}
                      </span>
                    </div>
                  </>
                )}
              </div>

              {/* Form fields */}
              <div className="space-y-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">
                    Chế độ sinh trắc nghiệm
                  </label>
                  <div className="grid grid-cols-1 gap-1.5">
                    {GENERATION_MODES.map((mode) => (
                      <button
                        key={mode.id}
                        type="button"
                        onClick={() => setGenerationMode(mode.id)}
                        className={`flex items-center justify-between px-2.5 py-2 text-[11px] font-semibold rounded-lg border transition-all ${
                          generationMode === mode.id
                            ? "border-blue-300 bg-blue-50 text-blue-700"
                            : "border-slate-200 bg-white text-slate-600 hover:border-blue-200"
                        }`}
                      >
                        <span>{mode.label}</span>
                        {generationMode === mode.id && (
                          <CheckCircle size={12} className="text-blue-600" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {generationMode === "symbolic" && (
                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1.5">
                      Bộ giải toán giải tích 1
                    </label>
                    <select
                      value={selectedSolverCode}
                      onChange={(e) => setSelectedSolverCode(e.target.value)}
                      className="w-full px-2.5 py-2 border border-slate-200 rounded-lg text-[11px] bg-slate-50 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400"
                    >
                      {solvers.length === 0 ? (
                        <option value="">Chưa có bộ giải toán</option>
                      ) : (
                        solvers.map((solver) => (
                          <option key={solver.code} value={solver.code}>
                            {getSolverLabel(solver)}
                          </option>
                        ))
                      )}
                    </select>
                    {solverError && (
                      <p className="mt-1 text-[10px] text-red-600">
                        {solverError}
                      </p>
                    )}
                  </div>
                )}

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
                    {["1", "3", "5"].map((n) => (
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

              <button
                type="button"
                onClick={handleGen}
                disabled={!hasLoadedSource || generating}
                className={`w-full mt-3 flex items-center justify-center gap-2 py-2.5 text-[12px] font-bold rounded-xl transition-all ${
                  !hasLoadedSource || generating
                    ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                {generating ? <RefreshCw size={13} className="animate-spin" /> : <Sparkles size={13} />}
                {generating ? "Đang sinh..." : "Sinh câu hỏi trắc nghiệm"}
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
                {checkingQuality && (
                  <span className="text-[10px] bg-amber-100 text-amber-700 font-semibold px-2 py-0.5 rounded-full">
                    Đang kiểm định
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {hasLoadedSource && selectedCount > 0 && (
                  <>
                    <button className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-all">
                      <Download size={12} /> Xuất LaTeX ({selectedCount})
                    </button>
                    <button
                      type="button"
                      onClick={handleSaveSelected}
                      disabled={saving || checkingQuality}
                      className={`flex items-center gap-1.5 text-[11px] font-semibold border px-3 py-1.5 rounded-lg transition-all ${
                        saving || checkingQuality
                          ? "text-slate-400 bg-slate-100 border-slate-200 cursor-not-allowed"
                          : "text-emerald-600 bg-emerald-50 border-emerald-200 hover:bg-emerald-100"
                      }`}
                    >
                      {saving ? <RefreshCw size={12} className="animate-spin" /> : <DatabaseZap size={12} />}
                      {saving ? "Đang lưu..." : "Thêm vào corpus"}
                    </button>
                  </>
                )}
              </div>
            </div>

            {generationError && (
              <div className="mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-[11px] text-red-600">
                {generationError}
              </div>
            )}

            {saveMessage && (
              <div className="mb-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-[11px] text-emerald-700">
                {saveMessage}
              </div>
            )}

            {!hasLoadedSource ? (
              <div className="bg-white border border-dashed border-slate-200 rounded-xl p-8 text-center">
                <Sparkles size={24} className="text-slate-300 mx-auto mb-3" />
                <p className="text-[13px] font-bold text-slate-700">
                  {sourceLoading
                    ? "Đang tải câu hỏi nguồn"
                    : sourceError
                      ? "Không thể tải câu hỏi nguồn"
                      : "Hãy chọn một câu hỏi nguồn để sinh biến thể"}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  {sourceError
                    ? "Hãy quay lại Semantic Search hoặc Chi tiết bài tập để chọn một bài hợp lệ."
                    : "Vào Semantic Search hoặc Chi tiết bài tập, sau đó bấm Sinh biến thể."}
                </p>
              </div>
            ) : variants.length === 0 ? (
              <div className="bg-white border border-dashed border-slate-200 rounded-xl p-8 text-center">
                <Sparkles size={24} className="text-blue-300 mx-auto mb-3" />
                <p className="text-[13px] font-bold text-slate-700">
                  Chưa có biến thể nào
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Bấm Sinh biến thể để tạo kết quả từ câu hỏi nguồn hiện tại.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {variants.map((v) => {
                const DiffIcon = v.diffIcon;
                const isSelected = v.selected;
                const validationReport = v.validationReport || {};
                const warnings = validationReport.warnings || [];
                const blockingIssues = validationReport.blocking_issues || [];
                const symbolicChecks = validationReport.symbolic_checks || [];
                const validationCanSave =
                  validationReport.can_save !== false && v.canSave !== false;
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
                        <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-full">
                          {getGenerationMethodLabel(v.generationMethod || v.mode)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <span className="text-[10px] text-slate-400">Kiểm định:</span>
                          <span className={`text-[11px] font-bold ${v.qaScore >= 96 ? "text-emerald-600" : "text-amber-600"}`}>{v.qaScore}%</span>
                          <div className="w-10 h-1 rounded-full bg-slate-100 overflow-hidden">
                            <div className={`h-full rounded-full ${v.qaScore >= 96 ? "bg-emerald-500" : "bg-amber-400"}`} style={{ width: `${v.qaScore}%` }} />
                          </div>
                        </div>

                        {v.quality && (
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                            v.canSave
                              ? "text-emerald-700 bg-emerald-50 border-emerald-200"
                              : "text-red-700 bg-red-50 border-red-200"
                          }`}>
                            {v.canSave ? "Có thể lưu" : "Không thể lưu"}
                          </span>
                        )}

                        <button onClick={() => handleCopy(v.id)}
                          className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
                          {copiedId === v.id ? <CheckCircle size={12} className="text-emerald-500" /> : <Copy size={12} />}
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            onOpenQualityContext({
                              origin: "gen",
                              sourceQuestionId,
                              variantId: v.id,
                              candidate: v.candidate,
                              quality: v.quality,
                              previewQuality: v.previewQuality ?? v.quality,
                              preSaveQuality: v.preSaveQuality ?? null,
                              generationSession: {
                                sourceQuestionId,
                                variants,
                                generationMode,
                                selectedSolverCode,
                                strategy,
                                count,
                                targetDiff,
                                note,
                              },
                            })
                          }
                          disabled={!v.quality}
                          className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          <Eye size={12} />
                        </button>
                      </div>
                    </div>
                    <div className="px-4 py-3">
                      <div className="flex items-center gap-3 mb-2.5">
                        <div className="w-5 h-5 rounded bg-purple-600 flex items-center justify-center flex-shrink-0">
                          <span className="text-white font-bold" style={{ fontSize: 9 }}>∫</span>
                        </div>
                        <div className="text-[13px] text-purple-700 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-100 font-bold">
                          <LatexInline value={v.latex} />
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed mb-2">
                        <MathText value={v.statement} />
                      </p>

                      {v.choices?.length > 0 && (
                        <div className="mb-2 grid grid-cols-1 gap-1.5">
                          {v.choices.map((choice, choiceIndex) => {
                            const choiceKey =
                              getChoiceValue(choice, "key") ||
                              String.fromCharCode(65 + choiceIndex);
                            const isCorrect =
                              choiceKey === v.correctChoice ||
                              getChoiceValue(choice, "is_correct") === true;

                            return (
                              <div
                                key={`${v.id}-${choiceKey}`}
                                className={`flex items-start gap-2 rounded-lg border px-2.5 py-1.5 ${
                                  isCorrect
                                    ? "border-emerald-200 bg-emerald-50"
                                    : "border-slate-100 bg-slate-50"
                                }`}
                              >
                                <span
                                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                                    isCorrect
                                      ? "bg-emerald-600 text-white"
                                      : "bg-white text-slate-500 border border-slate-200"
                                  }`}
                                >
                                  {choiceKey}
                                </span>
                                <span className="min-w-0 text-[11px] leading-relaxed text-slate-700">
                                  <MathText value={getChoiceDisplayText(choice)} />
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      <div className="mb-2 flex flex-wrap items-center gap-1.5">
                        {v.correctChoice && (
                          <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded">
                            Đáp án đúng: {v.correctChoice}
                          </span>
                        )}
                        <span
                          className={`text-[10px] font-semibold border px-2 py-0.5 rounded ${
                            validationCanSave
                              ? "text-emerald-700 bg-emerald-50 border-emerald-100"
                              : "text-red-700 bg-red-50 border-red-100"
                          }`}
                        >
                          Kiểm định: {validationCanSave ? "Đạt" : "Không thể lưu"}
                        </span>
                        {v.solverCode && (
                          <span className="text-[10px] font-semibold text-violet-700 bg-violet-50 border border-violet-100 px-2 py-0.5 rounded">
                            Bộ giải: {getSolverLabel(v.solverCode)}
                          </span>
                        )}
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded">
                          Cách sinh: {getGenerationMethodLabel(v.generationMethod || v.mode || "ai")}
                        </span>
                      </div>

                      {(blockingIssues.length > 0 || warnings.length > 0) && (
                        <div className="mb-2 space-y-1">
                          {blockingIssues.map((issue, issueIndex) => (
                            <div
                              key={`block-${v.id}-${issueIndex}`}
                              className="rounded-lg border border-red-100 bg-red-50 px-2.5 py-1 text-[10px] text-red-700"
                            >
                              Lỗi: {getIssueCode(issue)}
                            </div>
                          ))}
                          {warnings.map((issue, issueIndex) => (
                            <div
                              key={`warn-${v.id}-${issueIndex}`}
                              className="rounded-lg border border-amber-100 bg-amber-50 px-2.5 py-1 text-[10px] text-amber-700"
                            >
                              Cảnh báo: {getIssueCode(issue)}
                            </div>
                          ))}
                        </div>
                      )}

                      {symbolicChecks.length > 0 && (
                        <div className="mb-2 flex flex-wrap gap-1">
                          {symbolicChecks.map((check, checkIndex) => (
                            <span
                              key={`symbolic-${v.id}-${checkIndex}`}
                              className="text-[10px] font-semibold text-blue-700 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded"
                            >
                              {getIssueCode(check)}
                            </span>
                          ))}
                        </div>
                      )}

                      {v.savedQuestionId && (
                        <div className="mb-2 rounded-lg border border-emerald-100 bg-emerald-50 px-2.5 py-1.5 text-[10px] text-emerald-700">
                          Đã lưu: <span className="font-mono">{v.savedQuestionId}</span>
                          {v.embeddingStatus && (
                            <span className="ml-2 text-emerald-600">
                              Trạng thái embedding: {v.embeddingStatus}
                            </span>
                          )}
                        </div>
                      )}
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-400">Chiến lược:</span>
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">{v.strategy}</span>
                      </div>
                    </div>
                  </div>
                    );
                })}
                </div>
              )}

            {/* AI Explanation */}
            {variants.length > 0 && (
              <div className="mt-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={13} className="text-blue-400" />
                  <span className="text-[11px] font-bold text-blue-300">Giải thích từ AI</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                  {variants.length} biến thể được sinh từ câu hỏi nguồn hiện tại. Các cảnh báo trong từng card lấy từ bước preview của backend; bước tiếp theo sẽ chạy kiểm định chất lượng chi tiết trước khi lưu vào corpus.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
