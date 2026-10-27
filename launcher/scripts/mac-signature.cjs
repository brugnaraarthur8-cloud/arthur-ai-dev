// electron-builder skips signing on unforced pull_request builds. Everywhere
// else package.cjs requests either a configured identity or an ad-hoc signature.
function verifyMacArchiveSignature(appBundle, { env, runChecked, log = console.log }) {
  if (env.GITHUB_EVENT_NAME === "pull_request" && env.CSC_FOR_PULL_REQUEST !== "true") {
    log("PR build: electron-builder skips signing; application signature is NOT verified. Runtime integrity is checked separately.");
    return;
  }
  // Missing CSC_* credentials do not mean unsigned: identity=- is ad-hoc.
  // Propagate every verification failure, including local and release builds.
  runChecked("codesign", ["--verify", "--deep", "--strict", "--verbose=4", appBundle]);
}

module.exports = { verifyMacArchiveSignature };
