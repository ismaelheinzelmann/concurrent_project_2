def clear_errors(errors):
    for err in errors:
        err.clear()


def print_results(errors, id):
    total_errors = 0
    for thread_errors in errors:
        total_errors += len(thread_errors)
    if total_errors == 0:
        print(f"Processo {id + 1}: 0 erros encontrados.")
    else:
        print(f"Processo {id + 1}: {total_errors} erros encontrados (", end="")
        final_append = [
            f"T{i + 1}: {', '.join(e)}" for i, e in enumerate(errors) if len(e) > 0
        ]
        print("; ".join(final_append) + ")")


def verify_line(line) -> bool:
    for value in line:
        if value < 1 or value > 9:
            return False
    return len(line) == 9 and sum(line) == sum(set(line))


def verify_column(column) -> bool:
    # transpose the column into line and verify it
    return verify_line([value for (value,) in zip(*[column])])


def verify_subgrid(subgrid) -> bool:
    # flatten the subgrid into line and verify it
    return verify_line([value for row in subgrid for value in row])
