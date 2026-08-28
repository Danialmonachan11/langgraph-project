from security.prompt_guard import check_prompt

# validate user
def validate_input(user_query:str)->tuple[bool,str]:
    """
    checks to perform on user query:
    - is string
    - is it empty
    - length check - max and min
    - injection check
    """

    if not isinstance(user_query,str):
        return (False,"User query is not a string")

    elif not len(user_query)>0:
        return (False,"User query is empty")

    elif not len(user_query.split())<200:
        return (False,"User query is too long")

    elif not len(user_query.split())>1:
        return (False,"User query is too short")

    is_safe, reasons = check_prompt(user_query)
    if not is_safe:
        return (False,"User query is not safe and trying to inject prompt")

    else:
        return (True, user_query.strip())




    