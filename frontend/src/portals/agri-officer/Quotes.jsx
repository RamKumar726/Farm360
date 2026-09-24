import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * Quotes functionality is integrated directly into the Assignments page
 * (AgriAssignments.jsx) — the "Submit Solution & Quotation" button on each
 * lead card triggers the quotation form. This page redirects there.
 */
export default function AgriQuotes() {
  const navigate = useNavigate();
  useEffect(() => { navigate("/agri-officer/assignments", { replace: true }); }, [navigate]);
  return null;
}
