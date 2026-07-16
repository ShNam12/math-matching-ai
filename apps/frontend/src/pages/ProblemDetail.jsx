import { useEffect, useRef, useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  ArrowLeft, Copy, Share2, Star, GitBranch,
  Zap, ChevronRight, CheckCircle, BookMarked,
  TrendingUp, Tag, Clock, User, Printer, Download, LayoutDashboard
} from "lucide-react";
import {
  classifyQuestion,
  getQuestion,
  getQuestionTaxonomyQuality,
  updateQuestion,
} from "../services/questionApi";
import { searchQuestions } from "../services/searchApi";
import {
  getRecentQuestionIds,
  rememberRecentQuestion,
} from "../services/recentQuestions";
import { filterNavigationItems } from "../auth/navigation";
import LatexInline from "../components/LatexInline";
import MathText from "../components/MathText";
import UserMenu from "../components/UserMenu";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa" },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail", active: true },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

function getChoiceValue(choice, field) {
  if (!choice || typeof choice !== "object") return null;
  return choice[field] ?? null;
}

function formatQuestionType(questionType) {
  if (questionType === "multiple_choice") return "Trắc nghiệm";
  return "Tự luận";
}

function getValidationReport(question) {
  return question?.validation_report || {
    can_save: true,
    warnings: [],
    blocking_issues: [],
    symbolic_checks: [],
  };
}

function getIssueCode(issue) {
  return issue?.code || issue?.message || String(issue || "");
}

function getChoiceDisplayText(choice) {
  const text = getChoiceValue(choice, "text");
  const latex = getChoiceValue(choice, "latex");

  if (latex) return `$${latex}$`;
  if (text) return String(text);
  return "";
}

export default function ProblemDetail({
  activePage = "detail",
  onNavigate = () => {},
  currentUser = null,
  onLogout = () => {},
  selectedQuestionId = null,
  onOpenQuestionDetail = () => {},
  onOpenGeneration = () => {},
  onOpenQualityContext = () => {},
}) {
  const [starred, setStarred] = useState(true);
  const [copiedLatex, setCopiedLatex] = useState(false);

  const [question, setQuestion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recentQuestions, setRecentQuestions] = useState([]);
  const [recentLoading, setRecentLoading] = useState(false);

  const [metadataForm, setMetadataForm] = useState({
    subject: "",
    chapter: "",
    difficulty: "",
    skillsText: "",
  });

  const [metadataSaving, setMetadataSaving] = useState(false);
  const [metadataError, setMetadataError] = useState(null);
  const [metadataMessage, setMetadataMessage] = useState(null);

  const [classifying, setClassifying] = useState(false);
  const [classificationMessage, setClassificationMessage] = useState(null);
  const [classificationError, setClassificationError] = useState(null);
  const [taxonomyChecking, setTaxonomyChecking] = useState(false);
  const [taxonomyQualityError, setTaxonomyQualityError] = useState(null);

  const [similarQuestions, setSimilarQuestions] = useState([]);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [similarError, setSimilarError] = useState(null);
  const similarPanelRef = useRef(null);
  const isAdmin = currentUser?.role === "admin";

  const handleCopy = () => {
    setCopiedLatex(true);
    setTimeout(() => setCopiedLatex(false), 1500);
  };

  const handleMetadataChange = (field, value) => {
    setMetadataForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSaveMetadata = async () => {
    if (!question?.id) {
      return;
    }

    setMetadataSaving(true);
    setMetadataError(null);
    setMetadataMessage(null);

    const skills = metadataForm.skillsText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    try {
      const updatedQuestion = await updateQuestion(question.id, {
        subject: metadataForm.subject.trim() || null,
        chapter: metadataForm.chapter.trim() || null,
        difficulty: metadataForm.difficulty || null,
        skills,
      });

      setQuestion(updatedQuestion);
      setMetadataMessage("Đã cập nhật metadata.");
    } catch (requestError) {
      setMetadataError(requestError.message);
    } finally {
      setMetadataSaving(false);
    }
  };

  const handleClassifyQuestion = async () => {
    if (!question?.id || classifying) return;

    setClassifying(true);
    setClassificationMessage(null);
    setClassificationError(null);

    try {
      const updatedQuestion = await classifyQuestion(question.id);
      setQuestion(updatedQuestion);
      setClassificationMessage("Đã AI Matching lại câu hỏi.");
    } catch (requestError) {
      setClassificationError(requestError.message);
    } finally {
      setClassifying(false);
    }
  };

  const handleCheckTaxonomyQuality = async () => {
    if (!question?.id || taxonomyChecking) return;

    setTaxonomyChecking(true);
    setTaxonomyQualityError(null);

    try {
      const quality = await getQuestionTaxonomyQuality(question.id);

      onOpenQualityContext({
        type: "taxonomy",
        questionId: question.id,
        question,
        quality,
      });
    } catch (requestError) {
      setTaxonomyQualityError(requestError.message);
    } finally {
      setTaxonomyChecking(false);
    }
  };

  useEffect(() => {
    if (!selectedQuestionId) {
      queueMicrotask(() => {
        setQuestion(null);
        setLoading(false);
        setError(null);
      });
      return;
    }

    let cancelled = false;

    async function loadQuestion() {
      setLoading(true);
      setError(null);
      setQuestion(null);

      try {
        const data = await getQuestion(selectedQuestionId);

        if (!cancelled) {
          setQuestion(data);
          rememberRecentQuestion(data.id);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError.message);
          setQuestion(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadQuestion();

    return () => {
      cancelled = true;
    };
  }, [selectedQuestionId]);

  useEffect(() => {
    if (selectedQuestionId) {
      return undefined;
    }

    let cancelled = false;

    async function loadRecentQuestions() {
      const ids = getRecentQuestionIds();

      if (ids.length === 0) {
        setRecentQuestions([]);
        setRecentLoading(false);
        return;
      }

      setRecentLoading(true);

      const results = await Promise.allSettled(ids.map((id) => getQuestion(id)));

      if (!cancelled) {
        setRecentQuestions(
          results
            .filter((result) => result.status === "fulfilled")
            .map((result) => result.value),
        );
        setRecentLoading(false);
      }
    }

    loadRecentQuestions();

    return () => {
      cancelled = true;
    };
  }, [selectedQuestionId]);

  useEffect(() => {
    queueMicrotask(() => {
      if (!question) {
        setMetadataForm({
          subject: "",
          chapter: "",
          difficulty: "",
          skillsText: "",
        });
        return;
      }

      setMetadataForm({
        subject: question.subject || "",
        chapter: question.chapter || "",
        difficulty: question.difficulty || "",
        skillsText: Array.isArray(question.skills) ? question.skills.join(", ") : "",
      });
    });
  }, [question]);

  useEffect(() => {
    if (!question?.statement) {
      queueMicrotask(() => {
        setSimilarQuestions([]);
      });
      return;
    }

    let cancelled = false;

    async function loadSimilarQuestions() {
      setSimilarLoading(true);
      setSimilarError(null);

      try {
        const data = await searchQuestions({
          query: question.statement,
          limit: 6,
        });

        if (!cancelled) {
          setSimilarQuestions(
            data.results
              .filter((item) => item.question_id !== question.id)
              .slice(0, 3),
          );
        }
      } catch (requestError) {
        if (!cancelled) {
          setSimilarError(requestError.message);
          setSimilarQuestions([]);
        }
      } finally {
        if (!cancelled) {
          setSimilarLoading(false);
        }
      }
    }

    loadSimilarQuestions();

    return () => {
      cancelled = true;
    };
  }, [question]);

  const displayProblem = question
    ? {
        id: question.id,
        topic: question.topic_name || question.subject || "Chưa phân loại",
        subtopic: question.problem_type_name || question.chapter_name || "Chưa có dạng bài",
        chapter: question.chapter_name || `Câu ${question.sequence_number}`,
        difficulty: question.difficulty || "Chưa rõ",
        skill: question.skills?.[0] || "Chưa gán kỹ năng",
        source: question.document_id,
        addedBy: "Backend",
        addedDate: new Date(question.created_at).toLocaleDateString("vi-VN"),
        latex: question.formulas?.[0]?.latex || question.marker || "Question",
        statement: question.statement,
        tags: question.skills?.length ? question.skills : ["Backend"],
        similarCount: similarQuestions.length,
        variantCount: 0,
        solution: question.solution,
        answer: question.answer,
        formulas: question.formulas || [],
        embeddingStatus: question.embedding_status,
        questionType: question.question_type || "free_response",
        choices: Array.isArray(question.choices) ? question.choices : [],
        correctChoice: question.correct_choice || null,
        validationReport: getValidationReport(question),
        generationMethod: question.generation_method,
        solverCode: question.solver_code,

        classificationStatus: question.classification_status,
        confidence: question.taxonomy_confidence,
        reason: question.taxonomy_reason,
        reviewStatus: question.review_status,
        chapterCode: question.chapter_code,
        topicCode: question.topic_code,
        problemTypeCode: question.problem_type_code,

      }
    : null;

  const isMultipleChoice = displayProblem?.questionType === "multiple_choice";
  const validationReport = displayProblem?.validationReport || getValidationReport(null);
  const validationWarnings = Array.isArray(validationReport.warnings)
    ? validationReport.warnings
    : [];
  const validationBlockingIssues = Array.isArray(validationReport.blocking_issues)
    ? validationReport.blocking_issues
    : [];
  const symbolicChecks = Array.isArray(validationReport.symbolic_checks)
    ? validationReport.symbolic_checks
    : [];

  const solutionBlocks = question
    ? [
        question.solution && {
          num: 1,
          title: "Lời giải",
          content: question.solution,
          latex: question.answer || "",
        },
        question.answer && {
          num: 2,
          title: "Đáp án",
          content: question.answer,
          latex: "",
        },
      ].filter(Boolean)
    : [];

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
        {/* Header */}
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => onNavigate("search")}
              className="flex items-center gap-1.5 text-[11px] text-blue-600 hover:text-blue-800 font-semibold bg-blue-50 px-2.5 py-1.5 rounded-lg transition-all"
            >
              {selectedQuestionId ? <ArrowLeft size={12} /> : <Search size={12} />}
              {selectedQuestionId ? "Quay lại kết quả" : "Tìm bài tập"}
            </button>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              {question ? (
                <>
                  <span>Semantic Search</span>
                  <ChevronRight size={11} />
                  <span className="font-mono font-semibold text-slate-600">
                    {displayProblem.id}
                  </span>
                </>
              ) : (
                <span className="font-semibold text-slate-500">Chưa chọn bài tập</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            {question && (
              <>
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
              </>
            )}
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400 ml-1">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold ml-1">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-5 flex gap-5">
          {!selectedQuestionId && (
            <section className="flex-1 w-full max-w-5xl mx-auto py-10">
              <div className="rounded-2xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                  <FileText size={27} />
                </div>
                <h1 className="mt-5 text-xl font-bold text-slate-800">Chưa chọn bài tập</h1>
                <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                  Chọn một bài từ Semantic Search để xem đề bài, lời giải chi tiết
                  và các thông tin liên quan.
                </p>
                <button
                  type="button"
                  onClick={() => onNavigate("search")}
                  className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
                >
                  <Search size={15} />
                  Tìm bài tập
                </button>
              </div>

              <div className="mt-6">
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="text-sm font-bold text-slate-700">Bài tập đã xem gần đây</h2>
                  <span className="text-xs text-slate-400">Tối đa 5 bài</span>
                </div>

                {recentLoading && (
                  <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
                    Đang tải bài tập gần đây...
                  </div>
                )}

                {!recentLoading && recentQuestions.length === 0 && (
                  <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
                    Bạn chưa xem bài tập nào. Hãy bắt đầu từ Semantic Search.
                  </div>
                )}

                {!recentLoading && recentQuestions.length > 0 && (
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {recentQuestions.map((recent) => (
                      <button
                        key={recent.id}
                        type="button"
                        onClick={() => onOpenQuestionDetail(recent.id)}
                        className="rounded-xl border border-slate-200 bg-white p-4 text-left transition-all hover:border-blue-300 hover:shadow-sm"
                      >
                        <p className="font-mono text-xs font-bold text-blue-600">{recent.id}</p>
                        <div className="mt-2 h-11 overflow-hidden text-sm leading-5 text-slate-700">
                          <MathText value={recent.statement || "Không có nội dung đề bài."} />
                        </div>
                        <div className="mt-3 flex items-center gap-2">
                          <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-500">
                            {recent.difficulty || "Chưa rõ độ khó"}
                          </span>
                          <span className="truncate text-[10px] text-slate-400">
                            {recent.skills?.[0] || "Chưa gắn kỹ năng"}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </section>
          )}

          {selectedQuestionId && (
            <>
              {loading && (
                <div className="absolute inset-x-0 top-16 mx-auto w-fit rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-[12px] font-semibold text-blue-700">
                  Đang tải chi tiết câu hỏi...
                </div>
              )}

              {error && (
                <div className="absolute inset-x-0 top-16 mx-auto w-fit rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] font-semibold text-red-700">
                  {error}
                </div>
              )}

              {question && (
                <>
          {/* Left — problem + solution */}
          <div className="flex-1 min-w-0 space-y-4">
            {/* Hero card */}
            <div className="bg-blue-600 rounded-2xl p-5 text-white">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[10px] font-bold bg-white/20 px-2.5 py-0.5 rounded-full">{displayProblem.chapter}</span>
                <ChevronRight size={11} className="opacity-60" />
                <span className="text-[11px] opacity-80">{displayProblem.topic}</span>
                <ChevronRight size={11} className="opacity-60" />
                <span className="text-[11px] opacity-80">{displayProblem.subtopic}</span>
              </div>
              <div className="bg-white/15 rounded-xl px-4 py-3 mb-3 font-mono text-[15px] font-bold flex items-center gap-3">
                <span className="text-2xl opacity-70">∫</span>
                <LatexInline value={displayProblem.latex} />
                <button onClick={handleCopy} className="ml-auto text-white/60 hover:text-white transition-colors">
                  {copiedLatex ? <CheckCircle size={14} /> : <Copy size={14} />}
                </button>
              </div>
              <p className="text-[12px] leading-relaxed text-white/90">
                <MathText value={displayProblem.statement} />
              </p>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-[10px] font-semibold bg-white/15 border border-white/20 text-white px-2.5 py-1 rounded-full">
                  {formatQuestionType(displayProblem.questionType)}
                </span>
                <span className="text-[10px] font-semibold bg-red-400/30 border border-red-300/30 text-white px-2.5 py-1 rounded-full">{displayProblem.difficulty}</span>
                <span className="text-[10px] font-semibold bg-white/15 border border-white/20 text-white px-2.5 py-1 rounded-full">{displayProblem.skill}</span>
                {displayProblem.tags.map((t) => (
                  <span key={t} className="text-[10px] bg-white/10 text-white/80 px-2.5 py-1 rounded-full">{t}</span>
                ))}
              </div>
            </div>

            {isMultipleChoice && (
              <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden">
                <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <CheckSquare size={14} className="text-blue-600" />
                    <span className="text-[12px] font-bold text-slate-700">Lua chon dap an</span>
                  </div>
                  {displayProblem.correctChoice && (
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
                      Dap an dung: {displayProblem.correctChoice}
                    </span>
                  )}
                </div>
                <div className="p-4 grid grid-cols-1 gap-2">
                  {displayProblem.choices.length === 0 && (
                    <div className="rounded-xl border border-amber-100 bg-amber-50 px-3 py-2 text-[11px] text-amber-700">
                      Chua co lua chon A/B/C/D.
                    </div>
                  )}

                  {displayProblem.choices.map((choice, index) => {
                    const key = getChoiceValue(choice, "key") || "?";
                    const isCorrect =
                      getChoiceValue(choice, "is_correct") === true ||
                      key === displayProblem.correctChoice;
                    const rationale = getChoiceValue(choice, "rationale");

                    return (
                      <div
                        key={`${key}-${index}`}
                        className={`rounded-xl border px-3 py-2.5 ${
                          isCorrect
                            ? "border-emerald-200 bg-emerald-50"
                            : "border-slate-100 bg-slate-50"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-[12px] font-bold flex-shrink-0 ${
                            isCorrect
                              ? "bg-emerald-600 text-white"
                              : "bg-white text-slate-600 border border-slate-200"
                          }`}>
                            {key}
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className={`text-[12px] leading-relaxed ${
                              isCorrect ? "text-emerald-800" : "text-slate-700"
                            }`}>
                              <MathText value={getChoiceDisplayText(choice)} />
                            </p>
                            {rationale && (
                              <p className="mt-1 text-[10px] text-slate-500 leading-relaxed">
                                {rationale}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Solution */}
            <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100 flex items-center gap-2">
                <BookMarked size={14} className="text-blue-600" />
                <span className="text-[12px] font-bold text-slate-700">Lời giải từng bước</span>
                <span className="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full ml-1">{solutionBlocks.length} bước</span>
              </div>
              <div className="divide-y divide-slate-50">
                {solutionBlocks.map((step) => (
                  <div key={step.num} className="px-5 py-4 flex gap-4">
                    <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0 mt-0.5">
                      {step.num}
                    </div>
                    <div className="flex-1">
                      <p className="text-[12px] font-bold text-slate-700 mb-1">{step.title}</p>
                      <p className="text-[11px] text-slate-500 leading-relaxed mb-2">
                        <MathText value={step.content} />
                      </p>
                      {step.latex && (
                        <div className="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
                          <code className="text-[11px] font-mono text-blue-800 break-all leading-relaxed">
                            <LatexInline value={step.latex} />
                          </code>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button
                type="button"
                disabled={!displayProblem.id || !isAdmin}
                onClick={() => onOpenGeneration(displayProblem.id)}
                className={`flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-xl hover:bg-blue-700 transition-all disabled:opacity-60 ${isAdmin ? "" : "hidden"}`}
              >
                <Zap size={13} /> Sinh biến thể từ bài này
              </button>
              <button
                type="button"
                onClick={() => similarPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
                className="flex items-center gap-2 px-4 py-2.5 text-blue-600 bg-blue-50 border border-blue-200 text-[12px] font-semibold rounded-xl hover:bg-blue-100 transition-all"
              >
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
                { icon: Tag, label: "Mã bài", val: displayProblem.id },
                { icon: BookOpen, label: "Nguồn", val: displayProblem.source },
                { icon: TrendingUp, label: "Độ khó", val: displayProblem.difficulty },
                { icon: CheckCircle, label: "Kỹ năng", val: displayProblem.skill },
                { icon: User, label: "Thêm bởi", val: displayProblem.addedBy },
                { icon: Clock, label: "Ngày thêm", val: displayProblem.addedDate },
              ].map((row) => (
                <div key={row.label} className="flex items-start gap-2 py-1.5 border-b border-slate-50 last:border-0">
                  <row.icon size={11} className="text-slate-400 mt-0.5 flex-shrink-0" />
                  <span className="text-[10px] text-slate-400 flex-shrink-0 w-16">{row.label}</span>
                  <span className="text-[11px] font-semibold text-slate-700 truncate">{row.val}</span>
                </div>
              ))}

              {question && (
                <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700">
                    MCQ & Validation
                  </p>

                  <div className="space-y-1.5 text-[11px]">
                    <p className="text-slate-500">
                      Loai cau hoi:{" "}
                      <span className="font-semibold text-slate-700">
                        {formatQuestionType(displayProblem.questionType)}
                      </span>
                    </p>

                    {displayProblem.generationMethod && (
                      <p className="text-slate-500">
                        Generation:{" "}
                        <span className="font-semibold text-slate-700">
                          {displayProblem.generationMethod}
                        </span>
                      </p>
                    )}

                    {displayProblem.solverCode && (
                      <p className="text-slate-500">
                        Solver:{" "}
                        <span className="font-semibold text-slate-700">
                          {displayProblem.solverCode}
                        </span>
                      </p>
                    )}

                    {isMultipleChoice && (
                      <p className="text-slate-500">
                        Dap an dung:{" "}
                        <span className="font-semibold text-emerald-700">
                          {displayProblem.correctChoice || "Chua co"}
                        </span>
                      </p>
                    )}

                    <p className="text-slate-500">
                      Trang thai luu:{" "}
                      <span className={`font-semibold ${
                        validationReport.can_save === false
                          ? "text-red-700"
                          : "text-emerald-700"
                      }`}>
                        {validationReport.can_save === false
                          ? "Khong the luu"
                          : "Co the luu"}
                      </span>
                    </p>
                  </div>

                  {validationBlockingIssues.length > 0 && (
                    <div className="rounded-lg border border-red-100 bg-red-50 px-2.5 py-2">
                      <p className="text-[10px] font-bold text-red-700 mb-1">
                        Blocking issues
                      </p>
                      <div className="space-y-1">
                        {validationBlockingIssues.map((issue, index) => (
                          <p key={`${getIssueCode(issue)}-${index}`} className="text-[10px] text-red-700">
                            {getIssueCode(issue)}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {validationWarnings.length > 0 && (
                    <div className="rounded-lg border border-amber-100 bg-amber-50 px-2.5 py-2">
                      <p className="text-[10px] font-bold text-amber-700 mb-1">
                        Warnings
                      </p>
                      <div className="space-y-1">
                        {validationWarnings.map((issue, index) => (
                          <p key={`${getIssueCode(issue)}-${index}`} className="text-[10px] text-amber-700">
                            {getIssueCode(issue)}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {symbolicChecks.length > 0 && (
                    <div className="rounded-lg border border-blue-100 bg-blue-50 px-2.5 py-2">
                      <p className="text-[10px] font-bold text-blue-700 mb-1">
                        Symbolic checks
                      </p>
                      <div className="space-y-1">
                        {symbolicChecks.map((check, index) => (
                          <p key={`${check?.code || "symbolic"}-${index}`} className="text-[10px] text-blue-700">
                            {check?.code || check?.message || "symbolic_check"}:{" "}
                            {check?.passed === false ? "failed" : "passed"}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {question && (
                <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700">
                    AI Matching
                  </p>

                  <div className="space-y-1.5 text-[11px]">
                    <p className="text-slate-500">
                      Chương:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.chapter_name || "Chưa phân loại"}
                      </span>
                    </p>

                    <p className="text-slate-500">
                      Chủ đề:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.topic_name || "Chưa phân loại"}
                      </span>
                    </p>

                    <p className="text-slate-500">
                      Dạng bài:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.problem_type_name || "Chưa phân loại"}
                      </span>
                    </p>

                    <p className="text-slate-500">
                      Độ tin cậy:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.taxonomy_confidence != null
                          ? `${Math.round(question.taxonomy_confidence * 100)}%`
                          : "Chưa có"}
                      </span>
                    </p>

                    <p className="text-slate-500">
                      Trạng thái:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.classification_status || "pending"}
                      </span>
                    </p>

                    <p className="text-slate-500 leading-relaxed">
                      Lý do:{" "}
                      <span className="font-semibold text-slate-700">
                        {question.taxonomy_reason || "Chưa có lý do phân loại"}
                      </span>
                    </p>
                  </div>

                  {classificationError && isAdmin && (
                    <p className="text-[10px] text-red-600">
                      {classificationError}
                    </p>
                  )}

                  {classificationMessage && isAdmin && (
                    <p className="text-[10px] text-emerald-600">
                      {classificationMessage}
                    </p>
                  )}

                  <button
                    type="button"
                    disabled={classifying || !question?.id || !isAdmin}
                    onClick={handleClassifyQuestion}
                    className={`w-full rounded-lg bg-emerald-600 px-3 py-2 text-[11px] font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 ${isAdmin ? "" : "hidden"}`}
                  >
                    {classifying ? "Đang AI Matching..." : "AI Matching lại"}
                  </button>

                  {taxonomyQualityError && isAdmin && (
                    <p className="text-[10px] text-red-600">
                      {taxonomyQualityError}
                    </p>
                  )}

                  <button
                    type="button"
                    disabled={taxonomyChecking || !question?.id || !isAdmin}
                    onClick={handleCheckTaxonomyQuality}
                    className={`w-full rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] font-semibold text-amber-700 hover:bg-amber-100 disabled:opacity-60 ${isAdmin ? "" : "hidden"}`}
                  >
                    {taxonomyChecking ? "Đang kiểm định..." : "Kiểm định taxonomy"}
                  </button>

                </div>
              )}

              {question && isAdmin && (
                <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700">
                    Sửa metadata
                  </p>

                  <input
                    value={metadataForm.subject}
                    onChange={(event) => handleMetadataChange("subject", event.target.value)}
                    placeholder="Subject, ví dụ: Calculus"
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-[11px] text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400"
                  />

                  <input
                    value={metadataForm.chapter}
                    onChange={(event) => handleMetadataChange("chapter", event.target.value)}
                    placeholder="Chapter, ví dụ: Dao ham"
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-[11px] text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400"
                  />

                  <select
                    value={metadataForm.difficulty}
                    onChange={(event) => handleMetadataChange("difficulty", event.target.value)}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-[11px] text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400"
                  >
                    <option value="">Chưa rõ</option>
                    <option value="easy">Dễ</option>
                    <option value="medium">Vừa</option>
                    <option value="hard">Khó</option>
                  </select>

                  <textarea
                    value={metadataForm.skillsText}
                    onChange={(event) => handleMetadataChange("skillsText", event.target.value)}
                    rows={2}
                    placeholder="Skills, cách nhau bằng dấu phẩy"
                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-[11px] text-slate-700 resize-none focus:outline-none focus:ring-1 focus:ring-blue-400"
                  />

                  {metadataError && (
                    <p className="text-[10px] text-red-600">{metadataError}</p>
                  )}

                  {metadataMessage && (
                    <p className="text-[10px] text-emerald-600">{metadataMessage}</p>
                  )}

                  <button
                    type="button"
                    onClick={handleSaveMetadata}
                    disabled={metadataSaving}
                    className="w-full rounded-lg bg-blue-600 px-3 py-2 text-[11px] font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                  >
                    {metadataSaving ? "Đang lưu..." : "Lưu metadata"}
                  </button>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Thống kê</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: "Bài tương tự", val: displayProblem.similarCount },
                  { label: "Biến thể đã sinh", val: displayProblem.variantCount },
                  { label: "Lượt xem", val: 0 },
                  { label: "Lần dùng đề", val: 0 },
                ].map((s) => (
                  <div key={s.label} className="bg-slate-50 rounded-lg p-2.5 text-center">
                    <p className="text-[15px] font-bold text-blue-700">{s.val}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">{s.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Similar problems */}
            <div ref={similarPanelRef} className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Bài tập tương tự</p>
                <div className="space-y-2">
                  {similarLoading && (
                    <div className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-[11px] text-slate-500">
                      Đang tìm bài tương tự...
                    </div>
                  )}

                  {!similarLoading && similarError && (
                    <div className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-[11px] text-red-600">
                      {similarError}
                    </div>
                  )}

                  {!similarLoading && !similarError && similarQuestions.length === 0 && (
                    <div className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-[11px] text-slate-500">
                      Chưa có bài tương tự.
                    </div>
                  )}

                  {!similarLoading &&
                    !similarError &&
                    similarQuestions.map((s) => (
                      <button
                        key={s.question_id}
                        type="button"
                        onClick={() => onOpenQuestionDetail(s.question_id)}
                        className="w-full flex items-center gap-2 p-2.5 border border-slate-100 rounded-lg hover:border-blue-200 cursor-pointer transition-all group text-left"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] font-bold text-slate-500 font-mono truncate">
                            {s.question_id}
                          </p>
                          <code className="text-[10px] font-mono text-blue-700 truncate block mt-0.5">
                            {s.answer || s.marker || "Question"}
                          </code>
                        </div>
                        <div className="flex flex-col items-end gap-0.5">
                          <span className="text-[11px] font-bold text-indigo-700">
                            {Math.round(s.score * 100)}%
                          </span>
                          <div className="w-8 h-1 rounded-full bg-slate-100 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-indigo-500"
                              style={{ width: `${Math.round(s.score * 100)}%` }}
                            />
                          </div>
                        </div>
                      </button>
                    ))}

                  <button className="w-full text-[11px] text-blue-500 hover:text-blue-700 font-medium py-1 transition-colors">
                    Xem tất cả {displayProblem.similarCount} bài →
                  </button>
                </div>
            </div>
          </div>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
