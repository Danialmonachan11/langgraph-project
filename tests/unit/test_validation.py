from agents.validation_agent import allowed_statements


# define the function to test allowed_statements defined in validation_agent.py

# case 1
def test_select_statements():
    """
    we store the output from the allowed statement function and test it against
    what we believe the function should return, so it can either be TRUE or FALSE

    Note: If any assert condition fails, it gives the error loudly 
    """
    result = allowed_statements("select revenue from stores")
    assert result == True       # True because we expect our function allowed_statements to return True here

# case 2
def test_delete_statement():
    result = allowed_statements("Drop table revenue")
    assert result == False      # False because we expect our function allowed_statements to return False here

