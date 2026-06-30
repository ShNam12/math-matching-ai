import { useEffect, useState } from "react"
import Dashboard from "./pages/Dashboard.jsx"
import UploadDocument from "./pages/UploadDocument.jsx"
import SemanticSearch from "./pages/SemanticSearch.jsx"
import CalculusTaxonomy from "./pages/CalculusTaxonomy.jsx"
import QARules from "./pages/QARules.jsx"
import ProblemDetail from "./pages/ProblemDetail.jsx"
import GenVariants from "./pages/GenVariants.jsx"
import Analytics from "./pages/Analytics.jsx"
import SettingsPage from "./pages/SystemSettings.jsx"
import Login from "./pages/Login.jsx"
import { canAccessPage } from "./auth/navigation"
import {
  clearStoredAuthSession,
  getStoredAuthSession,
  storeAuthSession,
} from "./auth/session"
import { getCurrentUser } from "./services/authApi"
import "./App.css"

const PAGES = {
  dashboard: Dashboard,
  upload: UploadDocument,
  search: SemanticSearch,
  taxonomy: CalculusTaxonomy,
  qa: QARules,
  detail: ProblemDetail,
  gen: GenVariants,
  analytics: Analytics,
  settings: SettingsPage,
}

function App() {
  const [authSession, setAuthSession] = useState(() => getStoredAuthSession())
  const [authChecking, setAuthChecking] = useState(Boolean(getStoredAuthSession()))
  const [activePage, setActivePage] = useState("dashboard")
  const [selectedQuestionId, setSelectedQuestionId] = useState(null)
  const [sourceQuestionId, setSourceQuestionId] = useState(null)
  const [selectedQualityContext, setSelectedQualityContext] = useState(null)
  const [initialSearchFilters, setInitialSearchFilters] = useState(null)

  const currentUser = authSession?.user ?? null
  const currentRole = currentUser?.role
  const accessToken = authSession?.accessToken
  const safeActivePage = canAccessPage(activePage, currentRole)
    ? activePage
    : "dashboard"
  const ActivePage = PAGES[safeActivePage]

  useEffect(() => {
    let cancelled = false

    async function verifyStoredSession() {
      if (!accessToken) {
        setAuthChecking(false)
        return
      }

      try {
        const user = await getCurrentUser()
        if (!cancelled) {
          const nextSession = {
            accessToken,
            user,
          }
          storeAuthSession(nextSession)
          setAuthSession(nextSession)
        }
      } catch {
        if (!cancelled) {
          clearStoredAuthSession()
          setAuthSession(null)
        }
      } finally {
        if (!cancelled) {
          setAuthChecking(false)
        }
      }
    }

    verifyStoredSession()

    return () => {
      cancelled = true
    }
  }, [accessToken])

  function handleOpenQuestionDetail(questionId) {
    setSelectedQuestionId(questionId)
    setActivePage("detail")
  }

  function handleOpenGeneration(questionId) {
    if (!canAccessPage("gen", currentRole)) {
      setActivePage("dashboard")
      return
    }

    setSourceQuestionId(questionId)
    setActivePage("gen")
  }

  function handleOpenQualityContext(context) {
    if (!canAccessPage("qa", currentRole)) {
      setActivePage("dashboard")
      return
    }

    setSelectedQualityContext(context)
    setActivePage("qa")
  }

  function handleOpenSearchWithFilters(filters) {
    setInitialSearchFilters(filters)
    setActivePage("search")
  }

  function handleLogin(session) {
    const nextSession = {
      accessToken: session.access_token,
      user: session.user,
    }
    storeAuthSession(nextSession)
    setAuthSession(nextSession)
    setActivePage("dashboard")
  }

  function handleLogout() {
    clearStoredAuthSession()
    setAuthSession(null)
    setActivePage("dashboard")
    setSelectedQuestionId(null)
    setSourceQuestionId(null)
    setSelectedQualityContext(null)
    setInitialSearchFilters(null)
  }

  function handleNavigate(pageId) {
    if (!canAccessPage(pageId, currentRole)) {
      setActivePage("dashboard")
      return
    }

    setActivePage(pageId)
  }

  if (authChecking) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center text-sm text-slate-500">
        Dang kiem tra phien dang nhap
      </div>
    )
  }

  if (!authSession) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <ActivePage
      activePage={safeActivePage}
      onNavigate={handleNavigate}
      currentUser={currentUser}
      onLogout={handleLogout}
      selectedQuestionId={selectedQuestionId}
      sourceQuestionId={sourceQuestionId}
      selectedQualityContext={selectedQualityContext}
      initialSearchFilters={initialSearchFilters}
      onOpenQuestionDetail={handleOpenQuestionDetail}
      onOpenGeneration={handleOpenGeneration}
      onOpenQualityContext={handleOpenQualityContext}
      onOpenSearchWithFilters={handleOpenSearchWithFilters}
    />
  )
}

export default App
