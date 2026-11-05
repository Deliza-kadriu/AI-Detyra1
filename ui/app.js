'use strict';
const $ = id => document.getElementById(id);
const descriptions = {
  golfers: ['Social Golfers', 'DFS builds groups, rejects repeated pairs and undoes choices when a branch fails.'],
  sudoku: ['Sudoku', 'FIFO breadth-first search explores partial boards one level at a time. Clues stay fixed.'],
  latin: ['Latin Square', 'IDDFS restarts depth-limited DFS at each limit. Backtracking clears failed cell assignments.'],
  trees: ['Search trees', 'Explore BFS spanning trees, rejected actions, repeated states and the first solution path.'],
  reference: ['Published optimal schedule', 'Independently verify a published ten-week witness and the matching upper bound.']
};
let examples = {}, running = false, runId = null, result = null, timer = null;
let started = 0, eventCount = 0, logCount = 0, activeAlgorithm = 'golfers';
let initialSudoku = null, baselines = {}, benchmarkRows = [], activeParameters = null;
const benchmarkDefaults = {sudoku:[25,65,10,3,0,81,'Empty cells'],golfers:[1,7,1,1,1,20,'Weeks'],latin:[1,6,1,1,1,7,'Square size'],trees:[0,8,2,1,0,20,'Depth limit']};
const inputBoard = $('puzzle-input');
for (let i = 0; i < 81; i++) {
  const cell = document.createElement('input');
  cell.type = 'text'; cell.inputMode = 'numeric'; cell.maxLength = 1;
  cell.setAttribute('aria-label', `Row ${Math.floor(i/9)+1}, column ${i%9+1}`);
  cell.addEventListener('input', () => {
    cell.value = cell.value.replace(/[^1-9]/g, '');
    $('difficulty').value = 'custom';
  });
  inputBoard.append(cell);
}
function sudokuInput(board) {
  [...inputBoard.children].forEach((cell, i) => { cell.value = board?.[Math.floor(i/9)]?.[i%9] || ''; });
}
function readBoard() {
  return Array.from({length:9}, (_,r) => Array.from({length:9}, (_,c) => Number(inputBoard.children[r*9+c].value || 0)));
}
function setStatus(text, kind = '') { $('status').textContent = text; $('status').className = `status ${kind}`; }
function updateBound() {
  const g = Number($('groups').value), p = Number($('players').value), w = Number($('weeks').value);
  const n = g*p, bound = p > 1 ? Math.floor((n-1)/(p-1)) : null;
  $('golf-bound').textContent = `${n} players · ${bound === null ? 'No finite pair bound' : `at most ${bound} weeks by pair counting`}${bound !== null && w > bound ? '. This target exceeds the bound.' : '.'}`;
  $('golf-bound').classList.toggle('warning', bound !== null && w > bound);
}
function syncForm() {
  const algorithm = $('algorithm').value;
  $('algorithm-note').textContent = descriptions[algorithm][1];
  for (const section of document.querySelectorAll('[data-fields]')) {
    section.hidden = section.dataset.fields !== algorithm;
    for (const control of section.querySelectorAll('input,select,button')) control.disabled = section.hidden || running;
  }
  for (const control of $('experiment').querySelectorAll('input,select,button')) {
    if (!control.closest('[data-fields]') && control.id !== 'stop') control.disabled = running;
  }
  const benchmark = $('mode').value === 'benchmark' && algorithm !== 'reference';
  $('mode').disabled = running || algorithm === 'reference';
  if (algorithm === 'reference') $('mode').value = 'single';
  $('benchmark-controls').hidden = !benchmark;
  $('events-label').textContent = benchmark ? 'TRIALS COMPLETED' : 'TRACE EVENTS';
  $('trace-title').textContent = benchmark ? 'Benchmark log' : 'Live trace';
  $('log-kind').textContent = benchmark ? 'Measured trial events' : 'Actual solver events';
  for (const control of $('benchmark-controls').querySelectorAll('input')) control.disabled = running || !benchmark;
  for (const id of ['weeks','maximize','difficulty','size','max-depth']) $(id).disabled ||= benchmark;
  for (const input of inputBoard.children) input.disabled ||= benchmark;
  inputBoard.hidden = benchmark;
  $('time-limit').parentElement.hidden = benchmark;
  document.querySelector('.trace-settings').hidden = benchmark;
  if (algorithm === 'sudoku') $('puzzle-note').textContent = benchmark
    ? 'The benchmark generates valid incomplete boards at each blank count. It measures finding any completion, not uniqueness.'
    : 'Generated demonstration levels. Edit cells for a custom puzzle; blank means empty. For Hard, use a 0 ms pause to keep the run within budget.';
  $('bench-seed').disabled = running || !benchmark || algorithm !== 'sudoku';
  $('bench-seed').hidden = algorithm !== 'sudoku';
  document.querySelector('[for="bench-seed"]').hidden = algorithm !== 'sudoku';
  document.querySelector('#tree-problem option[value="all"]').disabled = benchmark;
  if (benchmark && $('tree-problem').value === 'all') $('tree-problem').value = '8-puzzle';
  const enhanced = $('golf-strategy').value !== 'numeric';
  $('enhanced-controls').hidden = !enhanced;
  for (const control of $('enhanced-controls').querySelectorAll('input')) control.disabled = running || !enhanced || algorithm !== 'golfers';
  const strategyNotes={numeric:'The coursework baseline follows numeric candidate order.',restarts:'Extra mode: constrained players first, forward checking and seeded DFS restarts. The longest valid prefix is retained.',structured:'Extra mode for 8 groups of 4: mathematical candidate preferences help reach nine weeks. This uses additional structure, not the baseline uninformed ordering. Ten still requires search.'};
  $('strategy-note').textContent = strategyNotes[$('golf-strategy').value];
  $('stop').disabled = !running;
  $('run').innerHTML = running ? '<span>●</span> Running…' : `<span>▶</span> ${benchmark ? 'Measure limits' : 'Run experiment'}`;
  $('delay').disabled = running || !$('trace').checked;
  $('delay-value').textContent = `${$('delay').value} ms`;
  if (!running) $('stage-title').textContent = descriptions[algorithm][0];
  updateBound();
  updatePerformance();
}
$('algorithm').addEventListener('change', () => {
  activeAlgorithm = $('algorithm').value;
  setBenchmarkDefaults();
  $('visual').replaceChildren(element('div','Choose inputs, then run this experiment.','empty-state'));
  $('results').replaceChildren(element('p','Completed cases will appear here.','muted'));
  $('current-step').textContent = 'Configure your inputs and run an experiment.';
  $('case-name').textContent = ''; $('form-error').textContent = '';
  $('nodes').textContent = '—'; $('metric-value').textContent = '—';
  $('elapsed').innerHTML = '0.0<small>s</small>';
  result = null; $('download').disabled = true;
  setStatus('Ready'); syncForm(); metrics();
});
$('trace').addEventListener('change', syncForm);
$('mode').addEventListener('change', syncForm);
$('delay').addEventListener('input', () => $('delay-value').textContent = `${$('delay').value} ms`);
for (const id of ['groups','players','weeks']) $(id).addEventListener('input', updateBound);
$('golf-strategy').onchange = syncForm;
$('small-preset').onclick = () => { $('golf-strategy').value='numeric'; $('groups').value = 3; $('players').value = 2; $('weeks').value = 5; syncForm(); };
$('large-preset').onclick = () => { $('golf-strategy').value='numeric'; $('groups').value = 8; $('players').value = 4; $('weeks').value = 5; syncForm(); };
$('push-preset').onclick = () => {
  $('mode').value='single'; $('groups').value=8; $('players').value=4; $('weeks').value=10;
  $('golf-strategy').value='structured'; $('golf-seed').value=2026; $('restart-nodes').value=10000;
  $('maximize').checked=false; $('trace').checked=false; $('delay').value=0;
  $('max-nodes').value=2000000; $('time-limit').value=30; syncForm();
};
$('difficulty').onchange = () => {
  const level = $('difficulty').value;
  if (examples[level] || level === 'all') sudokuInput(examples[level] || examples.easy);
  else sudokuInput(null);
  updatePerformance();
};
$('clear-trace').onclick = () => { $('trace-log').replaceChildren(); logCount = 0; };
function element(tag, text, className) {
  const el = document.createElement(tag); if (text !== undefined) el.textContent = text;
  if (className) el.className = className; return el;
}
function log(message) {
  const area = $('trace-log');
  area.querySelector('.trace-placeholder')?.remove();
  const kind = /BACKTRACK|DEAD END/.test(message) ? 'backtrack' : /REJECT/.test(message) ? 'reject' : /GOAL|PASS|complete/.test(message) ? 'goal' : '';
  const line = element('div', undefined, `trace-line ${kind}`);
  line.append(element('span', String(++logCount).padStart(4,'0'), 'trace-number'), element('span', message));
  area.append(line);
  while (area.children.length > 400) area.firstChild.remove();
  if ($('follow').checked) area.scrollTop = area.scrollHeight;
}
function metrics(stats = {}) {
  if (stats.expanded_nodes !== undefined) $('nodes').textContent = stats.expanded_nodes.toLocaleString();
  const isQueue = activeAlgorithm === 'sudoku' || activeAlgorithm === 'trees';
  $('metric-label').textContent = isQueue ? 'PEAK FRONTIER' : 'BACKTRACKS';
  const value = isQueue ? stats.peak_frontier : stats.backtracks;
  if (value !== undefined) $('metric-value').textContent = value.toLocaleString();
}
function boardView(board, sudoku = false, activeCell = null, clues = null) {
  const n = board.length;
  const grid = element('div', undefined, `board${sudoku ? ' sudoku' : ''}`);
  grid.style.gridTemplateColumns = `repeat(${n},1fr)`;
  board.forEach((row,r) => row.forEach((value,c) => {
    const cell = element('div', value || '·', `cell${!value ? ' blank' : ''}${clues?.[r]?.[c] ? ' clue' : ''}${activeCell?.[0] === r && activeCell?.[1] === c ? ' active' : ''}`);
    grid.append(cell);
  }));
  return grid;
}
function showState(event) {
  if (event.board) {
    $('visual').replaceChildren(boardView(event.board, activeAlgorithm === 'sudoku', event.cell, initialSudoku));
  } else if (event.state) {
    const state = event.state;
    if (event.problem === '8-puzzle') {
      $('visual').replaceChildren(boardView([state.slice(0,3),state.slice(3,6),state.slice(6,9)]));
    } else {
      const chips = element('div', undefined, 'state-chips');
      const values = event.problem === 'missionaries' ? [`${state[0]} missionaries left`,`${state[1]} cannibals left`,`Boat: ${state[2] ? 'right' : 'left'}`] : Array.from({length:6}, (_,i) => `Day ${i+1}: ${state[i] || '—'}`);
      values.forEach(value => chips.append(element('span', value)));
      $('visual').replaceChildren(chips);
    }
  }
}
function scheduleView(schedule) {
  const wrap = element('div', undefined, 'schedule-wrap'), table = element('table');
  const head = element('tr'); head.append(element('th','Week'));
  schedule[0].forEach((_,i) => head.append(element('th',`Group ${i+1}`)));
  const thead = element('thead'); thead.append(head); table.append(thead);
  const body = element('tbody');
  schedule.forEach((week,i) => {
    const row = element('tr'); row.append(element('td',String(i+1)));
    week.forEach(group => row.append(element('td',group.join(', ')))); body.append(row);
  });
  table.append(body); wrap.append(table); return wrap;
}
function treeView(tree) {
  const wrap = element('div', undefined, 'tree-view');
  const children = new Map(), path = new Set(tree.solution_path);
  tree.nodes.forEach(node => { if (!children.has(node.parent)) children.set(node.parent, []); children.get(node.parent).push(node); });
  function append(node, parent) {
    const block = element('div', undefined, `tree-node${path.has(node.id) ? ' on-path' : ''}`);
    block.append(element('div',`${path.has(node.id) ? '★' : '·'} #${node.id} ${node.action} [${node.kind}${node.repeat_of !== undefined ? ` → #${node.repeat_of}` : ''}]`, 'tree-line'));
    const info = element('details'), summary = element('summary','State & rejected actions'); info.append(summary);
    info.append(element('div', JSON.stringify(node.state)));
    node.rejections.forEach(rejection => info.append(element('div',`× ${rejection.action}: ${rejection.reason}`)));
    block.append(info);
    (children.get(node.id) || []).forEach(child => append(child, block));
    parent.append(block);
  }
  append(tree.nodes[0], wrap); return wrap;
}
function renderCase(event) {
  metrics(event.stats);
  const section = element('div', undefined, 'result-case');
  let title = event.weeks ? `${event.weeks} weeks` : event.difficulty || (event.size ? `${event.size} × ${event.size} Latin Square` : event.tree?.problem || 'Result');
  if (event.target_weeks && event.target_weeks !== event.weeks && event.schedule) title += ` retained / ${event.target_weeks}-week target`;
  section.append(element('h3',title));
  if(event.target_reached === false && event.schedule) section.append(element('p',`Valid partial achievement: ${event.weeks} complete weeks. The ${event.target_weeks}-week target was not reached.`, 'muted'));
  if(event.strategy && event.strategy !== 'numeric') section.append(element('p',`Extra search mode: ${event.strategy}; ${event.stats.attempts || 0} attempts, ${event.stats.restarts || 0} restarts.`, 'muted'));
  const status = event.stats?.status || event.status || 'complete';
  const checked = event.validation?.valid;
  const text = checked ? 'PASS · Independent constraint validation' : status === 'infeasible' ? 'Infeasible · No valid completion exists' : status === 'resource_limit' ? 'Resource limit · Feasibility remains unknown' : event.tree && !event.tree.solution_path.length ? 'No goal found within the selected limits' : status;
  section.append(element('p',text,checked ? 'pass' : 'muted'));
  if (event.stop_reason) section.append(element('p',event.stop_reason,'muted'));
  if (event.stats?.expanded_nodes !== undefined) section.append(element('p',`${event.stats.expanded_nodes.toLocaleString()} expanded nodes${event.stats.elapsed_seconds !== undefined ? ` · ${event.stats.elapsed_seconds.toFixed(4)} s (including trace pauses)` : ''}`));
  if (event.tree) {
    section.append(element('p',`${event.tree.nodes.length} recorded tree nodes · ${event.tree.truncated ? 'Partial tree: search was truncated' : 'Reachable search exhausted; goals terminal'}`));
    if (event.tree.solution_path.length) section.append(element('p',`Solution path: ${event.tree.solution_path.map(id=>`#${id}`).join(' → ')}`));
    const details = element('details'); details.append(element('summary','Explore tree')); details.append(treeView(event.tree)); section.append(details);
    $('visual').replaceChildren(treeView(event.tree));
  }
  if (event.schedule) $('visual').replaceChildren(scheduleView(event.schedule));
  if (event.solution || event.square) $('visual').replaceChildren(boardView(event.solution || event.square, !!event.solution, null, event.input));
  if (event.source_url) {
    section.append(element('p','Published witness; not a local DFS discovery.'));
    const link = element('a','View attributed source'); link.href = event.source_url; link.target='_blank'; link.rel='noopener'; section.append(link);
  }
  $('results').append(section);
  $('case-name').textContent = title;
  log(`CASE ${title}: ${status}${checked ? '; validation PASS' : ''}`);
}
function processEvent(event) {
  if(event.type === 'best') {
    metrics(event.stats);
    $('visual').replaceChildren(scheduleView(event.schedule));
    $('case-name').textContent=`Best so far: ${event.weeks} weeks`;
    $('current-step').textContent=`${event.weeks} complete weeks independently validated. Searching toward target ${event.target_weeks}…`;
    result={algorithm:'golfers',kind:'best_so_far',parameters:activeParameters,schedule:event.schedule,weeks:event.weeks,target_weeks:event.target_weeks,target_reached:event.weeks===event.target_weeks,validation:event.validation,strategy:event.strategy};
    $('download').disabled=false;
    log(`BEST: ${event.weeks} complete weeks; independent validation PASS`); return;
  }
  if (event.type === 'benchmark_progress') {
    $('current-step').textContent = `${event.message} · ${event.completed}/${event.planned} trials completed`;
    $('events').textContent = `${event.completed}/${event.planned}`;
    $('case-name').textContent = 'Tracing off for measurement';
    log(event.message); return;
  }
  if (event.type === 'benchmark_case') {
    metrics({expanded_nodes:event.expanded_nodes,peak_frontier:event.peak_frontier,backtracks:event.backtracks});
    log(`${event.value}: ${event.status} in ${formatTime(event.elapsed_seconds)}${event.stop_reason ? ' · '+event.stop_reason : ''}`); return;
  }
  if (event.type === 'benchmark_row') {
    benchmarkRows.push(event.row);
    renderBenchmark(benchmarkRows, event.axis); return;
  }
  if (event.type === 'result' && event.mode === 'benchmark') {
    result = event; $('download').disabled = false;
    renderBenchmark(event.rows, event.axis);
    const s = event.summary;
    $('events').textContent = `${s.completed_trials}/${s.planned_trials}`;
    const largest = s.largest_observed_success === null ? 'none' : `${s.largest_observed_success} ${event.axis}`;
    const all = s.largest_all_samples_successful === null ? 'none' : `${s.largest_all_samples_successful} ${event.axis}`;
    $('current-step').textContent = `Largest observed success: ${largest}. This is an empirical result, not a universal limit.`;
    const note = element('div',undefined,'benchmark-summary');
    note.append(element('p',`Largest observed success: ${largest}`),element('p',`Largest with all requested samples successful: ${all}`),element('p',`${s.completed_trials}/${s.planned_trials} trials completed · ${formatTime(s.wall_seconds)} overall${s.total_budget_exhausted ? ' · Total budget reached' : ''}`),element('p','Generated cases and selected budgets only. Times exclude tracing. Limits do not prove impossibility.'));
    $('results').replaceChildren(note);
    setStatus(s.total_budget_exhausted ? 'Budget reached' : 'Measured'); log('BENCHMARK COMPLETE'); return;
  }
  if (event.type === 'start') { log(`START ${descriptions[activeAlgorithm][0]}`); return; }
  if (event.type === 'case_start') {
    initialSudoku = event.input;
    $('case-name').textContent = event.name;
    if (event.input) $('visual').replaceChildren(boardView(event.input, true, null, event.input));
    return;
  }
  if (event.type === 'trace') {
    eventCount++; $('events').textContent = eventCount.toLocaleString();
    $('current-step').textContent = event.message; log(event.message); metrics(event.stats || event); showState(event);
    if (event.case) $('case-name').textContent = event.case;
  } else if (event.type === 'case') {
    renderCase(event);
  } else if (event.type === 'result') {
    result = event; $('download').disabled = false;
    const outcomes = event.runs.map(run=>run.stats?.status || run.status);
    const limited = outcomes.includes('resource_limit');
    setStatus(limited ? 'Resource limit' : 'Complete');
    let text = 'Run complete. Independent checks are shown below.';
    if (activeAlgorithm === 'golfers') {
      const s = event.summary;
      text = `Best found: ${s.best_weeks_found} weeks · Pair bound: ${s.pair_counting_upper_bound ?? 'unbounded'} · Maximum proven: ${s.maximum_proven ? 'yes' : 'no'}`;
    } else if (activeAlgorithm === 'reference') text = 'Published witness verified · Mathematical maximum: ten weeks';
    $('current-step').textContent = text;
    $('results').prepend(element('div',text,'summary-line'));
    log('FINISHED');
  } else if (event.type === 'error' || event.type === 'stopped') {
    setStatus(event.status === 'cancelled' ? 'Stopped' : event.status === 'resource_limit' ? 'Resource limit' : 'Error', event.type === 'error' ? 'error' : '');
    $('current-step').textContent = event.message; log(event.message);
    if (event.type === 'error') $('form-error').textContent = event.message;
  }
}
function parameters() {
  const algorithm = $('algorithm').value;
  const params = {algorithm, mode:$('mode').value, run_id:crypto.randomUUID(), trace:$('trace').checked,
    delay:$('trace').checked ? Number($('delay').value)/1000 : 0,
    max_nodes:Number($('max-nodes').value), time_limit:Number($('time-limit').value)};
  if (algorithm === 'golfers') Object.assign(params,{groups:Number($('groups').value),players_per_group:Number($('players').value),weeks:Number($('weeks').value),maximize:$('maximize').checked,strategy:$('golf-strategy').value,seed:Number($('golf-seed').value),restart_nodes:Number($('restart-nodes').value)});
  if (algorithm === 'sudoku') Object.assign(params,{difficulty:$('difficulty').value,board:readBoard(),max_frontier:Number($('max-frontier').value)});
  if (algorithm === 'latin') Object.assign(params,{size:Number($('size').value),symmetry:$('symmetry').checked,goal_depth_pruning:$('goal-pruning').checked});
  if (algorithm === 'trees') Object.assign(params,{problem:$('tree-problem').value,max_depth:$('max-depth').value === '' ? null : Number($('max-depth').value)});
  if (params.mode === 'benchmark') Object.assign(params,{
    bench_from:Number($('bench-from').value),bench_to:Number($('bench-to').value),bench_step:Number($('bench-step').value),
    bench_samples:Number($('bench-samples').value),bench_seed:Number($('bench-seed').value),
    bench_seconds:Number($('bench-seconds').value),bench_total_seconds:Number($('bench-total').value),trace:false,delay:0});
  return params;
}
$('experiment').addEventListener('submit', async event => {
  event.preventDefault(); if (running) return;
  const params = parameters(); activeParameters=params; activeAlgorithm = params.algorithm; runId = params.run_id;
  initialSudoku = params.algorithm === 'sudoku' ? (examples[params.difficulty] || params.board) : null;
  running = true; result = null; eventCount = 0; logCount = 0; benchmarkRows = [];
  $('results').replaceChildren(); $('trace-log').replaceChildren(); $('download').disabled = true;
  $('events').textContent = '0'; $('nodes').textContent = '—'; $('metric-value').textContent = '—';
  $('case-name').textContent = ''; $('form-error').textContent = '';
  $('current-step').textContent = 'Starting the Python solver…';
  $('visual').replaceChildren(element('div','Waiting for the next search step…','empty-state'));
  setStatus('Running','running'); syncForm(); metrics();
  started = performance.now();
  timer = setInterval(() => { $('elapsed').innerHTML = `${((performance.now()-started)/1000).toFixed(1)}<small>s</small>`; },100);
  try {
    const response = await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(params)});
    if (!response.ok) throw new Error((await response.json()).error || 'Could not start experiment.');
    const reader = response.body.getReader(), decoder = new TextDecoder();
    let pending = '';
    while (true) {
      const {value,done} = await reader.read();
      pending += decoder.decode(value || new Uint8Array(),{stream:!done});
      const lines = pending.split('\n'); pending = lines.pop();
      for (const line of lines) if (line.trim()) processEvent(JSON.parse(line));
      if (done) { if (pending.trim()) processEvent(JSON.parse(pending)); break; }
      // Yield so the browser paints live steps and Stop stays responsive.
      await new Promise(resolve => requestAnimationFrame(resolve));
    }
    if ($('status').textContent === 'Running') throw new Error('The run ended without a final result.');
  } catch (error) {
    setStatus('Error','error'); $('form-error').textContent = error.message; log(`ERROR: ${error.message}`);
  } finally {
    clearInterval(timer); running = false; runId = null; syncForm();
  }
});
$('stop').onclick = async () => {
  if (!runId) return;
  $('stop').disabled = true; $('current-step').textContent = 'Stopping experiment…';
  try {
    await fetch('/api/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:runId})});
  } catch(error) { $('form-error').textContent = error.message; }
};
$('download').onclick = () => {
  if (!result) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\n'],{type:'application/json'}));
  const link = document.createElement('a'); link.href=url; link.download=`${result.algorithm}-result.json`; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
};
async function initialize() {
  try {
    const response = await fetch('/api/examples');
    if (!response.ok) throw new Error('Could not load example puzzles.');
    examples = await response.json(); sudokuInput(examples.easy);
    const measured = await fetch('/api/baselines');
    if (measured.ok) baselines = await measured.json();
  } catch(error) { $('form-error').textContent = error.message; }
  setBenchmarkDefaults(); syncForm();
}
initialize();

function formatTime(seconds) {
  if (seconds === null || seconds === undefined) return '—';
  if (seconds < 0.001) return `${(seconds*1000).toFixed(3)} ms`;
  if (seconds < 1) return `${(seconds*1000).toFixed(1)} ms`;
  return `${seconds.toFixed(2)} s`;
}
function setBenchmarkDefaults() {
  const a = $('algorithm').value, defaults = benchmarkDefaults[a];
  if (!defaults) return;
  ['bench-from','bench-to','bench-step','bench-samples'].forEach((id,i) => $(id).value=defaults[i]);
  for (const id of ['bench-from','bench-to']) { $(id).min=defaults[4]; $(id).max=defaults[5]; }
  $('bench-from-label').textContent=`${defaults[6]}: from`;
  $('bench-to-label').textContent='To';
  $('bench-samples-label').textContent=a==='sudoku' ? 'Puzzles / count' : 'Runs / input';
  $('benchmark-note').textContent=a==='sudoku'
    ? 'Vary empty-cell count and generate multiple seeded puzzles per count. Trace is off; no fixed completion-time promise.'
    : `Vary ${defaults[6].toLowerCase()} using the current configuration below. The range replaces the single-case value. Trace is off.`;
}
function updatePerformance() {
  const algorithm=$('algorithm').value, area=$('performance-info'); area.replaceChildren();
  const notes = {
    sudoku:'Blank count alone does not predict time. Any completion can exist even with 81 blanks, but our BFS may exceed its budget. A uniquely solvable standard Sudoku can have at most 64 blanks (17 clues); that does not guarantee unique solvability for a given 17-clue board. This solver finds one completion and does not test uniqueness.',
    golfers:'The mathematical bound is floor((players−1)/(group size−1)). For 32 players in groups of four, ten weeks is attainable using the published witness. Numeric DFS found five within its recorded budget. Optional restarts reach further; structure-guided DFS can retain nine. More time alone does not guarantee ten, and a nine-week prefix may require earlier changes to extend.',
    latin:'A Latin Square exists for every positive n: a cyclic construction proves existence. IDDFS has a practical resource limit, not a mathematical maximum size. Symmetry and pruning settings strongly affect timing.',
    trees:'Depth here is an exploration budget, not a measure of initial puzzle difficulty. More depth usually explores more states; reaching the node or time cap truncates the tree. Goal discovery and exhausting a state graph are different outcomes.',
    reference:'The ten-week schedule is published reference evidence. Checking a witness is much cheaper than searching for one; its verification time is not a DFS runtime estimate.'
  };
  area.append(element('p',notes[algorithm]));
  if(algorithm==='sudoku') {
    const p=element('p'); const a=element('a','17-clue minimum: McGuire, Tugemann & Civario'); a.href='https://arxiv.org/abs/1201.0749';a.target='_blank';a.rel='noopener';p.append(a);area.append(p);
  }
  const cases=baselines[algorithm] || [];
  if(cases.length) {
    const table=element('table',undefined,'baseline-table'), head=element('tr');
    ['Saved example','Measured time','Search effort'].forEach(x=>head.append(element('th',x)));table.append(head);
    cases.forEach(run=>{
      const row=element('tr');
      const title=algorithm==='sudoku' ? `${run.value} blanks` : algorithm==='golfers' ? `${run.value} weeks` : algorithm==='latin' ? `n=${run.value}${run.symmetry_breaking ? ', symmetry' : ', no symmetry'}` : `${run.problem}, depth ${run.value}`;
      row.append(element('td',title),element('td',`${formatTime(run.elapsed_seconds)}${run.status==='resource_limit' ? ' · stopped' : ''}`),element('td',`${run.expanded_nodes.toLocaleString()} nodes`));table.append(row);
    });
    area.append(table,element('p','Prior recorded measurements for these exact examples only; tracing was off. They are context, not predictions for your next input. Use Measure limits to run fresh trials on this computer.'));
  }
}
function renderBenchmark(rows,axis) {
  const wrap=element('div'), chart=element('div',undefined,'benchmark-chart');
  const max=Math.max(...rows.map(row=>row.median_observed_seconds || 0),0.000001);
  rows.forEach(row=>{
    const line=element('div',undefined,'benchmark-bar-row'), track=element('div',undefined,'benchmark-bar-track');
    const bar=element('div',undefined,`benchmark-bar${row.budget_stops ? ' limit' : ''}`);
    bar.style.width=`${100*(row.median_observed_seconds||0)/max}%`;track.append(bar);
    line.append(element('span',`${row.value} ${axis}`),track,element('span',formatTime(row.median_observed_seconds)));chart.append(line);
  });
  wrap.append(chart,element('p','Bars show median observed trial duration, including runs stopped by budgets (amber). They are measured times, not predicted completion times.','benchmark-caption'));
  const scroller=element('div',undefined,'schedule-wrap'), table=element('table',undefined,'benchmark-table'), head=element('tr');
  const tree=activeAlgorithm==='trees';
  [axis,tree?'Depth completed':'Solved',...(tree?['Goal found']:[]),'Median success','Slowest success','Limit stops','Cause','Peak queue'].forEach(x=>head.append(element('th',x)));table.append(head);
  rows.forEach(row=>{
    const tr=element('tr');
    [row.value,`${row.successful}/${row.tested}${row.tested<row.requested ? ` (${row.requested} planned)` : ''}`,...(tree?[`${row.goals_found}/${row.tested}`]:[]),formatTime(row.median_solved_seconds),formatTime(row.max_solved_seconds),row.budget_stops,Object.keys(row.stop_reasons || {}).map(reason=>reason.split(' ')[0]).join(', ') || '—',row.peak_frontier || '—'].forEach(x=>tr.append(element('td',String(x))));table.append(tr);
  });
  scroller.append(table);wrap.append(scroller);
  wrap.append(element('p',tree ? 'Depth completed means the requested depth was explored without a node/time stop. Goal found is a separate measure; a shallow completed exploration may not reach a solution.' : 'Successful-time statistics include only solved, independently validated trials. Multiple completions may exist. A stopped search is not an unsolvable puzzle.','benchmark-caption'));
  $('visual').replaceChildren(wrap);
}
