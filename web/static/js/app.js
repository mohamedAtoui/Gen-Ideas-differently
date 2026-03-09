// CrossGen — Vanilla JS frontend with SSE streaming

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('solve-form');
    const input = document.getElementById('problem-input');
    const modelSelect = document.getElementById('model-select');
    const solveBtn = document.getElementById('solve-btn');
    const progressEl = document.getElementById('pipeline-progress');
    const resultsEl = document.getElementById('results');
    const errorEl = document.getElementById('error');
    const errorMsg = document.getElementById('error-msg');

    // Check for query param
    const params = new URLSearchParams(window.location.search);
    if (params.get('q')) {
        input.value = params.get('q');
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const problem = input.value.trim();
        if (!problem) return;
        startSolve(problem);
    });

    function startSolve(problem) {
        // Reset UI
        solveBtn.disabled = true;
        solveBtn.textContent = 'Running...';
        progressEl.classList.remove('hidden');
        resultsEl.classList.add('hidden');
        resultsEl.innerHTML = '';
        errorEl.classList.add('hidden');

        // Reset stages
        document.querySelectorAll('.stage').forEach(el => {
            el.className = 'stage stage-pending';
        });

        const model = modelSelect.value;
        const url = `/api/solve?problem=${encodeURIComponent(problem)}&model=${encodeURIComponent(model)}`;
        const source = new EventSource(url);
        let stageData = {};

        source.addEventListener('decompose', (e) => handleStage('decompose', e));
        source.addEventListener('abstract', (e) => handleStage('abstract', e));
        source.addEventListener('expand', (e) => handleStage('expand', e));
        source.addEventListener('mine', (e) => handleStage('mine', e));
        source.addEventListener('synthesize', (e) => handleStage('synthesize', e));
        source.addEventListener('evaluate', (e) => handleStage('evaluate', e));
        source.addEventListener('complete', (e) => {
            source.close();
            solveBtn.disabled = false;
            solveBtn.textContent = 'Solve';
            const data = JSON.parse(e.data);
            if (data.data) {
                renderResults(data.data);
            }
        });
        source.addEventListener('error', (e) => {
            source.close();
            solveBtn.disabled = false;
            solveBtn.textContent = 'Solve';
            if (e.data) {
                const data = JSON.parse(e.data);
                showError(data.error || 'Unknown error');
            } else {
                showError('Connection lost');
            }
        });

        source.onerror = () => {
            source.close();
            solveBtn.disabled = false;
            solveBtn.textContent = 'Solve';
        };

        function handleStage(stage, event) {
            const data = JSON.parse(event.data);
            const el = document.querySelector(`[data-stage="${stage}"]`);
            if (!el) return;

            if (data.status === 'running') {
                el.className = 'stage stage-running text-yellow-400';
            } else if (data.status === 'done') {
                el.className = 'stage stage-done';
                stageData[stage] = data.data;
            }
        }
    }

    function showError(msg) {
        errorEl.classList.remove('hidden');
        errorMsg.textContent = msg;
    }

    function renderResults(data) {
        resultsEl.classList.remove('hidden');
        const eval_ = data.evaluation;
        if (!eval_ || !eval_.scored_solutions || eval_.scored_solutions.length === 0) {
            resultsEl.innerHTML = '<div class="bg-gray-900 rounded-lg p-6 border border-gray-800 text-gray-400">No solutions generated.</div>';
            return;
        }

        let html = '';

        // Top recommendation
        if (eval_.top_recommendation) {
            html += `<div class="bg-purple-900/30 border border-purple-700 rounded-lg p-4">
                <span class="font-semibold text-purple-300">Top Recommendation:</span>
                <span class="text-gray-200 ml-2">${esc(eval_.top_recommendation)}</span>
            </div>`;
        }

        // Solutions table
        html += '<div class="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">';
        html += '<table class="w-full text-sm">';
        html += '<thead><tr class="border-b border-gray-800 text-gray-400">';
        html += '<th class="px-4 py-3 text-left">#</th>';
        html += '<th class="px-4 py-3 text-left">Source Domain</th>';
        html += '<th class="px-4 py-3 text-left">Mechanism</th>';
        html += '<th class="px-4 py-3 text-right">Novelty</th>';
        html += '<th class="px-4 py-3 text-right">Feasibility</th>';
        html += '<th class="px-4 py-3 text-right">Depth</th>';
        html += '<th class="px-4 py-3 text-right font-semibold">Score</th>';
        html += '</tr></thead><tbody>';

        eval_.scored_solutions.forEach((s, i) => {
            const rowClass = i === 0 ? 'bg-green-900/10' : '';
            html += `<tr class="border-b border-gray-800/50 ${rowClass}">`;
            html += `<td class="px-4 py-3 text-gray-500">${i + 1}</td>`;
            html += `<td class="px-4 py-3 text-cyan-400">${esc(s.solution.source_domain)}</td>`;
            html += `<td class="px-4 py-3">${esc(truncate(s.solution.source_mechanism, 50))}</td>`;
            html += `<td class="px-4 py-3 text-right text-purple-400">${s.novelty.toFixed(2)}</td>`;
            html += `<td class="px-4 py-3 text-right text-green-400">${s.feasibility.toFixed(2)}</td>`;
            html += `<td class="px-4 py-3 text-right text-blue-400">${s.structural_depth.toFixed(2)}</td>`;
            html += `<td class="px-4 py-3 text-right font-semibold text-yellow-400">${s.combined_score.toFixed(2)}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div>';

        // Detailed cards for top 3
        eval_.scored_solutions.slice(0, 3).forEach((s, i) => {
            const borderColor = i === 0 ? 'border-green-700' : 'border-gray-800';
            html += `<div class="bg-gray-900 rounded-lg p-6 border ${borderColor}">`;
            html += `<h3 class="font-semibold text-lg mb-3">#${i + 1} — ${esc(s.solution.source_domain)} <span class="text-gray-500 text-sm">(score: ${s.combined_score.toFixed(2)})</span></h3>`;
            html += `<p class="text-gray-400 text-sm mb-2"><strong class="text-gray-300">Mechanism:</strong> ${esc(s.solution.source_mechanism)}</p>`;
            html += `<p class="text-gray-300 mb-3">${esc(s.solution.concrete_approach)}</p>`;

            if (s.solution.candidate_inferences && s.solution.candidate_inferences.length > 0) {
                html += '<div class="mb-3"><strong class="text-gray-300 text-sm">Key Predictions:</strong><ul class="list-disc list-inside text-sm text-gray-400 mt-1">';
                s.solution.candidate_inferences.forEach(ci => {
                    html += `<li>${esc(ci)}</li>`;
                });
                html += '</ul></div>';
            }

            html += `<div class="flex gap-4 text-xs text-gray-500">`;
            html += `<span>Transfer: ${esc(s.solution.transfer_strength)}</span>`;
            if (s.analogy) {
                html += `<span>Breaks: ${esc(truncate(s.analogy.where_it_breaks, 60))}</span>`;
            }
            html += '</div></div>';
        });

        resultsEl.innerHTML = html;
    }

    function esc(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function truncate(str, len) {
        if (!str) return '';
        return str.length > len ? str.slice(0, len) + '...' : str;
    }
});
