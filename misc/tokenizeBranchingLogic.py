import re
from copy import deepcopy
from more_itertools import locate

def tokenizeBranchingLogic(string):
   raw_tokens = re.findall("\s*(\d+|\w+|.)", string)

   # Remove whitespace tokens:
   white_token_indices = []
   for token_index in range(len(raw_tokens)):
      if (raw_tokens[token_index].strip() == ""):
         white_token_indices.append(token_index)
   pl = []
   for token_index in range(len(raw_tokens)):
      if token_index in white_token_indices:
         continue
      else:
         pl.append(raw_tokens[token_index])

   # Combine raw tokens which should be considered a single token (e.g. '<','=' should be '<=').
   combine_indices = []
   for ii in range(len(pl)):
      if len(combine_indices)>0:
         if ii in combine_indices[-1]:
            continue
      token = pl[ii]
      if not (ii == len(pl)-1):
         next_token = pl[ii+1]
      else:
         next_token = None

      # Reconnect [event1][variable3(checkbox4)][repetition2]
      if token == "[":
         combine_indices.append([ii])
         for jj in range(ii+1, len(pl)):
#            if (pl[jj] != "]") or (pl[jj+1] == "["): # Breaks for [var1] = [var2]
#               combine_indices[-1].append(jj)
            
            # REDO OF ABOVE SECTION
            if (pl[jj] != "]"):
               combine_indices[-1].append(jj)
            elif (jj+1 < len(pl)):
               if (pl[jj+1] == "["):
                  combine_indices[-1].append(jj)
               else:
                  combine_indices[-1].append(jj)
                  break

            else:
               combine_indices[-1].append(jj)
               break
      # Reconnect '3'
      elif token == "'":
         combine_indices.append([ii])
         for jj in range(ii+1, len(pl)):
            if (pl[jj] != "'"):
               combine_indices[-1].append(jj)
            else:
               combine_indices[-1].append(jj)
               break
      # Reconnect <> and <=
      elif (token == "<") and ((next_token == "=") or (next_token == ">")):
         combine_indices.append([ii, ii+1])
      # Reconnect >=
      elif (token == ">") and (next_token == "="):
         combine_indices.append([ii, ii+1])
      # Reconnect !=
      elif (token == "!") and (next_token == "="):
         combine_indices.append([ii, ii+1])
      
   # Create list which specifies which tokens should be combined into a single token.
   ppl = []
   ci_index = 0
   if (0 in combine_indices[ci_index]):
      ppl.append(combine_indices[ci_index])
      ci_index += 1
   else:
      ppl.append([0])   
   for ii in range(1, len(pl)):
      if (ii in ppl[-1]): # if index was already added
         continue
      elif (ci_index < len(combine_indices)): # if last combination has not been reached
         if ii in combine_indices[ci_index]: # if index is in a combination
            ppl.append(combine_indices[ci_index])
            ci_index += 1
         else: # if index in not in combination
            ppl.append([ii])
      else:
         ppl.append([ii])

   pppl = list(range(len(ppl)) )
   for ii in range(len(ppl)):
      pppl[ii] = ""
      for jj in ppl[ii]:
         pppl[ii] += pl[jj]
   return pppl


