"""Generate BFS spanning trees with explicit repeated-state leaves and rejections."""

import argparse
from collections import deque
import json
from pathlib import Path
from time import perf_counter

from .problems import PROBLEMS


def build_tree(name, *, max_depth=None, max_nodes=5000, trace=None, time_limit=None):
    spec = PROBLEMS[name]
    max_depth = spec['depth'] if max_depth is None else max_depth
    if type(max_depth) is not int or max_depth < 0 or type(max_nodes) is not int or max_nodes < 1:
        raise ValueError('Depth must be nonnegative and max_nodes must be positive integers.')
    if time_limit is not None and not 0 < time_limit < float('inf'):
        raise ValueError('Time limit must be positive and finite.')
    start_time = perf_counter()
    nodes = [{'id': 0, 'parent': None, 'state': spec['start'], 'action': 'Start',
              'depth': 0, 'kind': 'new', 'rejections': []}]
    seen = {spec['start']: 0}
    queue = deque([0])
    goal_id = None
    peak = 1
    expanded = 0
    truncated = False
    while queue:
        if time_limit is not None and perf_counter() - start_time >= time_limit:
            for pending in queue:
                nodes[pending]['kind'] = 'time_limit'
            truncated = True
            break
        node = nodes[queue.popleft()]
        if trace:
            trace({'message': f"DEQUEUE #{node['id']} at depth {node['depth']}: {node['state']}",
                   'state': node['state'], 'problem': name, 'depth': node['depth'],
                   'expanded_nodes': expanded, 'peak_frontier': peak})
        if spec['goal'](node['state']):
            node['kind'] = 'goal'
            if goal_id is None:
                goal_id = node['id']
            continue
        if node['depth'] == max_depth:
            node['kind'] = 'depth_limit'
            truncated = True
            continue
        expanded += 1
        node['kind'] = 'expanded'
        for action, child, error in spec['actions'](node['state']):
            if error:
                node['rejections'].append({'action': action, 'reason': error})
                if trace:
                    trace({'message': f'REJECT {action}: {error}', 'problem': name})
                continue
            if len(nodes) >= max_nodes:
                node['kind'] = 'node_limit'
                truncated = True
                for pending in queue:
                    nodes[pending]['kind'] = 'node_limit'
                queue.clear()
                break
            repeated = child in seen
            entry = {'id': len(nodes), 'parent': node['id'], 'state': child,
                     'action': action, 'depth': node['depth'] + 1,
                     'kind': 'repeated' if repeated else 'new', 'rejections': []}
            nodes.append(entry)
            if trace:
                trace({'message': f"{'REPEAT' if repeated else 'ENQUEUE'} #{entry['id']}: {action}",
                       'problem': name, 'state': child, 'depth': entry['depth']})
            if repeated:
                entry['repeat_of'] = seen[child]
            else:
                seen[child] = entry['id']
                queue.append(entry['id'])
                peak = max(peak, len(queue))
    path = []
    current = goal_id
    while current is not None:
        path.append(current)
        current = nodes[current]['parent']
    path.reverse()
    return {'problem': name, 'description': spec['description'], 'algorithm': 'FIFO BFS',
            'max_depth': max_depth, 'max_nodes': max_nodes, 'truncated': truncated,
            'nodes': nodes, 'solution_path': path,
            'stats': {'expanded_nodes': expanded, 'unique_states': len(seen),
                      'tree_nodes': len(nodes), 'peak_frontier': peak,
                      'elapsed_seconds': perf_counter() - start_time}}


def render_markdown(trees):
    lines = ['# Generated search trees', '',
             'BFS spanning trees: repeated states are shown as leaves referring to their first node.',
             'Rejected actions appear below their parent. `*` marks the first solution path.', '']
    for tree in trees:
        lines += [f"## {tree['problem']}", '', tree['description'], '',
                  f"Truncated: **{tree['truncated']}**. Depth limit: {tree['max_depth']}. "
                  f"Expanded nodes: {tree['stats']['expanded_nodes']}. "
                  f"Peak frontier: {tree['stats']['peak_frontier']}.", '', '```text']
        children = {}
        for node in tree['nodes'][1:]:
            children.setdefault(node['parent'], []).append(node['id'])
        path = set(tree['solution_path'])

        def emit(node_id, prefix):
            node = tree['nodes'][node_id]
            repeat = f" -> #{node['repeat_of']}" if 'repeat_of' in node else ''
            lines.append(f"{prefix}{'*' if node_id in path else '-'} #{node_id} "
                         f"{node['action']}: {node['state']} [{node['kind']}{repeat}]")
            for rejected in node['rejections']:
                lines.append(f"{prefix}  x {rejected['action']}: {rejected['reason']}")
            for child_id in children.get(node_id, []):
                emit(child_id, prefix + '  ')

        emit(0, '')
        lines += ['```', '', 'Solution path: ' + (' → '.join(f'#{i}' for i in tree['solution_path'])
                                                   or 'No goal found within limits.'), '']
        if tree['problem'] == 'workforce' and tree['solution_path']:
            base = tree['nodes'][tree['solution_path'][-1]]['state']
            lines += ['| Worker | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |',
                      '| --- | --- | --- | --- | --- | --- | --- |']
            for w in range(3):
                lines.append(f"| {w + 1} | " + ' | '.join(base[(d - 2*w) % 6] for d in range(6)) + ' |')
            lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    from validate_trees import validate_path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--problem', choices=(*PROBLEMS, 'all'), default='all')
    parser.add_argument('--max-depth', type=int)
    parser.add_argument('--max-nodes', type=int, default=5000)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'results')
    args = parser.parse_args(argv)
    trees = []
    try:
        for name in (PROBLEMS if args.problem == 'all' else [args.problem]):
            tree = build_tree(name, max_depth=args.max_depth, max_nodes=args.max_nodes)
            tree['validation'] = validate_path(tree)
            if tree['solution_path'] and not tree['validation']['valid']:
                raise RuntimeError(tree['validation'])
            trees.append(tree)
            print(f"{name}: {len(tree['nodes'])} nodes; solution length "
                  f"{len(tree['solution_path']) - 1 if tree['solution_path'] else 'unknown'}; "
                  f"truncated={tree['truncated']}")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / 'search-trees.json').write_text(json.dumps(trees, indent=2) + '\n')
        (args.output_dir / 'search-trees.md').write_text(render_markdown(trees))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
