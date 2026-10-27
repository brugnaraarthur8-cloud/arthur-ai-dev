const test = require("node:test");
const assert = require("node:assert/strict");
const { verifyMacArchiveSignature } = require("../scripts/mac-signature.cjs");

for (const [label, env] of [
  ["local ad-hoc build", {}],
  ["main push without credentials", { GITHUB_EVENT_NAME: "push" }],
  ["tag release without credentials", { GITHUB_EVENT_NAME: "push", GITHUB_REF: "refs/tags/v1.0.0" }],
  ["configured certificate", { CSC_LINK: "synthetic-certificate.p12" }],
  ["configured identity", { CSC_NAME: "Synthetic Identity" }],
  ["forced PR signing", { GITHUB_EVENT_NAME: "pull_request", CSC_FOR_PULL_REQUEST: "true" }],
  ["manual workflow", { GITHUB_EVENT_NAME: "workflow_dispatch" }],
]) {
  test(`${label} verifies the entire application signature`, () => {
    const calls = [];
    verifyMacArchiveSignature("/synthetic/App.app", { env, runChecked: (...args) => calls.push(args) });
    assert.deepEqual(calls, [["codesign", ["--verify", "--deep", "--strict", "--verbose=4", "/synthetic/App.app"]]]);
  });
  test(`${label} rejects an invalid signature`, () => {
    const failure = new Error("synthetic invalid signature");
    assert.throws(() => verifyMacArchiveSignature("/synthetic/App.app", {
      env, runChecked: () => { throw failure; },
    }), error => error === failure);
  });
}

for (const credentials of [{}, { CSC_LINK: "synthetic-certificate.p12" }, { CSC_NAME: "Synthetic Identity" }]) {
  test(`unforced PR documents the verification gap (${Object.keys(credentials).join() || "no credentials"})`, () => {
    const messages = [];
    verifyMacArchiveSignature("/synthetic/App.app", {
      env: { GITHUB_EVENT_NAME: "pull_request", ...credentials },
      runChecked: () => assert.fail("electron-builder skips PR signing"),
      log: message => messages.push(message),
    });
    assert.equal(messages.length, 1);
    assert.match(messages[0], /NOT verified/);
  });
}
