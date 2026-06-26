def format_references (candidate: dict[str, object]): 
    '''
    This function is to format the reference ids, connecting them by commas
    '''
    references = candidate.get ("reference_examples")
    return ", ".join (str(reference) for reference in references)

def format_summary (result: dict[str, object]):
    '''
    This function is to format the summary output. Title the model name and replace underscore by highphen. The formatted paragraph has nothing much to say, the code speaks for itself alrd.
    '''
    model_name = str(result.get ("predicted_class")).replace ('_', '-').title()
    candidates = result.get ("variant_candidates")
    summary = f"Among the known variants, the closest match is: {candidates[0].get ("display_name")}, with possible reference IDs: {format_references(candidates[0])}. The next Closest match: {candidates[1].get ("display_name")}, with possible reference IDs: {format_references(candidates[1])}"

    return model_name, summary