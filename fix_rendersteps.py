#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

# Read the file
with open('Chi_Square_Calculator.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of renderSteps function
start_marker = '    function renderSteps(res){'
start_idx = content.find(start_marker)

if start_idx == -1:
    print("ERROR: Could not find renderSteps function start")
    sys.exit(1)

# Find the closing brace of renderSteps (next function definition)
end_marker = '    function renderResults(res){'
end_idx = content.find(end_marker)

if end_idx == -1:
    print("ERROR: Could not find renderResults function start")
    sys.exit(1)

# Extract before and after
before = content[:start_idx]
after = content[end_idx:]

# New renderSteps function with ASCII-safe content
new_rendersteps = '''    function renderSteps(res){
      const stepsEl = document.getElementById("stepsContainer");
      const r = state.rows, c = state.cols;

      // Helpers
      const cellId = (i, j) => `(${i+1},${j+1})`;
      const alphaStr = fmt(res.alpha, 4);
      const pStr = fmt(res.p, 8);
      const chi2Str = fmt(res.chi2, 6);

      const decisionLine = (res.p < res.alpha)
        ? `<span class="status-good fw-bold">Reject H0</span> because <span class="mono">${pStr} &lt; ${alphaStr}</span>.`
        : `<span class="status-warn fw-bold">Fail to reject H0</span> because <span class="mono">${pStr} &ge; ${alphaStr}</span>.`;

      const interp = (res.p < res.alpha)
        ? `This provides statistically significant evidence that the two variables are associated (not independent).`
        : `This does not provide statistically significant evidence of an association at this alpha (results are consistent with independence).`;

      // Observed table with totals
      const observedTableHtml = (() => {
        let html = `<div class="table-wrap my-2"><table class="table table-dark table-bordered align-middle">
          <thead><tr><th style="min-width:220px">Category</th>`;
        for(let j=0;j<c;j++) html += `<th>${escapeHtml(state.colLabels[j])}</th>`;
        html += `<th>Total</th></tr></thead><tbody>`;
        for(let i=0;i<r;i++){
          html += `<tr><th>${escapeHtml(state.rowLabels[i])}</th>`;
          for(let j=0;j<c;j++) html += `<td class="mono">${fmt(res.O[i][j],0)}</td>`;
          html += `<td class="mono">${fmt(res.rowTotals[i],0)}</td></tr>`;
        }
        html += `<tr><th>Total</th>`;
        for(let j=0;j<c;j++) html += `<td class="mono">${fmt(res.colTotals[j],0)}</td>`;
        html += `<td class="mono">${fmt(res.n,0)}</td></tr>`;
        html += `</tbody></table></div>`;
        return html;
      })();

      // Expected counts derivations (all cells)
      const expectedDerivations = (() => {
        let html = `<details class="mt-2">
          <summary class="small-note" style="cursor:pointer;">
            Show all expected-count calculations (every cell)
          </summary>
          <div class="mt-2 small-note">
            Using <span class="mono">E&lt;sub&gt;ij&lt;/sub&gt; = (RowTotal&lt;sub&gt;i&lt;/sub&gt; * ColTotal&lt;sub&gt;j&lt;/sub&gt;) / n</span>:
          </div>
          <ul class="mt-2 mb-0">`;

        for (let i=0;i<r;i++){
          for (let j=0;j<c;j++){
            const RT = res.rowTotals[i];
            const CT = res.colTotals[j];
            const n = res.n;
            const Eij = res.E[i][j];
            html += `<li class="mono">
              E${cellId(i,j)} = (${RT} * ${CT}) / ${n} = ${fmt(Eij,4)}
            </li>`;
          }
        }

        html += `</ul></details>`;
        return html;
      })();

      // Chi-square contributions derivations (all cells)
      const chiDerivations = (() => {
        let html = `<details class="mt-2">
          <summary class="small-note" style="cursor:pointer;">
            Show all chi-square cell calculations (every cell contribution)
          </summary>
          <div class="mt-2 small-note">
            Base formula per cell: <span class="mono">(O - E)^2 / E</span>.
            ${res.useYates ? `With Yates (2x2): replace |O-E| by <span class="mono">max(0, |O-E| - 0.5)</span>.` : ``}
          </div>
          <ul class="mt-2 mb-0">`;

        let sumTerms = 0;

        for (let i=0;i<r;i++){
          for (let j=0;j<c;j++){
            const Oij = res.O[i][j];
            const Eij = res.E[i][j];

            const absDiff = Math.abs(Oij - Eij);
            const adjDiff = res.useYates ? Math.max(0, absDiff - 0.5) : absDiff;
            const term = (adjDiff * adjDiff) / Eij;

            sumTerms += term;

            if (res.useYates){
              html += `<li class="mono">
                Cell ${cellId(i,j)}: O=${fmt(Oij,0)}, E=${fmt(Eij,4)}; |O-E|=${fmt(absDiff,4)};
                adj=max(0,|O-E|-0.5)=${fmt(adjDiff,4)};
                contrib=(adj^2)/E=(${fmt(adjDiff,4)}^2)/${fmt(Eij,4)}=${fmt(term,6)}
              </li>`;
            } else {
              html += `<li class="mono">
                Cell ${cellId(i,j)}: O=${fmt(Oij,0)}, E=${fmt(Eij,4)}; (O-E)=${fmt(Oij - Eij,4)};
                contrib=((O-E)^2)/E=(${fmt(Oij - Eij,4)}^2)/${fmt(Eij,4)}=${fmt(term,6)}
              </li>`;
            }
          }
        }

        html += `</ul>
          <div class="mt-2 small-note">
            Sum of all contributions = <span class="mono">${fmt(sumTerms,6)}</span>
            (should match total chi-square <span class="mono">${chi2Str}</span>, up to rounding).
          </div>
        </details>`;

        return html;
      })();

      // Build steps (ASCII-safe and more elaborate)
      stepsEl.innerHTML = `
        <div class="step">
          <div class="fw-semibold mb-1">Step 1 - Identify variables and state hypotheses</div>
          <div class="small-note">
            This is a chi-square test for independence on a contingency table (counts of two categorical variables).
            <ul class="mt-2 mb-0">
              <li><b>Row variable</b>: categories listed on the left side.</li>
              <li><b>Column variable</b>: categories listed across the top.</li>
            </ul>
            <div class="mt-2">
              <span class="mono">H0</span>: The variables are independent (no association).<br>
              <span class="mono">H1</span>: The variables are not independent (an association exists).
            </div>
          </div>
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 2 - Observed counts (O) and totals</div>
          <div class="small-note">
            The observed table is the input data (counts). We compute:
            <ul class="mt-2 mb-0">
              <li><span class="mono">RowTotal(i)</span> = sum across row i</li>
              <li><span class="mono">ColTotal(j)</span> = sum down column j</li>
              <li><span class="mono">n</span> = grand total of all cells</li>
            </ul>
          </div>
          ${observedTableHtml}
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 3 - Compute expected counts (E) under H0</div>
          <div class="small-note">
            Under independence, the expected count in cell (i,j) is:
            <div class="mt-2">
              <span class="mono">E&lt;sub&gt;ij&lt;/sub&gt; = (RowTotal&lt;sub&gt;i&lt;/sub&gt; * ColTotal&lt;sub&gt;j&lt;/sub&gt;) / n</span>
            </div>
            Why this makes sense: if the variables are independent, the proportion in a row category and the proportion in a column category combine multiplicatively, so expected counts follow row totals and column totals.
          </div>
          <div class="small-note mt-2">
            Example (first cell): <span class="mono">E(1,1) = (${res.rowTotals[0]} * ${res.colTotals[0]}) / ${res.n} = ${fmt(res.E[0][0],4)}</span>
          </div>
          ${expectedDerivations}
          <div class="small-note mt-2">
            Rule-of-thumb assumption: expected counts should generally be at least 5 in most cells for the chi-square approximation.
          </div>
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 4 - Compute the chi-square test statistic</div>
          <div class="small-note">
            We measure how far observed counts are from expected counts using:
            <div class="mt-2">
              <span class="mono">chi-square = Sum over all cells of ((O - E)^2 / E)</span>
            </div>
            Interpretation: each cell contributes more when the observed count differs a lot from expected, relative to the expected size.
          </div>
          <div class="small-note mt-2">
            Computed test statistic: <span class="mono">chi-square = ${chi2Str}</span>
            ${res.useYates ? `<span class="status-warn">(Yates correction applied)</span>` : ``}
          </div>
          ${chiDerivations}
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 5 - Degrees of freedom</div>
          <div class="small-note">
            For an r x c table:
            <div class="mt-2"><span class="mono">df = (r-1)(c-1) = (${r}-1)(${c}-1) = ${res.df}</span></div>
            Reason: once row totals and column totals are fixed, only (r-1)(c-1) cells can vary freely.
          </div>
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 6 - Compute the p-value</div>
          <div class="small-note">
            Under H0, the statistic approximately follows a chi-square distribution with df degrees of freedom.
            The p-value is the right-tail probability:
            <div class="mt-2"><span class="mono">p-value = P(ChiSq(df) &ge; observed chi-square)</span></div>
            A small p-value means the observed deviation from independence is unlikely under H0.
          </div>
          <div class="small-note mt-2"><span class="mono">p-value = ${pStr}</span></div>
        </div>

        <div class="step">
          <div class="fw-semibold mb-1">Step 7 - Decision and conclusion</div>
          <div class="small-note">
            Using <span class="mono">alpha = ${alphaStr}</span>: ${decisionLine}<br>
            ${interp}
          </div>
          <div class="small-note mt-2">
            Optional effect size: <span class="mono">Cramer's V = ${fmt(res.V,6)}</span>.
          </div>
        </div>
      `;
    }

'''

# Combine
new_content = before + new_rendersteps + after

# Write back
with open('Chi_Square_Calculator.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: renderSteps function replaced with clean ASCII-safe version")
print(f"File size: {len(new_content)} bytes")
