#from tokenizeBranchingLogic import tokenizeBranchingLogic

#test = "[actcohortsp] = '1' and [eeg] = '1' and [eegres_v2] != '1' and [epidischarge] = '1'"
#test = "[strage]='0' and ([neoais(1)]='0' and [neocsvt(1)]='0' ) and [preart(1)]='0'"
#test = "[vscreen]<>'2'AND [vscreen]<='3' and[monkey(2)] >= 3 oR [sand][var(2)][rep5] != '2' or ([var51] = '2' and [var32] = 4)"

#test_tokens = tokenizeBranchingLogic(test)

def translateTokens(tokens):
    """After fully tokenizing the branching logic, this method is used to convert the REDCap-readable tokens
    into Python-readable tokens. E.g. REDCap uses '=' to check for equality, while Python uses '=='."""
    for ii in range(len(tokens)):
        token = tokens[ii]
#        print "start token:", token
        if token == "=":
            tokens[ii] = "=="
        elif token == "<>": # WHAT DOES '<>' DO IN REDCAP? I DON'T FULLY UNDERSTAND, BUT THIS SEEMS RIGHT.
            tokens[ii] = "!="
        elif token.lower() == "and":
            tokens[ii] = " and "
        elif token.lower() == "or":
            tokens[ii] = " or "
#        print "end token:", token
    return tokens

#print translateTokens(test_tokens)
