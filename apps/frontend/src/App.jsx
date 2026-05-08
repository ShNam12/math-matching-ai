import { useState } from "react"
import Dashboard from "./pages/Dashboard.jsx"
import UploadDocument from "./pages/UploadDocument.jsx"
import SemanticSearch from "./pages/SemanticSearch.jsx"
import CalculusTaxonomy from "./pages/CalculusTaxonomy.jsx"
import QARules from "./pages/QARules.jsx"
import ProblemDetail from "./pages/ProblemDetail.jsx"
import GenVariants from "./pages/GenVariants.jsx"
import Analytics from "./pages/Analytics.jsx"
import SettingsPage from "./pages/Settings.jsx"
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
  const [activePage, setActivePage] = useState("dashboard")

  const ActivePage = PAGES[activePage]

  return (
    <ActivePage
      activePage={activePage}
      onNavigate={setActivePage}
    />
  )
}

export default App
