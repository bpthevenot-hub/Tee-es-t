// Shared by the Express server and the Netlify CSV export.
function isValidSessionId(id) {
  return typeof id === "string" && /^[A-Za-z0-9_-]{1,128}$/.test(id);
}

function escapeCsvField(value) {
  let text = String(value ?? "");
  // Quoting alone does not stop spreadsheet software from evaluating formulas.
  // Also handle leading whitespace/control characters used to hide a formula.
  if (
    typeof value === "string" &&
    (/^[\t\r\n]/u.test(text) || /^[\s\u0000-\u001f\u007f\u200b-\u200d\u2060]*[=+\-@]/u.test(text))
  ) {
    text = "'" + text;
  }
  return `"${text.replace(/"/g, '""')}"`;
}

module.exports = { isValidSessionId, escapeCsvField };
