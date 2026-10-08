const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { isValidSessionId, escapeCsvField } = require("./security");

const apiKey = `test-${crypto.randomUUID()}`;
process.env.LFDS_API_KEY = apiKey;
delete process.env.HUBSPOT_TOKEN;
const { app } = require("./index");
const dataDir = path.join(__dirname, "data");
const fixtureId = `security-test-${crypto.randomUUID()}`;
const fixturePath = path.join(dataDir, `${fixtureId}.json`);
let server;
let baseUrl;

before(async () => {
  server = app.listen(0);
  await new Promise((resolve) => server.once("listening", resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
  fs.writeFileSync(fixturePath, JSON.stringify({
    session_id: fixtureId,
    contact: { email: '=HYPERLINK("https://example.test","click")', consent_given: true },
    profile: { primary: "  =1+1", scores: { epicurien: -3 } },
    utm: { utm_source: "\t@SUM(1)" },
    answers: [{ question_id: "budget", value: '+cmd|"/C calc"!A0' }],
  }));
});

after(async () => {
  await new Promise((resolve) => server.close(resolve));
  if (fs.existsSync(fixturePath)) fs.unlinkSync(fixturePath);
});

test("validateur : IDs usuels acceptés, séparateurs et extensions rejetés", () => {
  assert.equal(isValidSessionId("abc-123_XYZ"), true);
  assert.equal(isValidSessionId("x".repeat(128)), true);
  for (const id of ["../secret", "a/b", "a\\b", "a.json", "", "x".repeat(129), 123, null]) {
    assert.equal(isValidSessionId(id), false, JSON.stringify(id));
  }
});

test("CSV : formule, whitespace/control et guillemets neutralisés, nombres préservés", () => {
  assert.equal(escapeCsvField('=HYPERLINK("x","y")'), '"\'=HYPERLINK(""x"",""y"")"');
  for (const value of ["+cmd", "-1+2", "@SUM(1)", "\t=cmd", "\r@SUM(1)", "  =1+1", "\u200b=1+1"]) {
    assert.ok(escapeCsvField(value).startsWith('"\''), JSON.stringify(value));
  }
  assert.equal(escapeCsvField(-3), '"-3"');
  assert.equal(escapeCsvField('bonjour "oui"'), '"bonjour ""oui"""');
  assert.equal(escapeCsvField(null), '""');
});

test("POST refuse le traversal sans écriture en dehors de data", async () => {
  for (const session_id of ["../../intrusion", "x/y", "x\\y", 42, "a".repeat(129)]) {
    const response = await fetch(`${baseUrl}/api/quiz/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id }),
    });
    assert.equal(response.status, 400, JSON.stringify(session_id));
  }
});

test("GET/DELETE admin rejettent un slash encodé, même avec la clé", async () => {
  for (const method of ["GET", "DELETE"]) {
    const response = await fetch(`${baseUrl}/api/admin/submissions/..%2F..%2Fprivate`, {
      method,
      headers: { "x-api-key": apiKey },
    });
    assert.equal(response.status, 400, method);
  }
});

test("export CSV exige la clé et neutralise les champs non fiables", async () => {
  assert.equal((await fetch(`${baseUrl}/api/admin/export/csv`)).status, 401);
  const response = await fetch(`${baseUrl}/api/admin/export/csv`, { headers: { "x-api-key": apiKey } });
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type"), /text\/csv/);
  const csv = await response.text();
  assert.ok(csv.includes('"\'=HYPERLINK(""https://example.test"",""click"")"'));
  assert.ok(csv.includes('"\'  =1+1"'));
  assert.ok(csv.includes('"\'\t@SUM(1)"'));
  assert.ok(csv.includes('"\'+cmd|""/C calc""!A0"'));
  assert.ok(csv.includes('"-3"'));
});

test("le serveur ne journalise pas la valeur de la clé au démarrage", async () => {
  const sentinel = `SENSITIVE-${crypto.randomUUID()}`;
  const child = spawn(process.execPath, [path.join(__dirname, "index.js")], {
    env: { ...process.env, LFDS_API_KEY: sentinel, PORT: "0" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  let output = "";
  const completed = new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill();
      reject(new Error("server startup timed out"));
    }, 5000);
    child.stdout.on("data", (chunk) => {
      output += chunk;
      if (output.includes("Admin (x-api-key required):")) child.kill();
    });
    child.stderr.on("data", (chunk) => { output += chunk; });
    child.once("error", reject);
    child.once("close", () => { clearTimeout(timer); resolve(); });
  });
  await completed;
  assert.ok(output.includes("API Key:  configured (value hidden)"));
  assert.ok(!output.includes(sentinel));
});
