#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Read file
with open('Chi_Square_Calculator.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find boundaries
start_pattern = '    function renderSteps(res){'
end_pattern = '    function renderResults(res){'

start_idx = content.find(start_pattern)
end_idx = content.find(end_pattern)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

# Extract parts
before = content[:start_idx]
after = content[end_idx:]

# Clean ASCII-safe renderSteps function - NO Unicode, NO HTML entities that need entities
new_function = '''    function renderSteps(res){
      const stepsEl = document.getElementById("stepsContainer");
      const r = state.rows, c = state.cols;
      const n = res.n;

      // Format helpers
      const fmt_val = (v, d) => fmt(v, d);
      
      // Build table HTML for observed counts
      let tableHtml = '<div class="table-wrap my-2"><table class="table table-dark table-bordered"><thead><tr><th>Category</th>';
      for(let j=0; j<c; j++) tableHtml += '<th>' + escapeHtml(state.colLabels[j]) + '</th>';
      tableHtml += '<th>Total</th></tr></thead><tbody>';
      
      for(let i=0; i<r; i++){
        tableHtml += '<tr><th>' + escapeHtml(state.rowLabels[i]) + '</th>';
        for(let j=0; j<c; j++){
          tableHtml += '<td class="mono">' + fmt_val(res.O[i][j], 0) + '</td>';
        }
        tableHtml += '<td class="mono"><b>' + fmt_val(res.rowTotals[i], 0) + '</b></td></tr>';
      }
      
      tableHtml += '<tr><th>Total</th>';
      for(let j=0; j<c; j++){
        tableHtml += '<td class="mono"><b>' + fmt_val(res.colTotals[j], 0) + '</b></td>';
      }
      tableHtml += '<td class="mono"><b>' + fmt_val(n, 0) + '</b></td></tr>';
      tableHtml += '</tbody></table></div>';

      // Decision statement color coding
      const pVal = fmt_val(res.p, 8);
      const alphaVal = fmt_val(res.alpha, 4);
      const chi2Val = fmt_val(res.chi2, 6);
      const dfVal = res.df;
      const cramerVal = fmt_val(res.V, 6);

      let decisionHtml = '';
      let decisionClass = 'status-warn';
      let decisionText = 'Fail to reject H0';
      let decisionExpl = 'does NOT provide statistically significant evidence of an association';
      
      if(res.p < res.alpha){
        decisionClass = 'status-good';
        decisionText = 'Reject H0';
        decisionExpl = 'DOES provide statistically significant evidence of an association';
      }

      decisionHtml = '<span class="' + decisionClass + ' fw-bold">' + decisionText + '</span> (p = ' + pVal + ')';

      // Build all steps
      let html = '';
      
      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 1: Hypotheses</div>';
      html += '<div class="small-note">';
      html += 'H0 (Null): The two variables are independent (no association)<br>';
      html += 'H1 (Alternative): The two variables are associated (not independent)<br>';
      html += 'Significance level: alpha = ' + alphaVal;
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 2: Observed Contingency Table</div>';
      html += '<div class="small-note">';
      html += 'Below are the observed counts O(i,j) for each cell:';
      html += tableHtml;
      html += 'Total sample size n = ' + fmt_val(n, 0);
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 3: Expected Counts Under H0</div>';
      html += '<div class="small-note">';
      html += 'Under independence (H0), expected count in cell (i,j) is:<br>';
      html += '<span class="mono">E(i,j) = (Row Total) * (Col Total) / n</span><br><br>';
      html += '<table class="table table-dark table-sm table-bordered"><thead><tr><th>Cell</th><th>Formula</th><th>Expected</th></tr></thead><tbody>';
      for(let i=0; i<r; i++){
        for(let j=0; j<c; j++){
          const cellLabel = '(' + (i+1) + ',' + (j+1) + ')';
          const formula = '(' + fmt_val(res.rowTotals[i], 0) + ' * ' + fmt_val(res.colTotals[j], 0) + ') / ' + fmt_val(n, 0);
          const expected = fmt_val(res.E[i][j], 4);
          html += '<tr><td>' + cellLabel + '</td><td>' + formula + '</td><td>' + expected + '</td></tr>';
        }
      }
      html += '</tbody></table>';
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 4: Chi-Square Test Statistic</div>';
      html += '<div class="small-note">';
      html += 'Formula: chi-square = SUM[(O - E)^2 / E]<br><br>';
      html += '<table class="table table-dark table-sm table-bordered"><thead><tr><th>Cell</th><th>O</th><th>E</th><th>(O-E)^2/E</th></tr></thead><tbody>';
      
      let sumContrib = 0;
      for(let i=0; i<r; i++){
        for(let j=0; j<c; j++){
          const O = res.O[i][j];
          const E = res.E[i][j];
          const contrib = res.contrib[i][j];
          sumContrib += contrib;
          const cellLabel = '(' + (i+1) + ',' + (j+1) + ')';
          html += '<tr><td>' + cellLabel + '</td><td>' + fmt_val(O, 0) + '</td><td>' + fmt_val(E, 4) + '</td><td>' + fmt_val(contrib, 6) + '</td></tr>';
        }
      }
      
      html += '</tbody></table>';
      html += '<br>Computed chi-square statistic: <span class="mono fw-bold">' + chi2Val + '</span><br>';
      if(res.useYates) html += '(Yates continuity correction applied)<br>';
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 5: Degrees of Freedom</div>';
      html += '<div class="small-note">';
      html += 'df = (rows - 1) * (cols - 1) = (' + r + ' - 1) * (' + c + ' - 1) = ' + dfVal;
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 6: P-value</div>';
      html += '<div class="small-note">';
      html += 'p-value = P(chi-square(' + dfVal + ') >= ' + chi2Val + ')<br>';
      html += '<span class="mono fw-bold">p-value = ' + pVal + '</span>';
      html += '</div></div>';

      html += '<div class="step">';
      html += '<div class="fw-semibold mb-2">Step 7: Decision and Conclusion</div>';
      html += '<div class="small-note">';
      html += '<b>Decision:</b> ' + decisionHtml + '<br><br>';
      html += '<b>Interpretation:</b> Since p-value ' + (res.p < res.alpha ? '<' : '>=') + ' alpha, we ' + decisionExpl + '.<br><br>';
      html += '<b>Effect Size (Cramer\'s V):</b> ' + cramerVal + ' (0 = no association, 1 = perfect association)';
      html += '</div></div>';

      stepsEl.innerHTML = html;
    }

'''

# Combine
new_content = before + new_function + after

# Write back
with open('Chi_Square_Calculator.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: renderSteps replaced with clean version (no Unicode)")
print(f"New file size: {len(new_content)} bytes")
