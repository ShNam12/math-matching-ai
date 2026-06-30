import { useEffect, useRef, useState } from "react";
import { LogOut } from "lucide-react";

function formatRole(role) {
  if (role === "admin") return "Administrator";
  if (role === "user") return "User";
  return role || "User";
}

function getInitial(username) {
  return (username || "U").trim().charAt(0).toUpperCase();
}

export default function UserMenu({
  currentUser = null,
  onLogout = () => {},
}) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);
  const username = currentUser?.username || currentUser?.full_name || "user";

  useEffect(() => {
    function handlePointerDown(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpen(false);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      {open && (
        <div className="absolute bottom-full left-2 right-2 mb-2 rounded-lg border border-slate-200 bg-white p-1.5 shadow-lg">
          <button
            type="button"
            onClick={onLogout}
            className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-left text-[11px] font-semibold text-red-600 hover:bg-red-50"
          >
            <LogOut size={13} />
            Dang xuat
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-slate-50"
      >
        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
          {getInitial(username)}
        </div>
        <div className="min-w-0">
          <p className="truncate text-[11px] font-semibold text-slate-700">
            {username}
          </p>
          <p className="truncate text-[10px] text-slate-400">
            {formatRole(currentUser?.role)}
          </p>
        </div>
      </button>
    </div>
  );
}

