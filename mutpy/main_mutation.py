import ast
import os

from mutpy import operators, utils


def generate_mutants_from_file(
    file_path=None,
    mutant_count=1,
    include_experimental=False,
    code_string=None,
):
    """Generate mutants from a single Python source file.

    Args:
        file_path (str): Path to Python source file.
        mutant_count (int): Maximum number of mutants to return.
        include_experimental (bool): Include experimental operators.
        code_string (str): Python source code string.

    Returns:
        list[dict]: A list of mutants. Each item contains:
            - number: 1-based mutation index
            - mutations: list of {"operator", "lineno"}
            - source: mutated source code
    """
    if not isinstance(mutant_count, int) or mutant_count < 1:
        raise ValueError('mutant_count should be a positive integer.')

    if file_path and code_string is not None:
        raise ValueError('Provide either file_path or code_string, not both.')

    if not file_path and code_string is None:
        raise ValueError('Provide file_path or code_string.')

    if code_string is not None:
        if not isinstance(code_string, str):
            raise ValueError('code_string should be a string.')
        source_code = code_string
    else:
        if not os.path.isfile(file_path):
            raise ValueError('file_path should point to an existing file.')
        if not file_path.endswith('.py'):
            raise ValueError('file_path should point to a .py file.')
        with open(file_path) as source_file:
            source_code = source_file.read()

    target_ast = utils.create_ast(source_code)
    sampler = utils.RandomSampler(percentage=100)
    selected_operators = _build_operators(include_experimental=include_experimental)

    mutants = []
    for op in utils.sort_operators(selected_operators):
        for mutation, mutant_ast in op().mutate(target_ast, sampler=sampler):
            mutations = [mutation]
            mutants.append({
                'number': len(mutants) + 1,
                'mutations': _serialize_mutations(mutations),
                'source': _to_source(mutant_ast),
            })
            if len(mutants) >= mutant_count:
                return mutants

    return mutants


def _to_source(node):
    try:
        from mutpy import codegen
        return codegen.to_source(node)
    except ImportError:
        if hasattr(ast, 'unparse'):
            return ast.unparse(node)
        raise RuntimeError('Cannot convert AST to source code: install astmonkey.')


def _build_operators(include_experimental=False):
    selected = set(operators.standard_operators)
    if include_experimental:
        selected |= operators.experimental_operators
    return selected


def _serialize_mutations(mutations):
    result = []
    for mutation in mutations:
        result.append({
            'operator': mutation.operator.name(),
            'lineno': _get_mutation_lineno(mutation),
        })
    return result


def _get_mutation_lineno(mutation):
    if hasattr(mutation.node, 'lineno'):
        return mutation.node.lineno
    if getattr(mutation.node, 'parent', None) is not None and hasattr(mutation.node.parent, 'lineno'):
        return mutation.node.parent.lineno
    return None
